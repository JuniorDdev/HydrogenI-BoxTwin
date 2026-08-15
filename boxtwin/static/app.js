const $ = id => document.getElementById(id);
const grid = $('grid');

function render(data){
  if(!data || !data.id) return;
  $('volume').textContent = data.volume_m3.toFixed(4);
  $('capacity').textContent = data.capacity_percent.toFixed(1);
  $('confidence').textContent = data.confidence_percent.toFixed(1);
  $('zones').textContent = data.valid_zones;
  $('updated').textContent = new Date(data.created_at).toLocaleString('pt-BR');
  grid.innerHTML = '';
  const max = Math.max(...data.height_grid_m.flat(), .001);
  data.height_grid_m.flat().forEach(value => {
    const cell = document.createElement('div'); cell.className='cell';
    const intensity = .25 + .75 * value/max;
    cell.style.background=`rgba(11,102,255,${intensity})`; cell.textContent=`${(value*100).toFixed(1)}`; grid.appendChild(cell);
  });
  $('alerts').innerHTML = data.alerts.length ? data.alerts.map(a=>`<div class="alert ${a.level}">${a.message}</div>`).join('') : '<p>Operação normal. Nenhum alerta ativo.</p>';
}
async function latest(){try{const r=await fetch('/api/readings/latest');render(await r.json());$('connection').textContent='● BoxNode online';$('connection').style.color='#25d695'}catch{$('connection').textContent='● Sem conexão';$('connection').style.color='#ef5b67'}}
$('capture').onclick=async()=>{const r=await fetch('/api/readings',{method:'POST'});const data=await r.json();if(r.ok)render(data);else alert(data.message||'Falha na captura.');};
$('calibrate').onclick=async()=>{if(!confirm('O box está completamente vazio?'))return;await fetch('/api/calibration',{method:'POST'});alert('Calibração salva. Agora adicione a carga.');};
for(let i=0;i<64;i++){const c=document.createElement('div');c.className='cell';c.style.background='#d8e2ef';grid.appendChild(c)}
latest(); setInterval(latest,5000);

