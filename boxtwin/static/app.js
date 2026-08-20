const $ = id => document.getElementById(id);
const state = { latest: null, health: null, activeScenario: null, activeAlerts: [] };
const alertStorageKey = 'boxtwin_intervention_seen_simulator';
const typeLabels = {capacity:'Capacidade', confidence:'Baixa confiança', obstruction:'Obstrução'};
const statusLabels = {open:'Aberta', acknowledged:'Ciente', in_progress:'Em atendimento', resolved:'Resolvida', false_positive:'Falso positivo'};
let lastSoundAlertId = null;
let reminderIntervalId = null;
let lastReminderAlertId = null;

<<<<<<< HEAD
=======
const viewState = {
  rotationY: Math.PI / 4,
  rotationX: 0.48,
  zoom: 1,
};

>>>>>>> 62ebd29 (feat: alertas, relatórios, sync edge-railway e preparo raspberry)
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

function acknowledgedAlerts() {
  try {
    return JSON.parse(localStorage.getItem(alertStorageKey) || '[]');
  } catch {
    return [];
  }
}

function markAlertSeen(id) {
  const ids = new Set(acknowledgedAlerts());
  ids.add(id);
  localStorage.setItem(alertStorageKey, JSON.stringify([...ids]));
}

function playAlertSound() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return;
  const audioContext = new AudioContextClass();
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.type = 'triangle';
  oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
  oscillator.frequency.exponentialRampToValueAtTime(622, audioContext.currentTime + 0.22);
  gain.gain.setValueAtTime(0.0001, audioContext.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.08, audioContext.currentTime + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.28);
  oscillator.connect(gain);
  gain.connect(audioContext.destination);
  oscillator.start();
  oscillator.stop(audioContext.currentTime + 0.3);
}

function stopReminderLoop() {
  if (reminderIntervalId) {
    window.clearInterval(reminderIntervalId);
    reminderIntervalId = null;
  }
  lastReminderAlertId = null;
}

function startReminderLoop(item) {
  if (!item || !['open', 'acknowledged'].includes(item.status)) {
    stopReminderLoop();
    return;
  }
  if (reminderIntervalId && lastReminderAlertId === item.id) return;
  stopReminderLoop();
  lastReminderAlertId = item.id;
  reminderIntervalId = window.setInterval(() => {
    showToast(
      `${typeLabels[item.anomaly_type] || item.anomaly_type}: alerta ainda ativo e aguardando tratativa.`,
      'error',
      5000,
    );
  }, 30000);
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
<<<<<<< HEAD
  const scaleX = Math.min(width / 19, 31), scaleY = scaleX * .48, scaleZ = height * 1.22;
  const project = (row, col, z = 0) => ({
    x: centerX + (col - row) * scaleX,
    y: originY + (col + row - 7) * scaleY - z * scaleZ
  });
=======
  const scaleX = Math.min(width / 19, 31) * viewState.zoom;
  const scaleY = scaleX * viewState.rotationX;
  const boxHeight = Math.max(state.health?.dimensions_m?.height || .5, maxValue, .001);
  const scaleZ = (Math.min(height * .5, originY - 18) / boxHeight) * viewState.zoom;

  const cosYaw = Math.cos(viewState.rotationY) * Math.SQRT2;
  const sinYaw = Math.sin(viewState.rotationY) * Math.SQRT2;
  const project = (row, col, z = 0) => {
    const u = col - 3.5;
    const v = row - 3.5;
    return {
      x: centerX + (u * cosYaw - v * sinYaw) * scaleX,
      y: originY + (u * sinYaw + v * cosYaw) * scaleY - z * scaleZ,
    };
  };
>>>>>>> 62ebd29 (feat: alertas, relatórios, sync edge-railway e preparo raspberry)

  ctx.strokeStyle = '#78b8df55';
  ctx.lineWidth = 1;
  const base = [project(0,0), project(0,7), project(7,7), project(7,0)];
  ctx.beginPath();
  base.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y));
  ctx.closePath();
  ctx.fillStyle = '#0a2238';
  ctx.fill();
  ctx.stroke();

  for (let sum = 0; sum <= 12; sum++) {
    for (let row = 0; row < 7; row++) {
      const col = sum - row;
      if (col < 0 || col >= 7) continue;
      const corners = [
        [row,col,grid[row][col]], [row,col+1,grid[row][col+1]],
        [row+1,col+1,grid[row+1][col+1]], [row+1,col,grid[row+1][col]]
      ].map(([r,c,z]) => project(r,c,z));
      const avg = (grid[row][col] + grid[row][col+1] + grid[row+1][col+1] + grid[row+1][col]) / 4;
      ctx.beginPath();
      corners.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y));
      ctx.closePath();
      ctx.fillStyle = colorFor(avg, maxValue);
      ctx.globalAlpha = .88;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.strokeStyle = '#d8f5ff55';
      ctx.stroke();
    }
  }

  ctx.strokeStyle = '#9bdcffaa';
  ctx.lineWidth = 1.2;
  [[0,0],[0,7],[7,7],[7,0]].forEach(([r,c]) => {
    const bottom = project(r,c,0);
    const top = project(r,c,state.health?.dimensions_m?.height || .5);
    ctx.beginPath();
    ctx.moveTo(bottom.x,bottom.y);
    ctx.lineTo(top.x,top.y);
    ctx.stroke();
  });
  ctx.fillStyle = '#b8d4e8';
  ctx.font = '11px Segoe UI';
  ctx.fillText('Superfície estimada da carga', 15, 22);
}

