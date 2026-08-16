const landingEl = id => document.getElementById(id);

function landingFormat(value, digits = 1) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(digits).replace('.', ',') : '--';
}

function previewColor(value, max) {
  const ratio = Math.max(0, Math.min(1, value / Math.max(max, 0.001)));
  const hue = 210 - ratio * 165;
  return `hsl(${hue} 88% ${42 + ratio * 12}%)`;
}

function renderPreviewGrid(grid) {
  const values = grid?.flat?.() || Array.from({length: 64}, (_, index) => .05 + Math.sin(index / 5) * .025);
  const max = Math.max(...values.filter(Number.isFinite), .001);
  landingEl('landingGrid').innerHTML = values.map((value, index) => {
    const safe = Number.isFinite(Number(value)) ? Number(value) : 0;
    return `<i style="--delay:${index * 8}ms;background:${previewColor(safe, max)};opacity:${.35 + safe / max * .65}"></i>`;
  }).join('');
}

async function loadLandingTelemetry() {
  renderPreviewGrid();
  try {
    const [healthResponse, latestResponse] = await Promise.all([fetch('/api/health'), fetch('/api/readings/latest')]);
    const health = await healthResponse.json();
    const latest = await latestResponse.json();
    landingEl('landingStatus').textContent = health.status === 'online' ? 'BoxNode online' : 'Indisponível';
    landingEl('landingStatus').classList.toggle('online', health.status === 'online');
    if (latest.id) {
      landingEl('landingOccupancy').textContent = `${landingFormat(latest.capacity_percent)}%`;
      landingEl('landingConfidence').textContent = `${landingFormat(latest.confidence_percent)}%`;
      landingEl('landingVolume').textContent = `${landingFormat(latest.volume_m3, 4)} m³`;
      landingEl('landingReadingState').textContent = latest.status === 'alert' ? 'Leitura com alerta operacional.' : 'Leitura dentro dos limites.';
      renderPreviewGrid(latest.height_grid_m);
    } else {
      landingEl('landingReadingState').textContent = 'BoxNode online, ainda sem leitura registrada.';
    }
  } catch (error) {
    landingEl('landingStatus').textContent = 'Modo de apresentação';
    landingEl('landingReadingState').textContent = 'Abra o simulador para gerar telemetria.';
  }
}

const menuToggle = landingEl('menuToggle');
const landingMenu = landingEl('landingMenu');
menuToggle.addEventListener('click', () => {
  const open = landingMenu.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(open));
});
landingMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  landingMenu.classList.remove('open');
  menuToggle.setAttribute('aria-expanded', 'false');
}));

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, {threshold: .12});
document.querySelectorAll('.reveal').forEach(element => observer.observe(element));
loadLandingTelemetry();
