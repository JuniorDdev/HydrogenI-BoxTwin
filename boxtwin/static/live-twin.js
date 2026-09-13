const canvas = document.getElementById('twinCanvas');
const context = canvas.getContext('2d');
const gridElement = document.getElementById('liveGrid');
const statusElement = document.getElementById('liveStatus');
const noticeElement = document.getElementById('liveNotice');

function formatDate(value) {
  return value ? new Date(value).toLocaleString('pt-BR') : '—';
}

function values(grid) { return grid.flat().filter(Number.isFinite); }

function colorFor(value, min, max) {
  if (!Number.isFinite(value)) return '#edf1f4';
  const normalized = max === min ? .5 : (value - min) / (max - min);
  const hue = 12 + normalized * 198;
  return `hsl(${hue} 78% ${42 + normalized * 18}%)`;
}

function renderGrid(grid) {
  const flat = values(grid); const min = Math.min(...flat); const max = Math.max(...flat);
  gridElement.replaceChildren(...grid.flat().map(value => {
    const cell = document.createElement('div');
    const relative = !Number.isFinite(value) ? 'none' : value < min + (max-min)/3 ? 'near' : value < min + (max-min)*2/3 ? 'mid' : 'far';
    cell.className = `live-zone ${relative}`;
    cell.textContent = Number.isFinite(value) ? `${Math.round(value)}` : '—';
    cell.title = Number.isFinite(value) ? `${value} mm` : 'sem leitura';
    return cell;
  }));
}

function drawTwin(grid) {
  const width = canvas.clientWidth; const height = canvas.clientHeight;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = width * dpr; canvas.height = height * dpr;
  context.setTransform(dpr, 0, 0, dpr, 0, 0);
  context.clearRect(0, 0, width, height);
  const flat = values(grid); if (!flat.length) return;
  const min = Math.min(...flat), max = Math.max(...flat);
  const origin = { x: width / 2, y: height * .17 };
  const sx = Math.min(width * .055, 42), sy = sx * .48, sz = Math.min(height * .5, 230);
  const project = (x, y, z) => ({ x: origin.x + (x-y)*sx, y: origin.y + (x+y)*sy - z });
  context.strokeStyle = '#70d8ff45'; context.lineWidth = 1;
  for (let r = 0; r <= 8; r++) { const a=project(0,r,0), b=project(8,r,0); context.beginPath();context.moveTo(a.x,a.y);context.lineTo(b.x,b.y);context.stroke(); }
  for (let c = 0; c <= 8; c++) { const a=project(c,0,0), b=project(c,8,0); context.beginPath();context.moveTo(a.x,a.y);context.lineTo(b.x,b.y);context.stroke(); }
  for (let r = 7; r >= 0; r--) for (let c = 0; c < 8; c++) {
    const value = grid[r][c]; if (!Number.isFinite(value)) continue;
    const closeness = max === min ? .5 : (max-value)/(max-min);
    const z = 12 + closeness * sz;
    const p1=project(c,r,0), p2=project(c+1,r,0), p3=project(c+1,r+1,0), p4=project(c,r+1,0);
    const t1=project(c,r,z), t2=project(c+1,r,z), t3=project(c+1,r+1,z), t4=project(c,r+1,z);
    context.fillStyle = colorFor(value,min,max); context.beginPath();context.moveTo(t1.x,t1.y);context.lineTo(t2.x,t2.y);context.lineTo(t3.x,t3.y);context.lineTo(t4.x,t4.y);context.closePath();context.fill();
    context.fillStyle = 'rgba(5,18,35,.38)'; context.beginPath();context.moveTo(t3.x,t3.y);context.lineTo(p3.x,p3.y);context.lineTo(p4.x,p4.y);context.lineTo(t4.x,t4.y);context.closePath();context.fill();
    context.fillStyle = 'rgba(255,255,255,.18)'; context.beginPath();context.moveTo(t2.x,t2.y);context.lineTo(p2.x,p2.y);context.lineTo(p3.x,p3.y);context.lineTo(t3.x,t3.y);context.closePath();context.fill();
  }
}

async function refresh() {
  try {
    const response = await fetch('/api/live-grid', { cache: 'no-store' });
    const data = await response.json();
    document.getElementById('refreshedAt').textContent = new Date().toLocaleTimeString('pt-BR');
    if (data.status === 'no_data') {
      statusElement.textContent = 'Aguardando sensor'; return;
    }
    renderGrid(data.distance_grid_mm); drawTwin(data.distance_grid_mm);
    document.getElementById('nodeLabel').textContent = data.node_id;
    document.getElementById('capturedAt').textContent = formatDate(data.captured_at);
    document.getElementById('validZones').textContent = `${data.valid_zones} de 64`;
    statusElement.textContent = 'Sensor sincronizado'; statusElement.classList.add('demo');
    noticeElement.className = 'live-notice'; noticeElement.textContent = 'Leitura bruta recebida. A geometria é relativa à distância, sem calibração de box ou cálculo de volume.';
  } catch (error) { statusElement.textContent = 'Falha ao atualizar'; }
}
window.addEventListener('resize', refresh); refresh(); setInterval(refresh, 10000);