function drawHistory(items) {
  const canvas = $('historyCanvas');
  const { context: ctx, width, height } = sizeCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  const pad = { left: 38, right: 14, top: 15, bottom: 24 };
  const w = width - pad.left - pad.right;
  const h = height - pad.top - pad.bottom;
  ctx.font = '10px Segoe UI';
  ctx.fillStyle = '#708196';
  ctx.strokeStyle = '#dce5ef';
  ctx.lineWidth = 1;
  [0,25,50,75,100].forEach(value => {
    const y = pad.top + h * (1 - value / 100);
    ctx.beginPath();
    ctx.moveTo(pad.left,y);
    ctx.lineTo(width-pad.right,y);
    ctx.stroke();
    ctx.fillText(`${value}%`, 5, y + 3);
  });
  if (!items.length) return;
  const points = items.map((item,index) => ({
    x: pad.left + (items.length === 1 ? w / 2 : index * w / (items.length - 1)),
    y: pad.top + h * (1 - Math.min(100,item.capacity_percent) / 100),
  }));
  const gradient = ctx.createLinearGradient(0,pad.top,0,pad.top+h);
  gradient.addColorStop(0,'rgba(23,105,255,.30)');
  gradient.addColorStop(1,'rgba(23,105,255,0)');
  ctx.beginPath();
  points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.lineTo(points.at(-1).x,pad.top+h);
  ctx.lineTo(points[0].x,pad.top+h);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();
  ctx.beginPath();
  points.forEach((p,i) => i ? ctx.lineTo(p.x,p.y) : ctx.moveTo(p.x,p.y));
  ctx.strokeStyle='#1769ff';
  ctx.lineWidth=2.5;
  ctx.stroke();
  points.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x,p.y,3,0,Math.PI*2);
    ctx.fillStyle='#fff';
    ctx.fill();
    ctx.strokeStyle='#1769ff';
    ctx.stroke();
  });
}

function setActiveScenario(id) {
  state.activeScenario = id;
  document.querySelectorAll('.scenario').forEach(button => button.classList.toggle('active', button.dataset.id === id));
}

