const $ = id => document.getElementById(id);
const escapeHtml = text => String(text ?? '').replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
const statusLabels = {open:'Aberta', acknowledged:'Ciente', in_progress:'Em atendimento', resolved:'Resolvida', false_positive:'Falso positivo'};
const typeLabels = {capacity:'Capacidade', confidence:'Baixa confiança', obstruction:'Obstrução'};
const alertStorageKey = 'boxtwin_intervention_seen_admin';
let lastSoundAlertId = null;
let reminderIntervalId = null;
let lastReminderAlertId = null;
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
  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
  oscillator.frequency.exponentialRampToValueAtTime(660, audioContext.currentTime + 0.22);
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
<<<<<<< HEAD
    <article class="incident ${escapeHtml(item.severity)}">
      <div><a href="/admin/anomalies/${item.id}"><b>#${item.id} · ${escapeHtml(item.message)}</b></a><small>${localDate(item.created_at)} · ${escapeHtml(typeLabels[item.anomaly_type] || item.anomaly_type)}</small></div>
      <span class="badge">${escapeHtml(statusLabels[item.status] || item.status)}</span>
      ${item.status === 'open' ? `<button onclick="ack(${item.id})" class="secondary compact">Registrar ciência</button>` : ''}
      <button onclick="askIncident(${item.id})" class="secondary compact">Sugerir tratativa</button>
=======
    <article class="incident ${escapeHtml(item.severity)} ${item.status === 'open' || item.status === 'acknowledged' ? 'needs-attention' : ''}">
      <div>
        <a href="/admin/anomalies/${item.id}"><b>#${item.id} · ${escapeHtml(item.message)}</b></a>
        <small>${localDate(item.created_at)} · ${escapeHtml(typeLabels[item.anomaly_type] || item.anomaly_type)}</small>
        <span class="alert-pill ${item.email_sent ? 'email-sent' : ''}">${item.email_sent ? 'E-mail enviado ao cliente' : 'Aguardando envio/registro de e-mail'}</span>
        <div id="treatment-inline-${item.id}" class="assistant-answer" style="display:none;margin-top:10px;"></div>
      </div>
      <span class="badge status-badge status-${escapeHtml(item.status)}">${escapeHtml(statusLabels[item.status] || item.status)}</span>
      <button onclick="verifyIncident(${item.id})" class="secondary compact">Verificar</button>
      <button onclick="treatIncident(${item.id})" class="primary compact">Tratado</button>
>>>>>>> 62ebd29 (feat: alertas, relatórios, sync edge-railway e preparo raspberry)
    </article>`).join('') : '<p class="muted">Nenhuma anomalia registrada.</p>';
}

function renderActiveAlertSignal(items) {
  const banner = $('adminAlertBanner');
  const first = items[0];
  if (!first) {
    banner.hidden = true;
    banner.className = 'panel alert-signal';
    lastSoundAlertId = null;
    stopReminderLoop();
    return;
  }
  banner.hidden = false;
  banner.className = `panel alert-signal ${first.status === 'open' ? 'active' : ''} ${first.severity === 'danger' ? 'danger' : 'warning'}`;
  $('adminAlertTitle').textContent = `${typeLabels[first.anomaly_type] || first.anomaly_type} exige tratativa`;
  $('adminAlertMeta').textContent = `${items.length} alerta(s) ativo(s) · ${first.email_sent ? 'e-mail enviado' : 'e-mail pendente'} · ${statusLabels[first.status] || first.status}`;
  $('adminAlertText').textContent = `${first.message} Status atual: ${statusLabels[first.status] || first.status}.`;
  if (first.status === 'open' && first.id !== lastSoundAlertId) {
    playAlertSound();
    lastSoundAlertId = first.id;
  }
  startReminderLoop(first);
  const seen = new Set(acknowledgedAlerts());
  const pendingHuman = items.find(item => item.status === 'open' && !seen.has(item.id));
  if (pendingHuman) openInterventionModal(pendingHuman);
}

function openInterventionModal(item) {
  $('interventionTitle').textContent = `${typeLabels[item.anomaly_type] || item.anomaly_type} requer intervenção`;
  $('interventionText').textContent = item.message;
  $('interventionDetails').innerHTML = `
    <div><b>Status operacional</b><small>${escapeHtml(statusLabels[item.status] || item.status)}</small></div>
    <div><b>Comunicação com o cliente</b><small>${item.email_sent ? 'E-mail de alerta enviado ao endereço configurado.' : 'Envio de e-mail ainda não confirmado.'}</small></div>
    <div><b>Data do evento</b><small>${escapeHtml(localDate(item.created_at))}</small></div>
  `;
  $('interventionModal').hidden = false;
  $('interventionConfirm').onclick = async () => {
    $('interventionConfirm').disabled = true;
    try {
      await api(`/api/admin/anomalies/${item.id}/acknowledge`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({note:'Leitura da tratativa confirmada no painel administrativo.'})});
      markAlertSeen(item.id);
      $('interventionModal').hidden = true;
      showToast('Ciência da anomalia registrada. O alerta segue visível no painel.', 'success');
      await loadAdmin();
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      $('interventionConfirm').disabled = false;
    }
  };
}

async function loadAdmin() {
  try {
    const [summary, anomalies, notifications, recipients, rules, activeAlerts] = await Promise.all([
      api('/api/admin/summary'),
      api('/api/admin/anomalies?limit=50&status=active'),
      api('/api/admin/notifications?limit=30'),
      api('/api/admin/recipients'),
      api('/api/admin/rules'),
      api('/api/alerts/active?limit=10'),
    ]);
    const emailState = new Map(activeAlerts.items.map(item => [item.id, item.email_sent]));
    const enrichedAnomalies = anomalies.map(item => ({...item, email_sent: emailState.get(item.id) || false}));
    renderSummary(summary);
    renderAnomalies(enrichedAnomalies);
    renderActiveAlertSignal(activeAlerts.items);
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

<<<<<<< HEAD
=======
async function verifyIncident(id) {
  const item = anomaliesById.get(id);
  if (!item) return;
  const box = $(`treatment-inline-${id}`);
  box.style.display = 'block';
  box.innerHTML = '<p>Analisando tratativa recomendada…</p>';
  try {
    if (item.status === 'open') {
      await api(`/api/admin/anomalies/${id}/acknowledge`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({note:'Ocorrência verificada no painel administrativo.'})});
    }
    const result = await api('/api/admin/assistant', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({question:`Quero verificar a anomalia ${item.anomaly_type}. Passe a tratativa e as verificações práticas para esta ocorrência: ${item.message}.`})
    });
    box.innerHTML = `<p>${escapeHtml(result.answer)}</p><small>Modo: ${escapeHtml(result.mode)} · Fontes: ${result.sources.map(source => escapeHtml(source.id)).join(', ')}</small>`;
    await loadAdmin();
  } catch (error) {
    box.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  }
}

async function treatIncident(id) {
  const item = anomaliesById.get(id);
  if (!item) return;
  await api(`/api/admin/anomalies/${id}/status`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      status:'resolved',
      note:'Ocorrência verificada e tratada no painel administrativo.',
    }),
  });
  showToast('Anomalia registrada como tratada e movida para o relatório.', 'success');
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

>>>>>>> 62ebd29 (feat: alertas, relatórios, sync edge-railway e preparo raspberry)
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
