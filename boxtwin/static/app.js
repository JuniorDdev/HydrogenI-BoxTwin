const $ = id => document.getElementById(id);
const state = { latest: null, health: null, activeScenario: null };

// Estado centralizado da câmera do gêmeo digital 3D. Hoje só os valores padrão são usados (a vista
// isométrica fixa de sempre) — mas por estarem aqui, uma extensão futura de arrastar-para-girar ou
// scroll-para-zoom só precisa alterar estes números e chamar drawTwin() de novo para redesenhar,
// sem tocar na lógica de projeção em si.
const viewState = {
  rotationY: Math.PI / 4, // giro em torno do eixo vertical (azimute), em radianos.
                          // Extensão futura: pointerdown/pointermove horizontal ajustaria este valor.
  rotationX: 0.48,        // inclinação vertical da vista, como razão escalaY/escalaX (0 = vista de
                          // topo, 1 = vista mais lateral) — é uma projeção axonométrica simplificada,
                          // não uma câmera 3D completa.
                          // Extensão futura: pointerdown/pointermove vertical ajustaria este valor.
  zoom: 1,                // fator de escala geral aplicado a X, Y e Z.
                          // Extensão futura: evento wheel ou gesto de pinça (touch) ajustaria este valor.
};

function fmt(value, digits = 1) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : '—';
}

function colorFor(value, max) {
  const ratio = Math.max(0, Math.min(1, value / Math.max(max, .001)));
  const stops = [[18,58,112],[20,151,218],[24,213,255],[255,181,71]];
  const scaled = ratio * (stops.length - 1);
  const index = Math.min(stops.length - 2, Math.floor(scaled));
  const part = scaled - index;
  const rgb = stops[index].map((v, i) => Math.round(v + (stops[index + 1][i] - v) * part));
  return `rgb(${rgb.join(',')})`;
}

function renderGrid(data) {
  const grid = $('grid');
  grid.innerHTML = '';
  const values = data.height_grid_m.flat();
  const max = Math.max(...values, .001);
  values.forEach(value => {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.style.background = colorFor(value, max);
    cell.textContent = (value * 100).toFixed(1);
    cell.title = `Altura: ${(value * 100).toFixed(2)} cm`;
    grid.appendChild(cell);
  });
}

function sizeCanvas(canvas) {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(1, Math.round(rect.width * ratio));
  canvas.height = Math.max(1, Math.round(rect.height * ratio));
  const context = canvas.getContext('2d');
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  return { context, width: rect.width, height: rect.height };
}

function drawTwin(grid) {
  const canvas = $('twinCanvas');
  const { context: ctx, width, height } = sizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const maxValue = Math.max(...grid.flat(), .001);
  const centerX = width * .50, originY = height * .76;
  const scaleX = Math.min(width / 19, 31) * viewState.zoom;
  const scaleY = scaleX * viewState.rotationX;
  const boxHeight = Math.max(state.health?.dimensions_m?.height || .5, maxValue, .001);
  const scaleZ = (Math.min(height * .5, originY - 18) / boxHeight) * viewState.zoom;

  // Projeção axonométrica: gira (row,col) em torno do centro da matriz 8x8 pelo ângulo de
  // viewState.rotationY antes de aplicar a inclinação/escala. Com os valores padrão acima
  // (rotationY = 45°), o resultado é matematicamente idêntico à projeção isométrica fixa original.
  const cosYaw = Math.cos(viewState.rotationY) * Math.SQRT2;
  const sinYaw = Math.sin(viewState.rotationY) * Math.SQRT2;
  const project = (row, col, z = 0) => {
    const u = col - 3.5, v = row - 3.5;
    return {
      x: centerX + (u * cosYaw - v * sinYaw) * scaleX,
      y: originY + (u * sinYaw + v * cosYaw) * scaleY - z * scaleZ
    };
  };

  ctx.strokeStyle = '#78b8df55'; ctx.lineWidth = 1;
  const base = [project(0,0), project(0,7), project(7,7), project(7,0)];
  ctx.beginPath(); base.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y)); ctx.closePath();
  ctx.fillStyle = '#0a2238'; ctx.fill(); ctx.stroke();

  for (let sum = 0; sum <= 12; sum++) {
    for (let row = 0; row < 7; row++) {
      const col = sum - row;
      if (col < 0 || col >= 7) continue;
      const corners = [
        [row,col,grid[row][col]], [row,col+1,grid[row][col+1]],
        [row+1,col+1,grid[row+1][col+1]], [row+1,col,grid[row+1][col]]
      ].map(([r,c,z]) => project(r,c,z));
      const avg = (grid[row][col] + grid[row][col+1] + grid[row+1][col+1] + grid[row+1][col]) / 4;
      ctx.beginPath(); corners.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y)); ctx.closePath();
      ctx.fillStyle = colorFor(avg, maxValue); ctx.globalAlpha = .88; ctx.fill();
      ctx.globalAlpha = 1; ctx.strokeStyle = '#d8f5ff55'; ctx.stroke();
    }
  }

  ctx.strokeStyle = '#9bdcffaa'; ctx.lineWidth = 1.2;
  [[0,0],[0,7],[7,7],[7,0]].forEach(([r,c]) => {
    const bottom = project(r,c,0), top = project(r,c,state.health?.dimensions_m?.height || .5);
    ctx.beginPath(); ctx.moveTo(bottom.x,bottom.y); ctx.lineTo(top.x,top.y); ctx.stroke();
  });
  ctx.fillStyle = '#b8d4e8'; ctx.font = '11px Segoe UI';
  ctx.fillText('Superfície estimada da carga', 15, 22);
}