function renderAlertSignal() {
  const banner = $('simAlertBanner');
  const first = state.activeAlerts[0];
  if (!first) {
    banner.hidden = true;
    banner.className = 'panel alert-signal';
    lastSoundAlertId = null;
    stopReminderLoop();
    return;
  }
  banner.hidden = false;
  banner.className = `panel alert-signal ${first.status === 'open' ? 'active' : ''} ${first.severity === 'danger' ? 'danger' : 'warning'}`;
  $('simAlertTitle').textContent = `${typeLabels[first.anomaly_type] || first.anomaly_type} requer tratativa`;
  $('simAlertMeta').textContent = `${state.activeAlerts.length} alerta(s) ativo(s) · ${first.email_sent ? 'cliente notificado' : 'aguardando notificação'} · ${statusLabels[first.status] || first.status}`;
  $('simAlertText').textContent = `${first.message} Status: ${statusLabels[first.status] || first.status}.`;
  if (first.status === 'open' && first.id !== lastSoundAlertId) {
    playAlertSound();
    lastSoundAlertId = first.id;
  }
  startReminderLoop(first);
  const seen = new Set(acknowledgedAlerts());
  const pendingHuman = state.activeAlerts.find(item => item.status === 'open' && !seen.has(item.id));
  if (pendingHuman) openInterventionModal(pendingHuman);
}

function openInterventionModal(item) {
  $('interventionTitle').textContent = `${typeLabels[item.anomaly_type] || item.anomaly_type} exige atenção`;
  $('interventionText').textContent = `${item.message} Vou carregar a orientação de tratativa para apoiar sua decisão.`;
  $('interventionDetails').innerHTML = `<div><b>Tratativa recomendada</b><small>Consultando procedimento operacional…</small></div>`;
  $('interventionModal').hidden = false;
  request('/api/admin/assistant', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({question:`Quero a tratativa operacional para ${item.anomaly_type}. Explique de forma humana e direta o que verificar e como tratar esta ocorrência: ${item.message}.`})
  }).then(result => {
    $('interventionDetails').innerHTML = `
      <div><b>Tratativa recomendada</b><small>${result.answer}</small></div>
      <div><b>Comunicação com o cliente</b><small>${item.email_sent ? 'E-mail de alerta enviado ao cliente.' : 'Envio de e-mail ainda não confirmado.'}</small></div>
      <div><b>Horário do alerta</b><small>${new Date(item.created_at).toLocaleString('pt-BR')}</small></div>
    `;
  }).catch(error => {
    $('interventionDetails').innerHTML = `
      <div><b>Tratativa recomendada</b><small>Não consegui carregar a orientação automática agora. Registre a ocorrência e valide com um responsável técnico.</small></div>
      <div><b>Detalhe</b><small>${error.message}</small></div>
    `;
  });
  $('interventionConfirm').onclick = async () => {
    $('interventionConfirm').disabled = true;
    try {
      await request(`/api/admin/anomalies/${item.id}/acknowledge`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({note:'Leitura da tratativa confirmada no simulador.'})});
      markAlertSeen(item.id);
      $('interventionModal').hidden = true;
      showToast('Ciência da anomalia registrada. O aviso seguirá fixo até a resolução.', 'success');
      await loadActiveAlerts();
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      $('interventionConfirm').disabled = false;
    }
  };
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
  renderGrid(data);
  drawTwin(data.height_grid_m);
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

