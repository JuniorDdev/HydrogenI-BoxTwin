const $ = id => document.getElementById(id);
const storageKey = 'hydrogeni-mobile-config';
const sameOrigin = window.location.origin;
let activeBaseUrl = sameOrigin;
let activeMode = 'cloud';

function cleanBaseUrl(value) {
  return String(value || '').trim().replace(/\/+$/, '');
}

function loadConfig() {
  const stored = JSON.parse(localStorage.getItem(storageKey) || '{}');
  $('localBaseUrl').value = stored.localBaseUrl || 'http://boxtwin.local:5000';
  $('cloudBaseUrl').value = stored.cloudBaseUrl || sameOrigin;
  activeBaseUrl = cleanBaseUrl(stored.activeBaseUrl || sameOrigin);
  activeMode = stored.activeMode || (activeBaseUrl.includes('boxtwin.local') ? 'local' : 'cloud');
  renderEndpoint();
}

function saveConfig() {
  localStorage.setItem(storageKey, JSON.stringify({
    localBaseUrl: cleanBaseUrl($('localBaseUrl').value),
    cloudBaseUrl: cleanBaseUrl($('cloudBaseUrl').value),
    activeBaseUrl,
    activeMode,
  }));
}

function renderEndpoint() {
  $('activeEndpoint').textContent = `Fonte atual: ${activeMode === 'local' ? 'Raspberry/local' : 'Railway/nuvem'} · ${activeBaseUrl}`;
}

function setStatus(online, text) {
  const badge = $('mobileStatus');
  badge.className = `mobile-status ${online ? 'online' : 'offline'}`;
  badge.textContent = text || (online ? 'Online' : 'Offline');
}

async function api(path, options = {}) {
  const response = await fetch(`${activeBaseUrl}${path}`, {
    ...options,
    headers: {'Content-Type': 'application/json', ...(options.headers || {})},
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

function fmt(value, digits = 1) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : '--';
}

function localDate(value) {
  return value ? new Date(value).toLocaleString('pt-BR', {dateStyle: 'short', timeStyle: 'short'}) : '--';
}

function renderReading(reading) {
  if (!reading || reading.status === 'no_data') {
    $('mobileReading').innerHTML = '<p class="muted">Nenhuma medição registrada nessa fonte.</p>';
    return;
  }
  $('mCapacity').textContent = fmt(reading.capacity_percent);
  $('mVolume').textContent = fmt(reading.volume_m3, 4);
  $('mConfidence').textContent = fmt(reading.confidence_percent);
  $('mZones').textContent = reading.valid_zones ?? '--';
  const alertText = (reading.alerts || []).length
    ? `<b class="mobile-danger">${reading.alerts.map(alert => alert.message).join(' · ')}</b>`
    : '<b class="mobile-ok">Operação normal</b>';
  $('mobileReading').innerHTML = `
    <div class="mobile-reading-row"><span>Status</span>${alertText}</div>
    <div class="mobile-reading-row"><span>BoxNode</span><b>${reading.node_id || '--'}</b></div>
    <div class="mobile-reading-row"><span>Cenário/sensor</span><b>${reading.scenario || reading.sensor_mode || '--'}</b></div>
    <div class="mobile-reading-row"><span>Atualizado</span><b>${localDate(reading.created_at || reading.captured_at)}</b></div>
  `;
}

function renderAlerts(payload) {
  const items = payload.items || [];
  $('mobileAlerts').innerHTML = items.length ? items.map(item => `
    <article class="mobile-list-item">
      <b>#${item.id} · ${item.message}</b>
      <small>${item.status || 'aberta'} · ${localDate(item.created_at)}</small>
    </article>
  `).join('') : '<p class="muted">Nenhuma tratativa ativa.</p>';
}

function renderHistory(items) {
  $('mobileHistory').innerHTML = items.length ? items.slice(-8).reverse().map(item => `
    <article class="mobile-list-item">
      <b>${fmt(item.capacity_percent)}% · ${fmt(item.volume_m3, 4)} m³</b>
      <small>${localDate(item.created_at)} · confiança ${fmt(item.confidence_percent)}%</small>
    </article>
  `).join('') : '<p class="muted">Nenhum histórico encontrado.</p>';
}

async function refreshAll() {
  try {
    setStatus(false, 'Conectando...');
    const [health, latest, alerts, history] = await Promise.all([
      api('/api/health'),
      api('/api/readings/latest'),
      api('/api/alerts/active?limit=20'),
      api('/api/readings/history?limit=20'),
    ]);
    setStatus(true, health.sensor_mode === 'mock' ? 'Online · mock' : 'Online · sensor');
    renderReading(latest);
    renderAlerts(alerts);
    renderHistory(history);
  } catch (error) {
    setStatus(false, 'Falha');
    $('mobileReading').innerHTML = `<p class="mobile-error">${error.message}. Verifique se a URL está correta e se o Raspberry está na mesma rede.</p>`;
  }
}

async function capture() {
  if (activeMode !== 'local') {
    $('mobileReading').innerHTML = '<p class="mobile-error">Para capturar, selecione a fonte Raspberry/local.</p>';
    return;
  }
  try {
    const reading = await api('/api/readings', {method: 'POST'});
    renderReading(reading);
    await refreshAll();
  } catch (error) {
    $('mobileReading').innerHTML = `<p class="mobile-error">${error.message}</p>`;
  }
}

async function calibrate() {
  if (activeMode !== 'local') {
    $('mobileReading').innerHTML = '<p class="mobile-error">Para calibrar, selecione a fonte Raspberry/local.</p>';
    return;
  }
  try {
    const result = await api('/api/calibration', {method: 'POST'});
    $('mobileReading').innerHTML = `<p class="mobile-ok">${result.message || 'Calibração salva.'}</p>`;
  } catch (error) {
    $('mobileReading').innerHTML = `<p class="mobile-error">${error.message}</p>`;
  }
}

$('useLocal').addEventListener('click', () => {
  activeBaseUrl = cleanBaseUrl($('localBaseUrl').value);
  activeMode = 'local';
  saveConfig();
  renderEndpoint();
  refreshAll();
});

$('useCloud').addEventListener('click', () => {
  activeBaseUrl = cleanBaseUrl($('cloudBaseUrl').value);
  activeMode = 'cloud';
  saveConfig();
  renderEndpoint();
  refreshAll();
});

$('refreshMobile').addEventListener('click', refreshAll);
$('captureMobile').addEventListener('click', capture);
$('calibrateMobile').addEventListener('click', calibrate);

loadConfig();
refreshAll();