function drawHistory(items) {
  const canvas = $('historyCanvas');
  const { context: ctx, width, height } = sizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const pad = { left: 38, right: 14, top: 15, bottom: 24 };
  const w = width - pad.left - pad.right, h = height - pad.top - pad.bottom;
  ctx.font = '10px Segoe UI'; ctx.fillStyle = '#708196'; ctx.strokeStyle = '#dce5ef'; ctx.lineWidth = 1;
  [0,25,50,75,100].forEach(value => {
    const y = pad.top + h * (1 - value / 100);
    ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(width-pad.right,y); ctx.stroke();
    ctx.fillText(`${value}%`, 5, y + 3);
  });
  if (!items.length) return;
  const points = items.map((item,index) => ({
    x: pad.left + (items.length === 1 ? w / 2 : index * w / (items.length - 1)),
    y: pad.top + h * (1 - Math.min(100,item.capacity_percent) / 100)
  }));
  const gradient = ctx.createLinearGradient(0,pad.top,0,pad.top+h);
  gradient.addColorStop(0,'rgba(23,105,255,.30)'); gradient.addColorStop(1,'rgba(23,105,255,0)');
  ctx.beginPath(); points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.lineTo(points.at(-1).x,pad.top+h); ctx.lineTo(points[0].x,pad.top+h); ctx.closePath(); ctx.fillStyle=gradient; ctx.fill();
  ctx.beginPath(); points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.strokeStyle='#1769ff'; ctx.lineWidth=2.5; ctx.stroke();
  points.forEach(p => {ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fillStyle='#fff';ctx.fill();ctx.strokeStyle='#1769ff';ctx.stroke();});
}

function setActiveScenario(id) {
  state.activeScenario = id;
  document.querySelectorAll('.scenario').forEach(button => button.classList.toggle('active', button.dataset.id === id));
}

function render(data) {
  if (!data || !data.id) return;
  state.latest = data;
  $('volume').textContent = fmt(data.volume_m3, 4);
  $('capacity').textContent = fmt(data.capacity_percent, 1);
  $('capacityBar').style.width = `${Math.min(100, data.capacity_percent)}%`;
  $('avgHeight').textContent = fmt((data.average_height_m || 0) * 100, 1);
  $('maxHeight').textContent = `Pico: ${fmt((data.maximum_height_m || 0) * 100, 1)} cm`;
  $('confidence').textContent = fmt(data.confidence_percent, 1);
  $('zones').textContent = data.valid_zones;
  $('referenceError').textContent = fmt(data.reference_error_points, 2);
  $('referenceValue').textContent = data.reference_percent == null ? 'Referência indisponível no sensor real' : `Referência: ${fmt(data.reference_percent,1)}%`;
  $('updated').textContent = `Atualizado ${new Date(data.created_at).toLocaleString('pt-BR')}`;
  setActiveScenario(data.scenario);
  renderGrid(data); drawTwin(data.height_grid_m);
  $('alerts').innerHTML = data.alerts.length
    ? data.alerts.map(alert => `<div class="alert ${alert.level}">${alert.message}</div>`).join('')
    : '<div class="alert ok">Operação normal. Nenhum alerta ativo.</div>';
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || data.message || 'Falha na operação.');
  return data;
}

