<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Valuation Lab — Monte Carlo & Valuation Toolkit</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<style>
  :root{--bg:#f7fbff;--card:#fff;--muted:#6b7280;--accent:#0ea5a4}
  body{font-family:Inter,system-ui,Segoe UI,Roboto,Arial;margin:10px;background:var(--bg);color:#02203c}
  .wrap{max-width:980px;margin:0 auto}
  h1{font-size:20px;margin:0 0 8px}
  .card{background:var(--card);border-radius:12px;padding:14px;margin-bottom:12px;box-shadow:0 6px 20px rgba(2,6,23,0.06)}
  label{display:block;margin-top:8px;font-size:13px;color:var(--muted)}
  input, select, textarea, button{width:100%;padding:10px;border-radius:8px;border:1px solid #e6eef6;margin-top:6px;box-sizing:border-box}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .full{grid-column:1/-1}
  .actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
  button.primary{background:var(--accent);color:#fff;border:none;padding:9px 12px;border-radius:10px;cursor:pointer}
  button.alt{background:#6366f1;color:white}
  .small{font-size:12px;color:var(--muted)}
  table{width:100%;border-collapse:collapse}
  th,td{padding:8px;border-bottom:1px solid #eef2f7;font-size:13px;text-align:left}
  .kpi{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dashed #eef2f7}
  .row{display:flex;gap:8px;align-items:center}
  canvas{max-width:100%}
  .badge{background:#ecfeff;color:#065f46;padding:4px 8px;border-radius:999px;font-size:12px}
  .muted{color:var(--muted)}
  @media(max-width:720px){ .grid{grid-template-columns:1fr} body{margin:8px} }
</style>
</head>
<body>
<div class="wrap">
  <h1>🚀 Valuation Lab — Monte Carlo + Benchmarks</h1>
  <div class="small muted">Run scenarios, export charts/CSV, and get LinkedIn-ready visuals. (Educational tool.)</div>

  <div class="card">
    <strong>Base Inputs</strong>
    <div class="grid" style="margin-top:8px">
      <div><label>Stock name</label><input id="stockName" value="NSDL (demo)"></div>
      <div><label>Starting EPS (₹)</label><input id="startEPS" type="number" step="any" value="17.16"></div>
      <div><label>Buy / IPO price (₹)</label><input id="buyPrice" type="number" step="any" value="800"></div>
      <div><label>Target/base P/E</label><input id="targetPE" type="number" step="any" value="40"></div>
      <div><label>Inflation (annual %)</label><input id="inflation" type="number" step="any" value="5"></div>
      <div><label>Discount rate for DCF proxy (annual %)</label><input id="discountRate" type="number" step="any" value="10"></div>
      <div class="full"><label>Simulation length (years)</label><input id="yearsTotal" type="number" step="1" value="20"></div>

      <div class="full">
        <label>Growth periods — add rows (years, mean growth%, volatility%). Monte Carlo samples around mean using volatility (std dev).</label>
        <div id="periodContainer"></div>
        <div class="actions"><button id="addPeriodBtn" class="primary">+ Add period</button><button id="resetPeriodsBtn" class="alt">Reset demo</button></div>
      </div>

      <div><label>Shares owned</label><input id="sharesOwned" type="number" step="1" value="18"></div>
      <div><label>Lump-sum budget now (₹)</label><input id="lumpSum" type="number" step="any" value="0"></div>
      <div><label>Current price (empty = auto EPS×P/E)</label><input id="currentPrice" type="number" step="any" placeholder="auto if empty"></div>
      <div><label>Dividend payout % of EPS</label><input id="divPayout" type="number" step="any" value="25"></div>
      <div><label>Reinvest dividends?</label><select id="reinvestDiv"><option value="yes">Yes</option><option value="no">No</option></select></div>

      <div><label>Auto split/bonus events (comma list like 10:2,15:1.5)</label><input id="splitEvents" placeholder="e.g. 10:2,15:1.5"></div>
      <div><label>Monthly SIP amount (₹)</label><input id="sipMonthly" type="number" step="any" value="0"></div>
      <div><label>SIP frequency</label><select id="sipFreq"><option value="monthly">Monthly</option><option value="yearly">Yearly</option></select></div>

      <div><label>Monte Carlo sims</label><input id="mcSims" type="number" step="1" value="1000"></div>
      <div><label>Random seed (0 = random)</label><input id="mcSeed" type="number" step="1" value="0"></div>

      <div class="full">
        <label>Peer benchmarking (paste JSON array) — fields: name, pe, epsGrowth</label>
        <textarea id="peers" rows="3">[{"name":"Peer A","pe":35,"epsGrowth":12},{"name":"Peer B","pe":30,"epsGrowth":15}]</textarea>
        <div class="small muted">Example: [{"name":"Peer A","pe":35,"epsGrowth":12}]</div>
      </div>

    </div>

    <div class="actions" style="margin-top:12px">
      <button id="runBtn" class="primary">Run Analysis</button>
      <button id="downloadCSV" class="alt">Download CSV</button>
      <button id="downloadJSON">Download JSON</button>
      <button id="exportPNG">Open Charts (PNG)</button>
    </div>
  </div>

  <!-- outputs -->
  <div id="output" style="display:none">
    <div id="summaryCard" class="card"></div>
    <div id="chartsCard" class="card">
      <strong>Charts</strong>
      <div style="margin-top:8px"><canvas id="fanChart" height="220"></canvas></div>
      <div style="margin-top:12px"><canvas id="distChart" height="160"></canvas></div>
    </div>
    <div id="tableCard" class="card"><strong>Year-by-year percentiles</strong><div id="tableWrap" style="overflow:auto;margin-top:8px"></div></div>
    <div id="benchCard" class="card"><strong>Benchmark Summary</strong><div id="benchWrap"></div></div>
  </div>

  <div class="small muted" style="margin-top:8px">Tip: export PNG from charts and share on LinkedIn with a short caption about assumptions. Always state growth assumptions and payout %.</div>
</div>

<!-- Chart.js CDN (internet needed) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<script>
/* Utilities */
const el = id => document.getElementById(id);
const num = v => Number(v)||0;
const fmt = n => Number(n).toLocaleString(undefined,{maximumFractionDigits:2});
function rndSeeded(seed){
  let t = seed >>> 0;
  return function(){
    t += 0x6D2B79F5;
    let r = Math.imul(t ^ t >>> 15, 1 | t);
    r ^= r + Math.imul(r ^ r >>> 7, 61 | r);
    return ((r ^ r >>> 14) >>> 0) / 4294967296;
  }
}

/* Growth periods UI */
const periodContainer = el('periodContainer');
function addPeriodRow(years=10, mean=20, vol=6){
  const row = document.createElement('div'); row.style.display='grid';
  row.style.gridTemplateColumns='1fr 1fr 1fr auto'; row.style.gap='8px'; row.style.marginTop='6px';
  row.innerHTML = `<input class="py" type="number" value="${years}" /><input class="pm" type="number" step="any" value="${mean}" /><input class="pv" type="number" step="any" value="${vol}" /><button class="pdel" style="background:#fecaca;border:none;border-radius:8px;padding:8px">Remove</button>`;
  periodContainer.appendChild(row);
  row.querySelector('.pdel').onclick = ()=> row.remove();
}
function getPeriods(){
  const rows = periodContainer.querySelectorAll('div'); const out=[];
  rows.forEach(r=>{ const yrs = num(r.querySelector('.py').value); const mean = num(r.querySelector('.pm').value); const vol = num(r.querySelector('.pv').value); if(yrs>0) out.push({years:yrs,mean,vol}); });
  return out;
}
el('addPeriodBtn').onclick = ()=> addPeriodRow(5,10,6);
el('resetPeriodsBtn').onclick = ()=>{ periodContainer.innerHTML=''; addPeriodRow(10,20,8); addPeriodRow(10,10,4); };
el('resetPeriodsBtn').click();

/* Simulation + Outputs */
let lastResult=null; let fanChart=null, distChart=null;

function runAnalysis(){
  // inputs
  const stockName = el('stockName').value || 'Stock';
  const startEPS = num(el('startEPS').value);
  const yearsTotal = Math.max(1, Math.floor(num(el('yearsTotal').value)));
  const targetPE = num(el('targetPE').value);
  const inflation = num(el('inflation').value)/100;
  const discountRate = num(el('discountRate').value)/100;
  const buyPrice = num(el('buyPrice').value);
  const currentPriceInput = num(el('currentPrice').value);
  const currentPrice = currentPriceInput>0 ? currentPriceInput : startEPS * targetPE;
  const sharesOwned = Math.max(0, Math.floor(num(el('sharesOwned').value)));
  const lump = num(el('lumpSum').value);
  const divPayout = num(el('divPayout').value)/100;
  const reinvestDiv = el('reinvestDiv').value === 'yes';
  const sipMonthly = num(el('sipMonthly').value);
  const sipFreq = el('sipFreq').value;
  const mcSims = Math.max(100, Math.floor(num(el('mcSims').value)));
  const mcSeed = Math.floor(num(el('mcSeed').value));
  let peers=[]; try{ peers = JSON.parse(el('peers').value) }catch(e){ peers=[] }

  const periods = getPeriods();
  // build per-year params
  const yearParams=[]; let yrsAssigned=0;
  for(const p of periods){ for(let i=0;i<p.years && yrsAssigned<yearsTotal;i++){ yearParams.push({mean:p.mean/100, vol:p.vol/100}); yrsAssigned++; } }
  while(yearParams.length < yearsTotal) yearParams.push(yearParams[yearParams.length-1] || {mean:0.1,vol:0.1});

  const rng = (mcSeed===0) ? Math.random : rndSeeded(mcSeed);
  const sims=[];

  // Monte Carlo
  for(let s=0;s<mcSims;s++){
    let eps = startEPS; const epsPath=[eps];
    for(let y=0;y<yearsTotal;y++){
      const gp = yearParams[y];
      let u1 = rng() || 1e-9, u2 = rng() || 1e-9;
      const z0 = Math.sqrt(-2*Math.log(u1)) * Math.cos(2*Math.PI*u2);
      const sampled = gp.mean + gp.vol * z0;
      const gf = Math.max(-0.9999, sampled);
      eps = eps * (1+gf);
      epsPath.push(eps);
    }
    sims.push(epsPath);
  }

  // parse splits
  const splitText = el('splitEvents').value.trim(); const splitMap={};
  if(splitText){ splitText.split(',').forEach(tok=>{ const t=tok.trim(); if(!t) return; const parts=t.split(':').map(x=>x.trim()); if(parts.length===2){ const yr=Number(parts[0]); const ratio=Number(parts[1]); if(yr>0 && ratio>0) splitMap[yr]=ratio; } }); }

  const finalPrices=[], finalEPSs=[], pvVals=[], wealths=[];
  const sipYearly = sipFreq === 'monthly' ? sipMonthly * 12 : sipMonthly;

  for(const epsPath of sims){
    const yearlyPrices = epsPath.map(eps => eps * targetPE);
    let shares = sharesOwned;
    if(lump > 0) shares += Math.floor(lump / currentPrice);
    let cashDivs=0, pvSum=0;
    for(let y=1;y<yearlyPrices.length;y++){
      const eps = epsPath[y], price = yearlyPrices[y];
      const divPerShare = eps * divPayout;
      const divThisYear = shares * divPerShare;
      cashDivs += divThisYear;
      if(reinvestDiv && price>0){ const buyNow = Math.floor(divThisYear / price); shares += buyNow; }
      if(sipYearly>0){ const buyFromSip = Math.floor(sipYearly / price); shares += buyFromSip; }
      if(splitMap[y]) shares *= splitMap[y];
      pvSum += (price * shares) / Math.pow(1+discountRate, y);
    }
    const finalPrice = yearlyPrices[yearlyPrices.length-1];
    const finalEPS = epsPath[epsPath.length-1];
    finalPrices.push(finalPrice); finalEPSs.push(finalEPS); pvVals.push(pvSum); wealths.push(finalPrice * shares + cashDivs);
  }

  // stats & percentiles
  function percentile(arr,p){ if(arr.length===0) return 0; const a=arr.slice().sort((x,y)=>x-y); const idx=(p/100)*(a.length-1); const lo=Math.floor(idx), hi=Math.ceil(idx), t=idx-lo; return a[lo]*(1-t)+a[hi]*t; }
  const stats = {
    finalPriceP10: percentile(finalPrices,10),
    finalPriceP25: percentile(finalPrices,25),
    finalPriceMedian: percentile(finalPrices,50),
    finalPriceP75: percentile(finalPrices,75),
    finalPriceP90: percentile(finalPrices,90),
    finalEPSMedian: percentile(finalEPSs,50),
    finalWealthP50: percentile(wealths,50),
    probAbove2x: finalPrices.filter(v=>v >= 2 * currentPrice).length / finalPrices.length,
    probAbove5x: finalPrices.filter(v=>v >= 5 * currentPrice).length / finalPrices.length
  };
  const avgPV = pvVals.reduce((a,b)=>a+b,0)/pvVals.length;
  const medianFinal = stats.finalPriceMedian;
  const nominalCagr = Math.pow(medianFinal / currentPrice, 1/yearsTotal) - 1;
  const realCagr = Math.pow((medianFinal / Math.pow(1+inflation, yearsTotal)) / currentPrice, 1/yearsTotal) - 1;
  const meanFinal = finalPrices.reduce((a,b)=>a+b,0)/finalPrices.length;
  const sdFinal = Math.sqrt(finalPrices.reduce((a,b)=>a + Math.pow(b-meanFinal,2),0)/finalPrices.length);
  const reward = medianFinal / currentPrice;
  const score = Math.max(0, Math.min(100, Math.round((Math.log10(Math.max(1,reward))*40) - (sdFinal/Math.max(1,meanFinal))*10 + 50)));

  // year percentiles for fan chart
  const yearPercentiles = [];
  for(let y=0;y<=yearsTotal;y++){
    const vals = sims.map(s=> s[y] * targetPE );
    yearPercentiles.push({ year:y, p10:percentile(vals,10), p25:percentile(vals,25), p50:percentile(vals,50), p75:percentile(vals,75), p90:percentile(vals,90) });
  }

  // benchmarks
  const benchSummary = (peers || []).map(p=>{
    const fairPrice = startEPS * (p.pe||0) * Math.pow(1+(p.epsGrowth||0)/100, yearsTotal);
    return {...p, fairPrice};
  });

  lastResult = { meta:{stockName, startEPS, currentPrice, targetPE, yearsTotal, mcSims}, stats, yearPercentiles, peers:benchSummary, finalPrices, finalEPSs, pvVals, wealths, nominalCagr, realCagr, score };

  renderOutputs();
}

/* Render outputs */
function renderOutputs(){
  if(!lastResult) return;
  el('output').style.display='block';
  const res = lastResult; const s = res.stats;
  el('summaryCard').innerHTML = `
    <div class="row"><div><strong>${res.meta.stockName}</strong> <span class="badge">MC ${res.meta.mcSims} sims</span></div></div>
    <div class="kpi"><div class="muted">Median projected price</div><div><strong>₹ ${fmt(s.finalPriceMedian)}</strong></div></div>
    <div class="kpi"><div class="muted">10th / 90th percentile</div><div>₹ ${fmt(s.finalPriceP10)} / ₹ ${fmt(s.finalPriceP90)}</div></div>
    <div class="kpi"><div class="muted">Median EPS (est)</div><div>₹ ${fmt(s.finalEPSMedian)}</div></div>
    <div class="kpi"><div class="muted">Median final wealth</div><div>₹ ${fmt(s.finalWealthP50)}</div></div>
    <div class="kpi"><div class="muted">Prob ≥2× price</div><div>${(s.probAbove2x*100).toFixed(1)}%</div></div>
    <div class="kpi"><div class="muted">Prob ≥5× price</div><div>${(s.probAbove5x*100).toFixed(1)}%</div></div>
    <div class="kpi"><div class="muted">DCF-ish avg PV</div><div>₹ ${fmt(res.pvVals.reduce((a,b)=>a+b,0)/res.pvVals.length)}</div></div>
    <div class="kpi"><div class="muted">Nominal CAGR</div><div>${(res.nominalCagr*100).toFixed(2)}%</div></div>
    <div class="kpi"><div class="muted">Real CAGR</div><div>${(res.realCagr*100).toFixed(2)}%</div></div>
    <div class="kpi"><div class="muted">Risk-Reward Score</div><div><strong>${res.score}</strong></div></div>
  `;

  // bench table
  const bw = el('benchWrap'); bw.innerHTML='';
  if(res.peers && res.peers.length){
    const t=document.createElement('table'); t.innerHTML='<thead><tr><th>Peer</th><th>PE</th><th>EPS growth%</th><th>Proxy fair price</th></tr></thead>';
    const tb=document.createElement('tbody');
    res.peers.forEach(p=>{ const tr=document.createElement('tr'); tr.innerHTML=`<td>${p.name}</td><td>${p.pe}</td><td>${p.epsGrowth}</td><td>₹ ${fmt(p.fairPrice)}</td>`; tb.appendChild(tr); });
    t.appendChild(tb); bw.appendChild(t);
  } else bw.innerHTML = '<div class="small muted">No peers provided.</div>';

  // table percentiles
  const tw = el('tableWrap'); tw.innerHTML='';
  const table=document.createElement('table');
  const thead=document.createElement('thead'); thead.innerHTML='<tr><th>Year</th><th>P10</th><th>P25</th><th>Median</th><th>P75</th><th>P90</th></tr>'; table.appendChild(thead);
  const tbody=document.createElement('tbody');
  res.yearPercentiles.forEach(y=>{ const tr=document.createElement('tr'); tr.innerHTML=`<td>${y.year}</td><td>₹ ${fmt(y.p10)}</td><td>₹ ${fmt(y.p25)}</td><td>₹ ${fmt(y.p50)}</td><td>₹ ${fmt(y.p75)}</td><td>₹ ${fmt(y.p90)}</td>`; tbody.appendChild(tr); });
  table.appendChild(tbody); tw.appendChild(table);

  // charts
  const labels = res.yearPercentiles.map(y=> y.year + 'y');
  const med = res.yearPercentiles.map(y=> y.p50);
  const p10 = res.yearPercentiles.map(y=> y.p10);
  const p25 = res.yearPercentiles.map(y=> y.p25);
  const p75 = res.yearPercentiles.map(y=> y.p75);
  const p90 = res.yearPercentiles.map(y=> y.p90);

  if(fanChart) fanChart.destroy();
  if(distChart) distChart.destroy();

  const ctx = el('fanChart').getContext('2d');
  fanChart = new Chart(ctx, {
    type:'line',
    data:{ labels, datasets:[
      {label:'P90', data:p90, borderColor:'rgba(99,102,241,0.25)', borderWidth:1, fill:'+1', pointRadius:0, tension:0.35},
      {label:'P75', data:p75, borderColor:'rgba(34,197,94,0.2)', borderWidth:1, fill:'+1', pointRadius:0, tension:0.35},
      {label:'Median', data:med, borderColor:'rgba(2,6,23,0.9)', borderWidth:2, fill:false, pointRadius:2, tension:0.35},
      {label:'P25', data:p25, borderColor:'rgba(34,197,94,0.2)', borderWidth:1, fill:'-1', pointRadius:0, tension:0.35},
      {label:'P10', data:p10, borderColor:'rgba(99,102,241,0.25)', borderWidth:1, fill:'-1', pointRadius:0, tension:0.35},
    ]},
    options:{ plugins:{ legend:{display:true,position:'bottom'}, tooltip:{mode:'index',intersect:false} }, scales:{ y:{ beginAtZero:false } } }
  });

  // histogram of final prices
  const finals = res.finalPrices;
  const nBuckets = 30; const min = Math.min(...finals), max = Math.max(...finals), step=(max-min)/nBuckets || 1;
  const buckets = new Array(nBuckets).fill(0), labels2=[];
  for(let i=0;i<nBuckets;i++) labels2.push(Math.round(min + i*step));
  finals.forEach(v=>{ const idx = Math.min(nBuckets-1, Math.floor((v-min)/Math.max(1e-9,step))); buckets[idx]++; });
  const ctx2 = el('distChart').getContext('2d');
  distChart = new Chart(ctx2, { type:'bar', data:{labels:labels2, datasets:[{label:'Frequency', data:buckets, backgroundColor:'rgba(99,102,241,0.7)'}]}, options:{ plugins:{ legend:{display:false} } } });
}

/* Exports */
el('runBtn').onclick = ()=>{ runAnalysis(); };
el('downloadCSV').onclick = ()=>{
  if(!lastResult){ alert('Run analysis first'); return; }
  const rows=[['year','p10','p25','p50','p75','p90']];
  lastResult.yearPercentiles.forEach(y=> rows.push([y.year,y.p10,y.p25,y.p50,y.p75,y.p90]));
  const csv = rows.map(r=> r.join(',')).join('\\n');
  const blob = new Blob([csv], {type:'text/csv'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='valuation_percentiles.csv'; a.click(); URL.revokeObjectURL(url);
};
el('downloadJSON').onclick = ()=>{
  if(!lastResult){ alert('Run analysis first'); return; }
  const blob = new Blob([JSON.stringify(lastResult,null,2)], {type:'application/json'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='valuation_mc.json'; a.click(); URL.revokeObjectURL(url);
};
el('exportPNG').onclick = ()=>{
  if(!lastResult){ alert('Run analysis first'); return; }
  const c1 = el('fanChart').toDataURL('image/png'); const c2 = el('distChart').toDataURL('image/png');
  window.open(c1); window.open(c2);
};

/* quick hint on first load */
if(!localStorage.getItem('vl_seen')){ localStorage.setItem('vl_seen','1'); setTimeout(()=> alert('Tip: run with demo defaults, then export PNG for LinkedIn. Add peers JSON to compare.'),600); }
</script>
</body>
</html>
