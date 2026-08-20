const $ = id => document.getElementById(id);
let detail;

const safe = value => String(value ?? '—').replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));

async function api(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (response.status === 401) {
    location.href = '/login';
    throw new Error('Sessão expirada');
  }
  if (!response.ok) throw new Error(data.error || 'Falha');
  return data;
}

function renderGrid(reading) {
  const box = $('incidentGrid');
  box.innerHTML = '';
  (reading?.height_grid_m || []).flat().forEach(value => {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.textContent = (value * 100).toFixed(1);
    cell.style.opacity = .45 + Math.min(1, value / (reading.maximum_height_m || 1)) * .55;
    box.appendChild(cell);
  });
}

async function load() {
  detail = await api(`/api/admin/anomalies/${window.ANOMALY_ID}`);
  const anomaly = detail.anomaly;
  const reading = detail.reading;
  $('incidentSummary').innerHTML = `<div><span class="eyebrow">${safe(anomaly.severity)} · ${safe(anomaly.status)}</span><h2>${safe(anomaly.message)}</h2><p>${new Date(anomaly.created_at).toLocaleString('pt-BR')} · ${safe(reading?.node_id)}</p></div>`;
  $('readingDetail').innerHTML = `
    <div><small>Ocupação</small><b>${reading?.capacity_percent ?? '—'}%</b></div>
    <div><small>Volume</small><b>${reading?.volume_m3 ?? '—'} m³</b></div>
    <div><small>Confiança</small><b>${reading?.confidence_percent ?? '—'}%</b></div>
    <div><small>Zonas válidas</small><b>${reading?.valid_zones ?? '—'}/64</b></div>
  `;
  renderGrid(reading);
  $('timeline').innerHTML = [{created_at: anomaly.created_at, actor: 'BoxTwin', event_type: 'detected', note: anomaly.message}, ...detail.events]
    .map(event => `<div class="timeline-event"><b>${safe(event.event_type)}</b><span>${safe(event.actor)}</span><small>${new Date(event.created_at).toLocaleString('pt-BR')}</small><p>${safe(event.note)}</p></div>`)
    .join('');
}

$('statusForm').onsubmit = async event => {
  event.preventDefault();
  await api(`/api/admin/anomalies/${window.ANOMALY_ID}/status`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({status: $('incidentStatus').value, note: $('incidentNote').value}),
  });
  await load();
};

$('suggestTreatment').onclick = async () => {
  const anomaly = detail.anomaly;
  const reading = detail.reading;
  $('treatment').textContent = 'Analisando…';
  const result = await api('/api/admin/assistant', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: `Como tratar ${anomaly.anomaly_type}: ${anomaly.message}?`, context: reading}),
  });
  $('treatment').innerHTML = `<p>${safe(result.answer)}</p><small>Modo: ${safe(result.mode)} · Fontes: ${result.sources.map(source => safe(source.id)).join(', ')}</small>`;
};

$('verifyButton').onclick = async () => {
  const anomaly = detail.anomaly;
  const reading = detail.reading;
  $('treatment').textContent = 'Verificando tratativa…';
  if (anomaly.status === 'open') {
    await api(`/api/admin/anomalies/${window.ANOMALY_ID}/acknowledge`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({note: 'Ocorrência verificada na página de detalhe.'}),
    });
  }
  const result = await api('/api/admin/assistant', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: `Quero verificar a anomalia ${anomaly.anomaly_type}. Passe a tratativa e as verificações práticas para esta ocorrência: ${anomaly.message}.`, context: reading}),
  });
  $('treatment').innerHTML = `<p>${safe(result.answer)}</p><small>Modo: ${safe(result.mode)} · Fontes: ${result.sources.map(source => safe(source.id)).join(', ')}</small>`;
  await load();
};

$('treatedButton').onclick = async () => {
  await api(`/api/admin/anomalies/${window.ANOMALY_ID}/status`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({status: 'resolved', note: 'Ocorrência verificada e tratada na página de detalhe.'}),
  });
  await load();
};

load();
