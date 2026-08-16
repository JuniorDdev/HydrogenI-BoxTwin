const $ = id => document.getElementById(id);
const escapeHtml = text => String(text ?? '').replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
const statusLabels = {open:'Aberta', acknowledged:'Ciente', in_progress:'Em atendimento', resolved:'Resolvida', false_positive:'Falso positivo'};
const typeLabels = {capacity:'Capacidade', confidence:'Baixa confiança', obstruction:'Obstrução'};
let anomaliesById = new Map();

async function api(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : {};
  if (response.status === 401) {
    location.href = '/login';
    throw new Error('Sessão expirada.');
  }
  if (!response.ok) throw new Error(data.error || 'Não foi possível concluir a operação.');
  return data;
}

function localDate(value) {
  return value ? new Date(value).toLocaleString('pt-BR', {dateStyle:'short', timeStyle:'short'}) : '-';
}

function renderSummary(summary) {
  const latest = summary.latest;
  $('adminOccupancy').textContent = latest ? Number(latest.capacity_percent).toFixed(1) : '-';
  $('adminVolume').textContent = latest ? `${Number(latest.volume_m3).toFixed(4)} m³ estimados` : 'Sem leitura';
  $('adminConfidence').textContent = summary.average_confidence ?? '-';
  $('adminActive').textContent = summary.active_incidents;
  $('adminResolved').textContent = summary.resolved_incidents;
  $('adminSensorMode').textContent = summary.sensor_mode === 'mock' ? 'Virtual' : 'Físico';
  $('adminReadingTime').textContent = latest ? `Leitura: ${localDate(latest.created_at)}` : 'Aguardando telemetria';
}

function renderAnomalies(items) {
  anomaliesById = new Map(items.map(item => [item.id, item]));
  $('anomalyList').innerHTML = items.length ? items.map(item => `
    <article class="incident ${escapeHtml(item.severity)}">
      <div><a href="/admin/anomalies/${item.id}"><b>#${item.id} · ${escapeHtml(item.message)}</b></a><small>${localDate(item.created_at)} · ${escapeHtml(typeLabels[item.anomaly_type] || item.anomaly_type)}</small></div>
      <span class="badge">${escapeHtml(statusLabels[item.status] || item.status)}</span>
      ${item.status === 'open' ? `<button onclick="ack(${item.id})" class="secondary compact">Registrar ciência</button>` : ''}
      <button onclick="askIncident(${item.id})" class="secondary compact">Sugerir tratativa</button>
    </article>`).join('') : '<p class="muted">Nenhuma anomalia registrada.</p>';
}

async function loadAdmin() {
  try {
    const [summary, anomalies, notifications, recipients, rules] = await Promise.all([
      api('/api/admin/summary'), api('/api/admin/anomalies?limit=50'), api('/api/admin/notifications?limit=30'),
      api('/api/admin/recipients'), api('/api/admin/rules')
    ]);
    renderSummary(summary);
    renderAnomalies(anomalies);
    $('notificationList').innerHTML = notifications.length ? notifications.map(item => `<div class="notification-row"><b>${escapeHtml(item.channel)}</b><span>${escapeHtml(item.delivery_status || item.status)}</span><small>${localDate(item.created_at)}</small></div>`).join('') : '<p class="muted">Nenhuma notificação enviada. Os canais externos permanecem opcionais.</p>';
    $('recipientList').innerHTML = recipients.map(item => `<div class="list-row"><b>${escapeHtml(item.name)}</b><span>${escapeHtml(item.team_name || item.recipient_type)}</span><small>${escapeHtml(item.email || item.phone)}</small></div>`).join('') || '<p class="muted">Cadastre o primeiro responsável.</p>';
    $('ruleRecipient').innerHTML = recipients.filter(item => item.active).map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
    $('ruleList').innerHTML = rules.map(item => `<div class="list-row"><b>${escapeHtml(typeLabels[item.anomaly_type] || item.anomaly_type)} → ${escapeHtml(item.recipient_name)}</b><span>${escapeHtml(item.channel)}</span><small>${item.escalation_minutes ? `Após ${item.escalation_minutes} min` : 'Imediata'}</small></div>`).join('') || '<p class="muted">Nenhuma regra cadastrada.</p>';
    $('adminConnection').textContent = 'Online';
  } catch (error) {
    $('adminConnection').textContent = 'Sem conexão';
    $('anomalyList').innerHTML = `<div class="alert danger">${escapeHtml(error.message)}</div>`;
  }
}

async function ack(id) {
  await api(`/api/admin/anomalies/${id}/acknowledge`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({note:'Ciência registrada no painel.'})});
  await loadAdmin();
}

async function askIncident(id) {
  const item = anomaliesById.get(id);
  if (!item) return;
  const question = `Anomalia #${id}: ${item.message}. Qual é a tratativa recomendada e quais verificações devem ser feitas?`;
  $('assistantQuestion').value = question;
  updateAssistantCount();
  await queryAssistant(question);
}

async function queryAssistant(question) {
  const cleanQuestion = String(question || '').trim();
  if (!cleanQuestion) return;
  $('assistantAnswer').textContent = 'Consultando procedimentos e contexto operacional...';
  try {
    const result = await api('/api/admin/assistant', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:cleanQuestion})});
    const sources = result.sources.map(source => escapeHtml(`${source.id} - ${source.title}`)).join('; ') || 'nenhuma fonte correspondente';
    $('assistantAnswer').innerHTML = `<p>${escapeHtml(result.answer)}</p><small>Fontes: ${sources} · Modo: ${escapeHtml(result.mode)}</small>`;
  } catch (error) {
    $('assistantAnswer').innerHTML = `<div class="alert danger">${escapeHtml(error.message)}</div>`;
  }
}

function updateAssistantCount() {
  $('assistantCount').textContent = `${$('assistantQuestion').value.length}/1200`;
}

$('assistantForm').addEventListener('submit', event => { event.preventDefault(); queryAssistant($('assistantQuestion').value); });
$('assistantQuestion').addEventListener('input', updateAssistantCount);
document.querySelectorAll('.quick-prompt').forEach(button => button.addEventListener('click', () => {
  $('assistantQuestion').value = button.dataset.prompt;
  updateAssistantCount();
  queryAssistant(button.dataset.prompt);
}));
$('refreshAdmin').addEventListener('click', loadAdmin);
$('recipientForm').addEventListener('submit', async event => {
  event.preventDefault();
  await api('/api/admin/recipients', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:$('recipientName').value, recipient_type:$('recipientType').value, team_name:$('recipientTeam').value, email:$('recipientEmail').value, phone:$('recipientPhone').value})});
  event.target.reset();
  await loadAdmin();
});
$('ruleForm').addEventListener('submit', async event => {
  event.preventDefault();
  await api('/api/admin/rules', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({anomaly_type:$('ruleType').value, severity:$('ruleSeverity').value, recipient_id:$('ruleRecipient').value, channel:$('ruleChannel').value, escalation_minutes:$('ruleDelay').value})});
  await loadAdmin();
});

const stream = new EventSource('/api/stream');
stream.addEventListener('reading', () => loadAdmin());
stream.onerror = () => { $('adminConnection').textContent = 'Reconectando...'; };
stream.onopen = () => { $('adminConnection').textContent = 'Online'; };
loadAdmin();
