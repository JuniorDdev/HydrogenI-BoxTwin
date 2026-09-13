const $ = id => document.getElementById(id);
const state = { latest: null, health: null, activeScenario: null, activeAlerts: [], rawTimer: null };
const alertStorageKey = 'boxtwin_intervention_seen_simulator';
const typeLabels = {capacity:'Capacidade', confidence:'Baixa confiança', obstruction:'Obstrução'};
const statusLabels = {open:'Aberta', acknowledged:'Ciente', in_progress:'Em atendimento', resolved:'Resolvida', false_positive:'Falso positivo'};
const treatmentGuides = {
  capacity: ['Confirmar ocupação no mapa 8 x 8.', 'Evitar nova carga neste box.', 'Acionar operação para retirada ou redistribuição.'],
  confidence: ['Verificar poeira, vibração e iluminação.', 'Conferir sensor e área de leitura.', 'Repetir captura após inspeção.'],
  obstruction: ['Pausar a medição automática.', 'Inspecionar janela/campo do sensor.', 'Limpar obstruções e capturar novamente.'],
};
let lastSoundAlertId = null;
let reminderIntervalId = null;
let lastReminderAlertId = null;
const reminderDelayMs = 45000;

const viewState = {
  rotationY: Math.PI / 4,
  rotationX: 0.48,
  zoom: 1,
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
  }, reminderDelayMs);
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

function renderRawGrid(data) {
  const grid = $('grid');
  grid.innerHTML = '';
  const values = data.distance_grid_mm.flat().filter(Number.isFinite);
  const max = Math.max(...values, 1);
  data.distance_grid_mm.flat().forEach(value => {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.style.background = Number.isFinite(value) ? colorFor(value, max) : '#27384a';
    cell.textContent = Number.isFinite(value) ? `${value}` : '—';
    cell.title = Number.isFinite(value) ? `Distância: ${value} mm` : 'Leitura inválida';
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
  const seen = new Set(acknowledgedAlerts());
  const first = state.activeAlerts.find(item => !seen.has(item.id));
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
  const pendingHuman = state.activeAlerts.find(item => item.status === 'open' && !seen.has(item.id));
  if (pendingHuman) openInterventionModal(pendingHuman);
}

function openInterventionModal(item) {
  $('interventionTitle').textContent = `${typeLabels[item.anomaly_type] || item.anomaly_type} exige atenção`;
  $('interventionText').textContent = item.message;
  const guide = treatmentGuides[item.anomaly_type] || ['Verificar a ocorrência no painel.', 'Registrar evidências.', 'Acionar responsável técnico.'];
  $('interventionDetails').innerHTML = `
    <div><b>Tratativa rápida</b><small>${guide.map((step, index) => `${index + 1}. ${step}`).join('<br>')}</small></div>
    <div><b>Comunicação</b><small>${item.email_sent ? 'Cliente notificado.' : 'Envio ao cliente ainda não confirmado.'}</small></div>
    <div><b>Horário</b><small>${new Date(item.created_at).toLocaleString('pt-BR')}</small></div>
  `;
  $('interventionModal').hidden = false;
  $('interventionConfirm').onclick = async () => {
    $('interventionConfirm').disabled = true;
    try {
      markAlertSeen(item.id);
      $('interventionModal').hidden = true;
      showToast('Leitura da tratativa confirmada no simulador. O aviso some da tela e a tratativa segue no painel.', 'success');
      renderAlertSignal();
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      $('interventionConfirm').disabled = false;
    }
  };
}

$('interventionClose').onclick = () => {
  $('interventionModal').hidden = true;
};

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
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : {};
  if (!response.ok) throw new Error(data.error || data.message || `Falha no servidor (${response.status}).`);
  return data;
}

async function refreshRawSensor() {
  const data = await request('/api/sensor/grid');
  renderRawGrid(data);
  $('updated').textContent = `Leitura bruta: ${new Date(data.captured_at).toLocaleString('pt-BR')}`;
  $('zones').textContent = data.valid_zones;
  $('alerts').innerHTML = '<div class="alert ok">Diagnóstico ao vivo: distâncias em milímetros. Volume requer calibração do box vazio.</div>';
}

async function loadHistory() {
  const items = await request('/api/readings/history?limit=20');
  drawHistory(items);
}

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
    if (!state.health.demo_enabled && latest.status === 'no_data') {
      $('capture').textContent = 'Atualizar leitura do sensor';
      await refreshRawSensor();
      state.rawTimer = window.setInterval(() => refreshRawSensor().catch(error => showToast(error.message, 'error')), 10000);
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

$('setup').onclick = async () => {
  const data=await request('/api/demo/setup',{method:'POST'});
  render(data.reading);
  await Promise.all([loadHistory(), loadActiveAlerts()]);
};

$('stopDemo').onclick = async () => {
  try {
    const data = await request('/api/demo/scenario/empty', {method:'POST'});
    render(data);
    state.activeAlerts.forEach(item => markAlertSeen(item.id));
    $('interventionModal').hidden = true;
    await Promise.all([loadHistory(), loadActiveAlerts()]);
    showToast('Demonstração pausada e box retornado ao cenário vazio.', 'success');
  } catch (error) {
    showToast(error.message, 'error');
  }
};

$('capture').onclick = async () => {
  try {
    if (!state.health.demo_enabled && !state.latest?.id) {
      await refreshRawSensor();
      return;
    }
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

initialize();