<<<<<<< HEAD
async function chooseScenario(id, button) {
  const buttons = document.querySelectorAll('.scenario'); buttons.forEach(item => item.disabled = true);
  try { render(await request(`/api/demo/scenario/${id}`, {method:'POST'})); await loadHistory(); }
  catch (error) { alert(error.message); }
  finally { buttons.forEach(item => item.disabled = false); }
=======
async function loadActiveAlerts() {
  const payload = await request('/api/alerts/active?limit=10');
  state.activeAlerts = payload.items || [];
  renderAlertSignal();
}

async function chooseScenario(id) {
  const buttons = document.querySelectorAll('.scenario');
  buttons.forEach(item => item.disabled = true);
  try {
    render(await request(`/api/demo/scenario/${id}`, {method:'POST'}));
    await Promise.all([loadHistory(), loadActiveAlerts()]);
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    buttons.forEach(item => item.disabled = false);
  }
>>>>>>> 62ebd29 (feat: alertas, relatórios, sync edge-railway e preparo raspberry)
}

async function loadScenarios() {
  if (!state.health.demo_enabled) {
    $('demoPanel').hidden = true;
    return;
  }
  const data = await request('/api/demo/scenarios');
  $('scenarios').innerHTML = '';
  data.scenarios.forEach(item => {
    const button = document.createElement('button');
    button.className = 'scenario';
    button.dataset.id = item.id;
    button.textContent = item.label;
    button.title = item.description;
    button.onclick = () => chooseScenario(item.id);
    $('scenarios').appendChild(button);
  });
  setActiveScenario(data.active);
}

async function initialize() {
  try {
    state.health = await request('/api/health');
    $('connection').textContent='● BoxNode online';
    $('connection').classList.add('online');
    const d=state.health.dimensions_m;
    $('boxCapacity').textContent=`${fmt(state.health.capacity_m3,3)} m³`;
    $('boxDimensions').textContent=`${d.length} m × ${d.width} m × ${d.height} m`;
    if (!state.health.demo_enabled) {
      $('modeBadge').textContent='SENSOR FÍSICO';
      $('modeBadge').classList.remove('demo');
    }
    await loadScenarios();
    const latest = await request('/api/readings/latest');
    if (latest.status === 'no_data' && state.health.demo_enabled) {
      const setup = await request('/api/demo/setup',{method:'POST'});
      render(setup.reading);
    } else {
      render(latest);
    }
    await Promise.all([loadHistory(), loadActiveAlerts()]);
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/service-worker.js').catch(()=>{});
    const stream = new EventSource('/api/stream');
    stream.addEventListener('reading', event => {
      const reading=JSON.parse(event.data);
      if(reading.id!==state.latest?.id){
        render(reading);
        loadHistory().catch(()=>{});
        loadActiveAlerts().catch(()=>{});
      }
    });
    stream.onerror = () => { $('connection').textContent='● Reconectando…'; };
    stream.onopen = () => { $('connection').textContent='● BoxNode online'; };
  } catch (error) {
    $('connection').textContent='● Sem conexão';
    $('connection').classList.remove('online');
    $('alerts').innerHTML=`<div class="alert danger">${error.message}</div>`;
  }
}

<<<<<<< HEAD
$('setup').onclick = async () => { const data=await request('/api/demo/setup',{method:'POST'});render(data.reading);await loadHistory(); };
$('capture').onclick = async () => { try{render(await request('/api/readings',{method:'POST'}));await loadHistory();}catch(error){alert(error.message);} };
$('calibrate').onclick = async () => {
  if (!confirm('A calibração definirá o box como vazio. Deseja continuar?')) return;
  try {
    if (state.health.demo_enabled) render(await request('/api/demo/scenario/empty',{method:'POST'}));
    else { await request('/api/calibration',{method:'POST'}); alert('Calibração salva.'); }
    await loadHistory();
  } catch(error){alert(error.message);}
};
window.addEventListener('resize',()=>{if(state.latest)drawTwin(state.latest.height_grid_m);loadHistory().catch(()=>{});});
=======
$('setup').onclick = async () => {
  const data=await request('/api/demo/setup',{method:'POST'});
  render(data.reading);
  await Promise.all([loadHistory(), loadActiveAlerts()]);
};

$('capture').onclick = async () => {
  try {
    render(await request('/api/readings',{method:'POST'}));
    await Promise.all([loadHistory(), loadActiveAlerts()]);
  } catch (error) {
    showToast(error.message,'error');
  }
};

async function performCalibration() {
  try {
    if (state.health.demo_enabled) render(await request('/api/demo/scenario/empty',{method:'POST'}));
    else {
      await request('/api/calibration',{method:'POST'});
      showToast('Calibração salva.','success');
    }
    await Promise.all([loadHistory(), loadActiveAlerts()]);
  } catch (error) {
    showToast(error.message,'error');
  }
}

$('calibrate').onclick = () => {
  showConfirmToast('A calibração definirá o box como vazio. Deseja continuar?', performCalibration, {confirmLabel:'Calibrar', cancelLabel:'Cancelar'});
};

window.addEventListener('resize', () => {
  if (state.latest) drawTwin(state.latest.height_grid_m);
  loadHistory().catch(()=>{});
});

>>>>>>> 62ebd29 (feat: alertas, relatórios, sync edge-railway e preparo raspberry)
initialize();
