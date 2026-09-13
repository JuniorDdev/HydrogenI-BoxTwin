const byId = id => document.getElementById(id);
const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
let chartLimit = 20;
let readingsCache = [];

async function painelApi(url) {
  const response = await fetch(url);
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : {};
  if (response.status === 401) {
    location.href = '/login';
    throw new Error('Sessão expirada.');
  }
  if (!response.ok) throw new Error(data.error || 'Falha ao carregar o painel.');
  return data;
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('pt-BR', {dateStyle:'short', timeStyle:'short'}) : '-';
}

function formatM3(value) {
  return Number(value || 0).toLocaleString('pt-BR', {minimumFractionDigits:4, maximumFractionDigits:4}) + ' m³';
}

function updateClock() {
  byId('painelClock').textContent = new Date().toLocaleTimeString('pt-BR', {hour12:false});
}

function drawChart(items) {
  const canvas = byId('painelChart');
  const context = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = rect.width * ratio;
  canvas.height = rect.height * ratio;
  context.scale(ratio, ratio);
  context.clearRect(0, 0, rect.width, rect.height);

  const values = items.map(item => Number(item.volume_m3 || 0));
  if (!values.length) {
    context.fillStyle = '#63716c';
    context.font = '14px Arial';
    context.fillText('Sem leituras para exibir.', 24, 42);
    return;
  }

  const pad = 24;
  const min = Math.min(...values) - 0.02;
  const max = Math.max(...values) + 0.02;
  const width = rect.width - pad * 2;
  const height = rect.height - pad * 2;
  context.strokeStyle = 'rgba(130,143,163,.18)';
  context.lineWidth = 1;
  for (let index = 0; index < 5; index += 1) {
    const y = pad + (height / 4) * index;
    context.beginPath();
    context.moveTo(pad, y);
    context.lineTo(rect.width - pad, y);
    context.stroke();
  }

  const points = values.map((value, index) => ({
    x: values.length === 1 ? rect.width / 2 : pad + (width / (values.length - 1)) * index,
    y: pad + height - ((value - min) / (max - min || 1)) * height,
  }));
  const gradient = context.createLinearGradient(0, pad, 0, rect.height - pad);
  gradient.addColorStop(0, 'rgba(21,183,158,.32)');
  gradient.addColorStop(1, 'rgba(21,183,158,0)');
  context.beginPath();
  points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
  context.lineTo(points[points.length - 1].x, rect.height - pad);
  context.lineTo(points[0].x, rect.height - pad);
  context.closePath();
  context.fillStyle = gradient;
  context.fill();
  context.beginPath();
  points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
  context.strokeStyle = '#15b79e';
  context.lineWidth = 3;
  context.lineJoin = 'round';
  context.lineCap = 'round';
  context.stroke();
  points.forEach((point, index) => {
    context.beginPath();
    context.arc(point.x, point.y, index === points.length - 1 ? 5 : 3.5, 0, Math.PI * 2);
    context.fillStyle = index === points.length - 1 ? '#fff' : '#15b79e';
    context.fill();
    context.strokeStyle = '#15b79e';
    context.lineWidth = 2;
    context.stroke();
  });
}

function renderSummary(summary) {
  const latest = summary.latest;
  byId('painelVolume').textContent = latest ? formatM3(latest.volume_m3) : '-';
  byId('painelOccupancy').textContent = latest ? Number(latest.capacity_percent).toFixed(1) + '%' : '-';
  byId('painelConfidence').textContent = summary.average_confidence ? `${summary.average_confidence}%` : '-';
  byId('painelAlerts').textContent = summary.active_incidents ?? '-';
  byId('painelTankFill').style.height = latest ? `${Math.max(0, Math.min(100, Number(latest.capacity_percent)))}%` : '0%';
  byId('painelTankVolume').textContent = latest ? formatM3(latest.volume_m3) : 'Sem leitura';
  byId('painelTankStatus').textContent = latest ? `${escapeHtml(latest.status || 'online')} · ${formatDate(latest.created_at)}` : 'Aguardando telemetria';
  byId('painelTrend').textContent = latest ? `Modo ${summary.sensor_mode === 'mock' ? 'virtual' : 'físico'}` : 'Aguardando leitura';
}

function renderReadings(items) {
  byId('painelReadings').innerHTML = items.slice(-6).reverse().map(item => `
    <tr>
      <td>${escapeHtml(formatDate(item.created_at))}</td>
      <td>${escapeHtml(formatM3(item.volume_m3))}</td>
      <td>${Number(item.capacity_percent || 0).toFixed(1)}%</td>
      <td>${Number(item.confidence_percent || 0).toFixed(1)}%</td>
      <td>${escapeHtml(item.status || '-')}</td>
    </tr>
  `).join('') || '<tr><td colspan="5" class="painel-empty">Nenhuma leitura registrada.</td></tr>';
}

function renderAlerts(payload) {
  const items = payload.items || [];
  byId('painelAlertList').innerHTML = items.map(item => {
    const badge = item.severity === 'danger' ? 'danger' : item.severity === 'warning' ? 'warning' : 'ok';
    return `<article class="painel-alert">
      <span class="painel-badge ${badge}">${escapeHtml(item.severity || 'info')}</span>
      <b>${escapeHtml(item.message || 'Alerta operacional')}</b>
      <p>${escapeHtml(item.status || 'ativo')} · ${escapeHtml(formatDate(item.created_at))}</p>
    </article>`;
  }).join('') || '<p class="painel-empty">Nenhum alerta ativo no momento.</p>';
}

async function loadPainel() {
  try {
    const [summary, history, alerts] = await Promise.all([
      painelApi('/api/admin/summary'),
      painelApi(`/api/readings/history?limit=${chartLimit}`),
      painelApi('/api/alerts/active?limit=10'),
    ]);
    readingsCache = history;
    renderSummary(summary);
    renderReadings(history);
    renderAlerts(alerts);
    drawChart(history);
    byId('painelConnection').textContent = 'Online';
  } catch (error) {
    byId('painelConnection').textContent = 'Sem conexão';
    byId('painelAlertList').innerHTML = `<div class="painel-alert"><span class="painel-badge danger">Erro</span><b>${escapeHtml(error.message)}</b></div>`;
  }
}

document.querySelectorAll('.painel-actions button').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.painel-actions button').forEach(item => item.classList.remove('selected'));
    button.classList.add('selected');
    chartLimit = Number(button.dataset.limit || 20);
    loadPainel();
  });
});

byId('painelRefresh').addEventListener('click', loadPainel);
window.addEventListener('resize', () => drawChart(readingsCache));
window.setInterval(updateClock, 1000);
updateClock();
loadPainel();

const stream = new EventSource('/api/stream');
stream.addEventListener('reading', () => loadPainel());
stream.onerror = () => { byId('painelConnection').textContent = 'Reconectando'; };
stream.onopen = () => { byId('painelConnection').textContent = 'Online'; };
