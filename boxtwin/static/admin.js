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
      <span class="badge status-badge status-${escapeHtml(item.status)}">${escapeHtml(statusLabels[item.status] || item.status)}</span>
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
    const activeRecipients = recipients.filter(item => item.active);
    $('ruleRecipient').innerHTML = activeRecipients.map(item => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join('');
    $('ruleRecipientWarning').hidden = activeRecipients.length > 0;
    $('ruleForm').querySelector('button').disabled = activeRecipients.length === 0;
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

function openAssistant() {
  $('assistantChat').hidden = false;
  $('assistantBackdrop').classList.add('visible');
  $('assistantToggle').setAttribute('aria-expanded', 'true');
  $('assistantToggle').classList.add('open');
  $('assistantQuestion').focus();
}

function closeAssistant() {
  $('assistantChat').hidden = true;
  $('assistantBackdrop').classList.remove('visible');
  $('assistantToggle').setAttribute('aria-expanded', 'false');
  $('assistantToggle').classList.remove('open');
}

function appendAssistantMessage(text, variant, meta) {
  const bubble = document.createElement('div');
  bubble.className = `assistant-msg assistant-msg-${variant}`;
  const paragraph = document.createElement('p');
  paragraph.style.margin = '0';
  paragraph.textContent = text;
  bubble.appendChild(paragraph);
  if (meta) {
    const small = document.createElement('small');
    small.textContent = meta;
    bubble.appendChild(small);
  }
  const container = $('assistantMessages');
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

let assistantHistory = [];

async function askIncident(id) {
  const item = anomaliesById.get(id);
  if (!item) return;
  const question = `Anomalia #${id}: ${item.message}. Qual é a tratativa recomendada e quais verificações devem ser feitas?`;
  openAssistant();
  await queryAssistant(question);
}

async function queryAssistant(question) {
  const cleanQuestion = String(question || '').trim();
  if (!cleanQuestion) return;
  appendAssistantMessage(cleanQuestion, 'user');
  $('assistantQuestion').value = '';
  autosizeAssistantInput();
  updateAssistantCount();
  $('assistantTyping').hidden = false;
  try {
    const result = await api('/api/admin/assistant', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question:cleanQuestion, history:assistantHistory})});
    const sources = result.sources.map(source => `${source.id} - ${source.title}`).join('; ') || 'nenhuma fonte correspondente';
    appendAssistantMessage(result.answer, 'bot', `Fontes: ${sources} · Modo: ${result.mode}`);
    assistantHistory = [...assistantHistory, {question: cleanQuestion, answer: result.answer}].slice(-6);
  } catch (error) {
    appendAssistantMessage(error.message, 'error');
  } finally {
    $('assistantTyping').hidden = true;
  }
}

function updateAssistantCount() {
  $('assistantCount').textContent = `${$('assistantQuestion').value.length}/1200`;
}

function autosizeAssistantInput() {
  const field = $('assistantQuestion');
  field.style.height = 'auto';
  field.style.height = `${field.scrollHeight}px`;
}

$('assistantToggle').addEventListener('click', () => {
  if ($('assistantChat').hidden) openAssistant();
  else closeAssistant();
});
$('assistantClose').addEventListener('click', closeAssistant);
$('assistantBackdrop').addEventListener('click', closeAssistant);
$('assistantForm').addEventListener('submit', event => { event.preventDefault(); queryAssistant($('assistantQuestion').value); });
$('assistantQuestion').addEventListener('input', () => { updateAssistantCount(); autosizeAssistantInput(); });
$('assistantQuestion').addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    queryAssistant($('assistantQuestion').value);
  }
});
document.querySelectorAll('.quick-prompt').forEach(button => button.addEventListener('click', () => {
  openAssistant();
  queryAssistant(button.dataset.prompt);
}));
$('refreshAdmin').addEventListener('click', loadAdmin);
$('recipientForm').addEventListener('submit', async event => {
  event.preventDefault();
  try {
    await api('/api/admin/recipients', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:$('recipientName').value, recipient_type:$('recipientType').value, team_name:$('recipientTeam').value, email:$('recipientEmail').value, phone:$('recipientPhone').value})});
    event.target.reset();
    showToast('Responsável cadastrado com sucesso.', 'success');
    await loadAdmin();
  } catch (error) {
    showToast(error.message, 'error');
  }
});
$('ruleForm').addEventListener('submit', async event => {
  event.preventDefault();
  if (!$('ruleRecipient').value) {
    showToast('Cadastre um responsável ativo antes de criar uma regra.', 'error');
    return;
  }
  try {
    await api('/api/admin/rules', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({anomaly_type:$('ruleType').value, severity:$('ruleSeverity').value, recipient_id:$('ruleRecipient').value, channel:$('ruleChannel').value, escalation_minutes:$('ruleDelay').value})});
    showToast('Regra de automação criada com sucesso.', 'success');
    await loadAdmin();
  } catch (error) {
    showToast(error.message, 'error');
  }
});

const stream = new EventSource('/api/stream');
stream.addEventListener('reading', () => loadAdmin());
stream.onerror = () => { $('adminConnection').textContent = 'Reconectando...'; };
stream.onopen = () => { $('adminConnection').textContent = 'Online'; };
loadAdmin();