async function loadHistory() {
  const items = await request('/api/readings/history?limit=20');
  drawHistory(items);
}

async function chooseScenario(id, button) {
  const buttons = document.querySelectorAll('.scenario'); buttons.forEach(item => item.disabled = true);
  try { render(await request(`/api/demo/scenario/${id}`, {method:'POST'})); await loadHistory(); }
  catch (error) { showToast(error.message, 'error'); }
  finally { buttons.forEach(item => item.disabled = false); }
}

async function loadScenarios() {
  if (!state.health.demo_enabled) { $('demoPanel').hidden = true; return; }
  const data = await request('/api/demo/scenarios');
  $('scenarios').innerHTML = '';
  data.scenarios.forEach(item => {
    const button = document.createElement('button'); button.className='scenario'; button.dataset.id=item.id;
    button.textContent=item.label; button.title=item.description; button.onclick=()=>chooseScenario(item.id,button);
    $('scenarios').appendChild(button);
  });
  setActiveScenario(data.active);
}

async function initialize() {
  try {
    state.health = await request('/api/health');
    $('connection').textContent='● BoxNode online'; $('connection').classList.add('online');
    const d=state.health.dimensions_m;
    $('boxCapacity').textContent=`${fmt(state.health.capacity_m3,3)} m³`;
    $('boxDimensions').textContent=`${d.length} m × ${d.width} m × ${d.height} m`;
    if (!state.health.demo_enabled) { $('modeBadge').textContent='SENSOR FÍSICO'; $('modeBadge').classList.remove('demo'); }
    await loadScenarios();
    const latest = await request('/api/readings/latest');
    if (latest.status === 'no_data' && state.health.demo_enabled) {
      const setup = await request('/api/demo/setup',{method:'POST'}); render(setup.reading);
    } else render(latest);
    await loadHistory();
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/service-worker.js').catch(()=>{});
    const stream = new EventSource('/api/stream');
    stream.addEventListener('reading', event => { const reading=JSON.parse(event.data); if(reading.id!==state.latest?.id){render(reading);loadHistory().catch(()=>{});} });
    stream.onerror=()=>{$('connection').textContent='● Reconectando…';};
    stream.onopen=()=>{$('connection').textContent='● BoxNode online';};
  } catch (error) {
    $('connection').textContent='● Sem conexão'; $('connection').classList.remove('online');
    $('alerts').innerHTML=`<div class="alert danger">${error.message}</div>`;
  }
}

$('setup').onclick = async () => { const data=await request('/api/demo/setup',{method:'POST'});render(data.reading);await loadHistory(); };
$('capture').onclick = async () => { try{render(await request('/api/readings',{method:'POST'}));await loadHistory();}catch(error){showToast(error.message,'error');} };

async function performCalibration() {
  try {
    if (state.health.demo_enabled) render(await request('/api/demo/scenario/empty',{method:'POST'}));
    else { await request('/api/calibration',{method:'POST'}); showToast('Calibração salva.','success'); }
    await loadHistory();
  } catch (error) { showToast(error.message,'error'); }
}
$('calibrate').onclick = () => {
  showConfirmToast('A calibração definirá o box como vazio. Deseja continuar?', performCalibration, {confirmLabel:'Calibrar', cancelLabel:'Cancelar'});
};
window.addEventListener('resize',()=>{if(state.latest)drawTwin(state.latest.height_grid_m);loadHistory().catch(()=>{});});

// Extensão futura (não implementada): handlers de pointerdown/pointermove/pointerup no #twinCanvas
// (mouse e touch) leriam o deslocamento do arraste, ajustariam viewState.rotationY (arraste
// horizontal) e viewState.rotationX (arraste vertical), e chamariam
// drawTwin(state.latest.height_grid_m) para redesenhar — igual ao listener de resize acima já faz.
// Um listener de 'wheel' (e gestos de pinça em touch) ajustaria viewState.zoom do mesmo jeito.
// Nenhum desses handlers existe ainda; drawTwin() e viewState já estão prontos para recebê-los.

initialize();
