"""
build_dashboard.py — Assembly-only builder.
Reads raw text from 데이터/ folder and inlines into HTML template.
NO data parsing, mapping, KPI/return/MDD calculation here.
All analysis runs in browser JavaScript.
"""
import os
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "데이터")
OUT_PATH = os.path.join(ROOT, "investment_dashboard.html")


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def safe(s):
    # </script> escape so embedded raw text cannot terminate the script tag
    return s.replace("</", "<\\/")


# ── Step 1: Read raw files (no parsing) ────────────────────────────────────
market_data_raw = read_text(os.path.join(DATA_DIR, "market_data.json"))
financial_index_raw = read_text(os.path.join(DATA_DIR, "financial_index.json"))
sector_targets_raw = read_text(os.path.join(DATA_DIR, "sector_targets.json"))
consensus_raw = read_text(os.path.join(DATA_DIR, "consensus_data.json"))

etf_holdings = {}
for name in os.listdir(DATA_DIR):
    if name.startswith("etf_holdings_") and name.endswith(".csv"):
        code6 = name.replace("etf_holdings_", "").replace(".csv", "")
        # Step 2.5: collection key must match market_data ticker key form ({6}.KS)
        key = f"{code6}.KS"
        etf_holdings[key] = read_text(os.path.join(DATA_DIR, name))

# Build CSV-as-JS-object literal (raw text only, JS will parse)
holdings_js_obj = "{" + ",".join(
    f"{json.dumps(k)}: {json.dumps(v)}" for k, v in etf_holdings.items()
) + "}"

# ── Step 2: Template ───────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>RoleMap 투자 대시보드</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#0D1117;--card:#161B22;--border:#30363D;--text:#E6EDF3;--mute:#8B949E;
  --green:#1D9E75;--red:#E24B4A;--gold:#C8963E;--teal:#3A9E9E;--gray:#888780;
  --fs-xs:10px;--fs-sm:11px;--fs-base:13px;--fs-md:14px;--fs-lg:18px;--fs-xl:22px;
  --sp-xs:4px;--sp-sm:8px;--sp-md:12px;--sp-lg:16px;--sp-xl:24px;
  --r-sm:4px;--r-md:6px;--r-lg:8px;--r-pill:12px;--r-round:20px;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:var(--fs-base)/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif;}
header{padding:var(--sp-lg) var(--sp-xl);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:var(--sp-lg);}
header h1{margin:0;font-size:var(--fs-lg);}
.spacer{flex:1}
.date-badge{color:var(--mute);font-size:var(--fs-sm);}
.tabs{display:flex;gap:0;border-bottom:1px solid var(--border);padding:0 var(--sp-xl);}
.tab{padding:var(--sp-md) var(--sp-lg);cursor:pointer;color:var(--mute);border-bottom:2px solid transparent;}
.tab.active{color:var(--text);border-bottom-color:var(--teal);}
.period-toggle{display:flex;gap:4px;background:var(--card);padding:4px;border-radius:var(--r-round);}
.period-btn{padding:4px 10px;cursor:pointer;border-radius:var(--r-round);color:var(--mute);font-size:var(--fs-sm);border:none;background:transparent;}
.period-btn.active{background:var(--teal);color:#fff;}
.view{padding:var(--sp-xl);display:none;}
.view.active{display:block;}
.row{display:grid;gap:var(--sp-lg);margin-bottom:var(--sp-lg);}
.row.r3{grid-template-columns:repeat(3,1fr);}
.row.r2{grid-template-columns:repeat(2,1fr);}
.row.kpi{grid-template-columns:repeat(5,1fr);}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r-lg);padding:var(--sp-md);}
.card h3{margin:0 0 var(--sp-sm);font-size:var(--fs-md);color:var(--mute);font-weight:400;}
.kpi-card .label{color:var(--mute);font-size:var(--fs-sm);}
.kpi-card .value{font-size:var(--fs-xl);font-weight:600;margin-top:var(--sp-xs);}
.kpi-card .sub{font-size:var(--fs-xs);color:var(--mute);margin-top:2px;}
.kpi-card.warn{border-color:var(--gold);}
.kpi-card.danger{border-color:var(--red);}
.green{color:var(--green);} .red{color:var(--red);} .gold{color:var(--gold);} .teal{color:var(--teal);} .mute{color:var(--mute);}
.dropdown-row{display:flex;align-items:center;gap:var(--sp-md);margin-bottom:var(--sp-lg);}
select,input[type=text]{background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:var(--r-md);padding:6px 10px;font-size:var(--fs-base);}
.badge{display:inline-block;padding:2px 8px;border-radius:var(--r-pill);font-size:var(--fs-xs);font-weight:600;}
.badge-passive{background:rgba(58,158,158,0.15);color:var(--teal);}
.badge-theme{background:rgba(200,150,62,0.15);color:var(--gold);}
.badge-buy{background:rgba(29,158,117,0.18);color:var(--green);}
.badge-hold{background:rgba(136,135,128,0.18);color:var(--gray);}
.badge-sell{background:rgba(226,75,74,0.18);color:var(--red);}
.badge-na{background:rgba(136,135,128,0.10);color:var(--mute);}
.badge-foreign{background:rgba(136,135,128,0.15);color:var(--mute);}
.banner{display:flex;flex-wrap:wrap;gap:var(--sp-sm);margin-bottom:var(--sp-lg);}
.banner-item{padding:8px 12px;border-radius:var(--r-md);background:var(--card);border-left:3px solid var(--teal);font-size:var(--fs-sm);}
.banner-item.r{border-left-color:var(--red);}
.banner-item.g{border-left-color:var(--gold);}
.banner-item.gn{border-left-color:var(--green);}
table{width:100%;border-collapse:collapse;font-size:var(--fs-sm);}
th,td{padding:6px 8px;text-align:right;border-bottom:1px solid var(--border);}
th:first-child,td:first-child{text-align:left;}
th{color:var(--mute);font-weight:400;}
tr:hover{background:rgba(255,255,255,0.02);}
tr.row-warn{background:rgba(200,150,62,0.06);}
.cell-low{color:var(--green);} .cell-high{color:var(--red);}
.chart-box{position:relative;height:240px;}
.chart-box.compact{height:200px;}
.chart-box.spark{height:50px;}
.risk-grid{display:grid;grid-template-columns:1fr 1fr;gap:var(--sp-sm);}
.risk-cell{background:rgba(255,255,255,0.02);padding:var(--sp-sm);border-radius:var(--r-sm);}
.risk-cell .lab{font-size:var(--fs-xs);color:var(--mute);}
.risk-cell .v{font-size:var(--fs-md);font-weight:600;margin-top:2px;}
.stock-header{display:flex;align-items:center;gap:var(--sp-md);background:var(--card);border:1px solid var(--border);border-radius:var(--r-lg);padding:var(--sp-md);margin-bottom:var(--sp-md);}
.stock-header .name{font-size:var(--fs-lg);font-weight:600;}
.stock-header .ticker-tag{font-size:var(--fs-sm);color:var(--mute);}
.peer-chips{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap;}
.peer-chip{padding:2px 8px;border-radius:var(--r-pill);background:rgba(58,158,158,0.10);color:var(--teal);font-size:var(--fs-xs);cursor:pointer;}
.kpi-grid-note{font-size:var(--fs-sm);color:var(--mute);margin-bottom:var(--sp-sm);}
.progress{background:rgba(255,255,255,0.05);border-radius:var(--r-sm);height:8px;overflow:hidden;margin-top:4px;}
.progress > i{display:block;height:100%;background:var(--teal);}
.fin-row{margin-bottom:var(--sp-sm);}
.fin-row .top{display:flex;justify-content:space-between;font-size:var(--fs-sm);}
.signal-list{list-style:none;padding:0;margin:0;}
.signal-list li{padding:6px 8px;border-radius:var(--r-sm);margin-bottom:4px;font-size:var(--fs-sm);background:rgba(255,255,255,0.02);}
.signal-list li.r{border-left:3px solid var(--red);}
.signal-list li.g{border-left:3px solid var(--gold);}
.signal-list li.gn{border-left:3px solid var(--green);}
.insight-panel{padding:var(--sp-md);}
.insight-panel.green{border-top:3px solid var(--green);}
.insight-panel.red{border-top:3px solid var(--red);}
.insight-panel.gold{border-top:3px solid var(--gold);}
.insight-panel.teal{border-top:3px solid var(--teal);}
.insight-panel.gray{border-top:3px solid var(--gray);}
#debug-toggle{position:fixed;bottom:16px;right:16px;background:var(--teal);color:#fff;border:none;border-radius:var(--r-pill);padding:8px 14px;cursor:pointer;font-size:var(--fs-sm);z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,0.4);}
#debug-panel{position:fixed;bottom:60px;right:16px;width:360px;max-height:60vh;overflow:auto;background:var(--card);border:1px solid var(--border);border-radius:var(--r-lg);padding:var(--sp-md);font:var(--fs-sm)/1.5 Consolas,monospace;display:none;z-index:9999;box-shadow:0 8px 24px rgba(0,0,0,0.5);}
#debug-panel.open{display:block;}
#debug-panel h4{margin:8px 0 4px;color:var(--mute);font-size:var(--fs-sm);text-transform:uppercase;letter-spacing:.5px;}
.tag-foreign{font-size:var(--fs-xs);color:var(--mute);margin-left:4px;}
</style>
</head>
<body>
<header>
  <h1>📊 RoleMap 투자 대시보드</h1>
  <span class="date-badge">한국 ETF + KOSPI 보유종목</span>
  <span class="spacer"></span>
  <div class="period-toggle" id="period-toggle-global">
    <button class="period-btn active" data-p="ytd">YTD</button>
    <button class="period-btn" data-p="1m">1M</button>
    <button class="period-btn" data-p="3m">3M</button>
    <button class="period-btn" data-p="1y">1Y</button>
  </div>
</header>
<div class="tabs">
  <div class="tab active" data-tab="pm">PM 뷰</div>
  <div class="tab" data-tab="ra">RA 뷰</div>
</div>

<section class="view active" id="view-pm">
  <div class="dropdown-row">
    <label class="mute">ETF</label>
    <select id="etf-select"></select>
    <span id="etf-type-badge"></span>
  </div>
  <div class="row kpi" id="pm-kpi"></div>
  <div class="banner" id="pm-banner"></div>
  <div class="row r3">
    <div class="card"><h3 id="pm-line-title">누적 수익률 vs 벤치마크 (YTD)</h3><div class="chart-box"><canvas id="pm-line"></canvas></div></div>
    <div class="card"><h3>구성종목 배분 (현재 기준)</h3><div class="chart-box"><canvas id="pm-donut"></canvas></div></div>
    <div class="card"><h3>리스크 모니터링 (전체기간)</h3>
      <div class="risk-grid" id="pm-risk-grid"></div>
      <div style="margin-top:8px;">
        <div class="lab mute" style="font-size:var(--fs-xs)">롤링 변동성 (30D)</div>
        <div class="chart-box spark"><canvas id="pm-spark"></canvas></div>
      </div>
    </div>
  </div>
  <div class="card" id="pm-bottom-panel"></div>
  <div class="card" style="margin-top:var(--sp-lg)"><h3>보유종목</h3>
    <div style="overflow:auto"><table id="pm-table"></table></div>
  </div>
</section>

<section class="view" id="view-ra">
  <div class="dropdown-row">
    <label class="mute">종목 검색</label>
    <input type="text" id="ra-search" placeholder="종목명 검색…" style="width:180px;">
    <select id="ra-select"></select>
  </div>
  <div id="ra-header" class="stock-header"></div>
  <div class="kpi-grid-note">펀더멘털 지표는 최신 공시 기준</div>
  <div class="row kpi" id="ra-kpi"></div>
  <div class="banner" id="ra-banner"></div>
  <div class="row r2">
    <div class="card">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:var(--sp-sm);gap:var(--sp-md);">
        <h3 id="ra-price-title" style="margin:0;">주가 추이 vs 목표주가 (YTD)</h3>
        <div class="period-toggle" id="period-toggle-ra">
          <button class="period-btn active" data-p="ytd">YTD</button>
          <button class="period-btn" data-p="1m">1M</button>
          <button class="period-btn" data-p="3m">3M</button>
          <button class="period-btn" data-p="1y">1Y</button>
        </div>
      </div>
      <div class="chart-box"><canvas id="ra-price"></canvas></div>
    </div>
    <div class="card" id="ra-surprise-card"><h3>어닝 서프라이즈 히스토리 (최신 공시 기준)</h3><div class="chart-box"><canvas id="ra-surprise"></canvas></div></div>
  </div>
  <div class="row r3">
    <div class="card"><h3>분기 실적 (최신 공시 기준)</h3><div class="chart-box"><canvas id="ra-quarterly"></canvas></div></div>
    <div class="card"><h3>피어 밸류에이션 비교 (최신 공시 기준)</h3><div id="ra-peer"></div></div>
    <div class="card"><h3>재무 건전성 (최신 공시 기준)</h3><div id="ra-fin"></div></div>
  </div>
  <div class="row r3" id="ra-insights"></div>
</section>

<button id="debug-toggle">🔍 매핑 상태</button>
<div id="debug-panel"></div>

<script id="data-market" type="application/json">__MARKET__</script>
<script id="data-fin" type="application/json">__FIN__</script>
<script id="data-sec" type="application/json">__SEC__</script>
<script id="data-cons" type="application/json">__CONS__</script>
<script>window.__HOLDINGS_RAW__ = __HOLDINGS__;</script>
<script>
'use strict';
// ── Parse inlined raw data in browser ──────────────────────────────────────
const MD = JSON.parse(document.getElementById('data-market').textContent);
const FIN = JSON.parse(document.getElementById('data-fin').textContent);
const SEC = JSON.parse(document.getElementById('data-sec').textContent);
const CONS = JSON.parse(document.getElementById('data-cons').textContent);
const HOLDINGS_RAW = window.__HOLDINGS_RAW__;

// Parse CSV → array of objects
function parseCSV(text){
  text = text.replace(/^﻿/, '');
  const lines = text.split(/\r?\n/).filter(l=>l.trim());
  const header = lines[0].split(',').map(s=>s.trim());
  return lines.slice(1).map(line=>{
    const cols = line.split(',').map(s=>s.trim());
    const o = {};
    header.forEach((h,i)=>{ o[h] = cols[i] === '' ? null : cols[i]; });
    return o;
  });
}
const HOLDINGS = {};
for (const k in HOLDINGS_RAW){ HOLDINGS[k] = parseCSV(HOLDINGS_RAW[k]); }

// ── Dataset meta (current-dataset.md) ──────────────────────────────────────
const ETF_META = {
  '423920.KS':{name:'TIGER 미국필라델피아반도체나스닥', bench:'^SOX', type:'passive'},
  '412570.KS':{name:'TIGER 2차전지테마', bench:'^KQ11', type:'theme'},
  '123320.KS':{name:'TIGER 코스피200', bench:'^KS200', type:'passive'},
  '243880.KS':{name:'TIGER 반도체', bench:'^KS200', type:'passive'},
};
const RA_DEFAULT = '006400.KS';
const PM_DEFAULT = '423920.KS';
const ETF_KEYWORDS = ['TIGER','KODEX','KINDEX','HANARO','ARIRANG','KOSEF','FOCUS','SOL','ACE','TREX','TIMEFOLIO','Invesco','iShares','SPDR','ETF'];
const BROKEN_NAME_RE = /^[0-9A-Z.]+,[A-Za-z0-9]+,\d+/;

// ── Step 0: Fast Path / Fallback detection ─────────────────────────────────
const fitCheck = (() => {
  const reasons = [];
  const expected = Object.keys(ETF_META);
  const missing = expected.filter(t=>!MD.tickers[t]);
  if (missing.length) reasons.push('missing ETFs: '+missing.join(','));
  for (const code in HOLDINGS){
    const rows = HOLDINGS[code]; if(!rows.length) continue;
    const yt = rows[0].yfinance_ticker || '';
    const sample = Object.keys(MD.tickers)[0];
    if (yt && (yt.includes('.') !== sample.includes('.'))) {
      reasons.push('ticker format mismatch in '+code); break;
    }
  }
  const sample = Object.values(MD.tickers)[0] || {};
  ['history','fundamentals'].forEach(k=>{ if(!(k in sample)) reasons.push('schema missing: '+k); });
  ['^SOX','^KQ11','^KS200'].forEach(b=>{ if(!MD.benchmarks?.[b]) reasons.push('missing benchmark: '+b); });
  return {fit:reasons.length===0, reasons, path:reasons.length===0?'fast-path':'fallback'};
})();
console.log(`[role-map] PATH=${fitCheck.path}`, fitCheck.fit?'(current-dataset.md 일치)':`(reason: ${fitCheck.reasons.join('; ')})`);
console.log('[role-map] close_role  ← current_price (market_data.json)');
console.log('[role-map] weight_role ← weight_pct    (etf_holdings_*.csv)');
console.log('[role-map] per_role    ← per_fwd       (market_data.json)');
console.log('[role-map] target_price_role ← target_price (market_data.json)');

// ── State ──────────────────────────────────────────────────────────────────
let state = { period:'ytd', tab:'pm', etf:PM_DEFAULT, stock:RA_DEFAULT };

// ── Helpers ────────────────────────────────────────────────────────────────
const fmtPct = (v, sign=true, dec=2) => v==null||isNaN(v) ? '—' : (sign && v>0?'+':'') + v.toFixed(dec) + '%';
const fmtNum = (v, dec=2) => v==null||isNaN(v) ? '—' : v.toFixed(dec);
const fmtKRW = v => v==null||isNaN(v) ? '—' : Math.round(v).toLocaleString('ko-KR') + '원';
const fmtEok = v => v==null||isNaN(v) ? '—' : Math.round(v/1e8).toLocaleString('ko-KR') + '억원';

function periodSlice(history, period){
  if (!history || !history.length) return [];
  if (period==='ytd'){
    const y = new Date().getFullYear();
    const idx = history.findIndex(h => h.date >= `${y}-01-01`);
    return idx<0 ? history.slice(-21) : history.slice(idx);
  }
  const map={'1m':21,'3m':63,'1y':252};
  return history.slice(-map[period]);
}
function returnPct(slice){
  if(slice.length<2) return null;
  const a=slice[0].close, b=slice[slice.length-1].close;
  return (b-a)/a*100;
}
function calcMDD(history){
  if(!history||!history.length) return null;
  let peak=history[0].close, mdd=0;
  for(const h of history){ if(h.close>peak)peak=h.close; const dd=(h.close-peak)/peak*100; if(dd<mdd)mdd=dd; }
  return mdd;
}
function dailyRets(history){
  const r=[]; for(let i=1;i<history.length;i++){ r.push((history[i].close-history[i-1].close)/history[i-1].close); } return r;
}
function std(arr){
  if(!arr.length) return null;
  const m=arr.reduce((s,v)=>s+v,0)/arr.length;
  return Math.sqrt(arr.reduce((s,v)=>s+(v-m)**2,0)/arr.length);
}
function cov(a,b){
  const n=Math.min(a.length,b.length); if(n<2) return null;
  const ma=a.slice(0,n).reduce((s,v)=>s+v,0)/n, mb=b.slice(0,n).reduce((s,v)=>s+v,0)/n;
  let c=0; for(let i=0;i<n;i++) c+=(a[i]-ma)*(b[i]-mb); return c/n;
}
function alignByDate(a,b){
  const mb={}; b.forEach(x=>mb[x.date]=x.close);
  const A=[], B=[];
  a.forEach(x=>{ if(mb[x.date]!=null){ A.push({date:x.date,close:x.close}); B.push({date:x.date,close:mb[x.date]}); } });
  return [A,B];
}
function trackingError(etfHist, benchHist){
  const [a,b] = alignByDate(etfHist, benchHist);
  const ra=dailyRets(a), rb=dailyRets(b);
  const diff=[]; for(let i=0;i<Math.min(ra.length,rb.length);i++) diff.push(ra[i]-rb[i]);
  const s=std(diff); return s==null?null:s*Math.sqrt(252)*100;
}
function beta(etfHist, benchHist){
  const [a,b] = alignByDate(etfHist, benchHist);
  if(a.length<30) return null;
  const ra=dailyRets(a), rb=dailyRets(b);
  const c=cov(ra,rb), v=std(rb); if(c==null||v==null) return null;
  return c/(v*v);
}
function var95(history){
  const r=dailyRets(history).sort((x,y)=>x-y); if(!r.length) return null;
  return r[Math.floor(r.length*0.05)]*100;
}
function annVol(history){
  const r=dailyRets(history); const s=std(r); return s==null?null:s*Math.sqrt(252)*100;
}
function rollingVol(history, win=30){
  const r=dailyRets(history); const out=[];
  for(let i=win;i<=r.length;i++){ const w=r.slice(i-win,i); const s=std(w); out.push({date:history[i].date, v: s==null?null:s*Math.sqrt(252)*100}); }
  return out;
}
function sharpe(history, vol1y){
  const r=dailyRets(history); if(r.length<2) return null;
  const annR = (r.reduce((s,v)=>s+v,0)/r.length)*252*100;
  const v = (vol1y!=null) ? vol1y : annVol(history);
  if(v==null||v===0) return null;
  return (annR-3.5)/v;
}
function periodReturnFromHistory(history, period){
  return returnPct(periodSlice(history, period));
}
function periodReturnFromReturns(returns, period){
  if(!returns) return null;
  const k = {ytd:'ytd','1m':'1m','3m':'3m','1y':'1y'}[period];
  let v = returns[k];
  if (v==null && period==='ytd') v = returns['1m'];
  return v==null?null:v;
}

// ── ETF type detection ────────────────────────────────────────────────────
function etfType(code){ return ETF_META[code]?.type || 'theme'; }

// ── PM rendering ──────────────────────────────────────────────────────────
let charts = {};
function destroyChart(id){ if(charts[id]){ charts[id].destroy(); delete charts[id]; } }

function periodLabel(p){ return ({ytd:'YTD','1m':'1M','3m':'3M','1y':'1Y'})[p]; }

function renderPM(){
  const code = state.etf;
  const meta = ETF_META[code] || {name:code, bench:null, type:'theme'};
  const t = MD.tickers[code]; if(!t) return;
  const period = state.period;

  // type badge
  const tb = document.getElementById('etf-type-badge');
  tb.className = ''; tb.innerHTML = '';
  if (meta.type==='passive') tb.innerHTML = '<span class="badge badge-passive">📌 패시브</span>';
  else tb.innerHTML = '<span class="badge badge-theme">🎯 테마형</span>';

  // KPI
  const ret = periodReturnFromReturns(t.returns, period);
  const holdings = HOLDINGS[code] || [];
  const aum = holdings.reduce((s,h)=>s+(parseFloat(h.market_value_krw)||0),0);
  const sh = sharpe(t.history, t.volatility_1y);
  const mdd = calcMDD(t.history);
  const bench = meta.bench ? MD.benchmarks[meta.bench] : null;
  const te = bench ? trackingError(t.history, bench.history) : null;

  function kpi(label, value, cls=''){
    return `<div class="card kpi-card ${cls}"><div class="label">${label}</div><div class="value">${value}</div></div>`;
  }
  const mddCls = mdd==null?'': (mdd<-15?'danger':(mdd<-5?'warn':''));
  const shCls = sh==null?'': (sh>1?'green':(sh<0?'red':''));
  const teCls = te==null?'': (te<2?'green':(te>4?'gold':''));

  document.getElementById('pm-kpi').innerHTML =
    kpi(`수익률 (${periodLabel(period)})`, `<span class="${ret>0?'green':(ret<0?'red':'')}">${fmtPct(ret)}</span>`) +
    kpi('총 AUM (현재)', fmtEok(aum)) +
    kpi('Sharpe (1Y)', `<span class="${shCls}">${fmtNum(sh)}</span>`) +
    kpi('MDD (전체기간)', `<span class="${mdd<0?'red':''}">${fmtPct(mdd)}</span>`, mddCls) +
    kpi('트래킹에러 (1Y)', `<span class="${teCls}">${te==null?'—':te.toFixed(2)+'%'}</span>`);

  // Banner
  renderBannerPM(t, holdings, mdd, bench);

  // Line chart
  document.getElementById('pm-line-title').textContent = `누적 수익률 vs 벤치마크 (${periodLabel(period)})`;
  const eSlice = periodSlice(t.history, period);
  const bSlice = bench ? periodSlice(bench.history, period) : [];
  const cumPct = arr => { if(!arr.length) return []; const a0=arr[0].close; return arr.map(x=>(x.close-a0)/a0*100); };
  destroyChart('pm-line');
  charts['pm-line'] = new Chart(document.getElementById('pm-line').getContext('2d'),{
    type:'line', data:{
      labels: eSlice.map(x=>x.date),
      datasets:[
        {label:meta.name, data:cumPct(eSlice), borderColor:'#3A9E9E', borderWidth:2, pointRadius:0, tension:.1},
        ...(bSlice.length?[{label:meta.bench, data:cumPct(bSlice), borderColor:'#888780', borderWidth:1, borderDash:[5,5], pointRadius:0}]:[])
      ]
    }, options:chartOpts(true)
  });

  // Donut
  const top = [...holdings].sort((a,b)=>(parseFloat(b.weight_pct)||0)-(parseFloat(a.weight_pct)||0));
  const top7 = top.slice(0,7);
  const otherSum = top.slice(7).reduce((s,h)=>s+(parseFloat(h.weight_pct)||0),0);
  destroyChart('pm-donut');
  charts['pm-donut'] = new Chart(document.getElementById('pm-donut').getContext('2d'),{
    type:'doughnut', data:{
      labels:[...top7.map(h=>h.name||h.ticker), ...(otherSum>0?['기타']:[])],
      datasets:[{data:[...top7.map(h=>parseFloat(h.weight_pct)||0), ...(otherSum>0?[otherSum]:[])],
        backgroundColor:['#3A9E9E','#4DAEAE','#5FB8B8','#80C4C4','#9FCFCF','#BCDBDB','#D8E7E7','#888780']}]
    }, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#E6EDF3',font:{size:10}}}}}
  });

  // Risk panel
  const b = beta(t.history, bench?.history) ?? t.fundamentals?.beta;
  const var95v = var95(t.history);
  const vol = t.volatility_1y!=null ? t.volatility_1y : annVol(t.history);
  const teVal = te;
  function rcell(label, val, fmt, cls){
    return `<div class="risk-cell"><div class="lab">${label}</div><div class="v ${cls}">${val==null?'—':fmt(val)}</div></div>`;
  }
  const betaCls = b==null?'': (b>1.2?'gold':(b<0.8?'green':''));
  const varCls = var95v==null?'': (var95v<-5?'red':(var95v<-3?'gold':''));
  const volCls = vol==null?'': (vol<15?'green':(vol>30?'gold':''));
  const teCls2 = teVal==null?'': (teVal<2?'green':(teVal>4?'gold':''));
  document.getElementById('pm-risk-grid').innerHTML =
    rcell('Beta', b, v=>v.toFixed(2), betaCls) +
    rcell('VaR 95%', var95v, v=>v.toFixed(2)+'%', varCls) +
    rcell('연환산 변동성', vol, v=>v.toFixed(1)+'%', volCls) +
    rcell('트래킹에러', teVal, v=>v.toFixed(2)+'%', teCls2);

  // Sparkline rolling vol
  const rv = rollingVol(t.history,30);
  destroyChart('pm-spark');
  if (rv.length) {
    charts['pm-spark'] = new Chart(document.getElementById('pm-spark').getContext('2d'),{
      type:'line', data:{labels:rv.map(x=>x.date), datasets:[{data:rv.map(x=>x.v), borderColor:'#C8963E', backgroundColor:'rgba(200,150,62,0.12)', fill:true, pointRadius:0, borderWidth:1, tension:.2}]},
      options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{enabled:false}},scales:{x:{display:false},y:{display:false}}}
    });
  }

  // Bottom panel
  renderPMBottom(code, holdings, t, mdd);

  // Holdings table
  renderPMTable(code, holdings, period);
}

function chartOpts(showLegend){
  return {responsive:true,maintainAspectRatio:false,
    plugins:{legend:{display:!!showLegend, labels:{color:'#E6EDF3',font:{size:10}}}},
    scales:{x:{ticks:{color:'#8B949E',maxTicksLimit:6,font:{size:10}}, grid:{color:'rgba(255,255,255,0.04)'}},
            y:{ticks:{color:'#8B949E',font:{size:10}}, grid:{color:'rgba(255,255,255,0.04)'}}}};
}

function renderBannerPM(t, holdings, mdd, bench){
  const list = [];
  const top = holdings.length ? [...holdings].sort((a,b)=>(parseFloat(b.weight_pct)||0)-(parseFloat(a.weight_pct)||0))[0] : null;
  if (mdd!=null && mdd<-15) list.push({c:'r', t:`리스크 한도 초과 (${fmtPct(mdd)}) — 포지션 축소 검토`});
  if (t.returns?.['1m']>50) list.push({c:'g', t:`단기 1M ${fmtPct(t.returns['1m'])} 급등 — 차익실현 검토`});
  if (top && parseFloat(top.weight_pct)>30) list.push({c:'g', t:`${top.name} ${parseFloat(top.weight_pct).toFixed(1)}% 집중 — 분산 검토`});
  // excess return YTD
  if (bench){
    const er = (returnPct(periodSlice(t.history,state.period))||0) - (returnPct(periodSlice(bench.history,state.period))||0);
    if (er > 10) list.push({c:'gn', t:`벤치마크 대비 초과수익 ${er.toFixed(2)}%p (${periodLabel(state.period)})`});
    else if (er < -10) list.push({c:'r', t:`벤치마크 대비 하회 ${er.toFixed(2)}%p (${periodLabel(state.period)})`});
  }
  if (!list.length) list.push({c:'gn', t:'포트폴리오 정상 운용 중'});
  document.getElementById('pm-banner').innerHTML = list.slice(0,3).map(x=>`<div class="banner-item ${x.c}">${x.t}</div>`).join('');
}

function renderPMBottom(code, holdings, t, mdd){
  const tp = etfType(code);
  const el = document.getElementById('pm-bottom-panel');
  if (tp==='passive'){
    const targets = SEC.etf_targets?.[code];
    if (targets){
      // sector aggregation
      const cur = {};
      holdings.forEach(h=>{
        const yt = h.yfinance_ticker || '';
        const sec = MD.tickers[yt]?.fundamentals?.sector || '기타';
        cur[sec] = (cur[sec]||0) + (parseFloat(h.weight_pct)||0);
      });
      const thr = SEC.rebalance_threshold_pct || 5.0;
      const items = Object.entries(targets.sectors).map(([s,o])=>{
        const c = cur[s] || 0; const tg = o.target_pct; const gap = c-tg;
        let cls='gn', msg='정상';
        if (gap > thr){ cls='r'; msg='축소 검토'; }
        else if (gap < -thr){ cls='g'; msg='확대 검토'; }
        return `<li class="${cls}">${s}: ${c.toFixed(1)}% / 목표 ${tg.toFixed(1)}% → ${msg}</li>`;
      }).join('');
      el.innerHTML = `<h3>리밸런싱 신호 — 섹터별 목표 대비 갭 (현재 기준)</h3><ul class="signal-list">${items}</ul>`;
    } else {
      // fallback
      const top = [...holdings].sort((a,b)=>(parseFloat(b.weight_pct)||0)-(parseFloat(a.weight_pct)||0))[0];
      const items=[];
      if (top && parseFloat(top.weight_pct)>30) items.push(`<li class="g">${top.name} ${parseFloat(top.weight_pct).toFixed(1)}% 집중 — 분산 검토</li>`);
      if (mdd!=null && mdd<-15) items.push(`<li class="r">리스크 한도 초과 — 포지션 축소 검토</li>`);
      if (t.returns?.['1m']>50) items.push(`<li class="g">단기 ${fmtPct(t.returns['1m'])} 급등 — 차익실현 검토</li>`);
      if (!items.length) items.push(`<li class="gn">현재 포트폴리오 정상 범위</li>`);
      el.innerHTML = `<h3>리밸런싱 신호 (현재 기준)</h3><ul class="signal-list">${items.join('')}</ul>`;
    }
  } else {
    // theme — 집중도
    const sorted = [...holdings].sort((a,b)=>(parseFloat(b.weight_pct)||0)-(parseFloat(a.weight_pct)||0));
    const w = sorted.map(h=>parseFloat(h.weight_pct)||0);
    const top1=w[0]||0, top3=(w[0]||0)+(w[1]||0)+(w[2]||0), top5=w.slice(0,5).reduce((s,v)=>s+v,0);
    const rows=[];
    rows.push(`<li class="${top1>30?'g':'gn'}">Top1 종목 비중: <strong>${top1.toFixed(1)}%</strong> ${top1>30?'(집중 위험)':''}</li>`);
    rows.push(`<li class="${top3>50?'g':'gn'}">Top3 종목 비중 합: <strong>${top3.toFixed(1)}%</strong></li>`);
    rows.push(`<li class="${top5>70?'r':'gn'}">Top5 종목 비중 합: <strong>${top5.toFixed(1)}%</strong></li>`);
    // contribution best/worst
    const contrib = sorted.map(h=>({n:h.name, c:(parseFloat(h.weight_pct)||0)*(parseFloat(h.return_1w_pct)||0)/100}));
    contrib.sort((a,b)=>b.c-a.c);
    if (contrib.length){
      rows.push(`<li class="gn">기여도 1위: <strong>${contrib[0].n} ${contrib[0].c>=0?'+':''}${contrib[0].c.toFixed(2)}%p</strong></li>`);
      rows.push(`<li class="r">기여도 꼴찌: <strong>${contrib[contrib.length-1].n} ${contrib[contrib.length-1].c.toFixed(2)}%p</strong></li>`);
    }
    if (top1<=30 && top3<=50 && top5<=70) rows.push(`<li class="gn">🟢 집중도 리스크 정상 범위</li>`);
    el.innerHTML = `<h3>집중도 리스크 (현재 기준)</h3><ul class="signal-list">${rows.join('')}</ul>`;
  }
}

function renderPMTable(code, holdings, period){
  const sorted = [...holdings].sort((a,b)=>(parseFloat(b.weight_pct)||0)-(parseFloat(a.weight_pct)||0));
  const periodKey = {ytd:'ytd','1m':'1m','3m':'3m','1y':'1y'}[period];
  const top1Pct = sorted.length ? parseFloat(sorted[0].weight_pct)||0 : 0;
  const head = `<thead><tr><th>종목명</th><th>의견</th><th>비중(%)</th><th>수익률 (${periodLabel(period)})</th><th>기여도 (${periodLabel(period)})</th><th>목표주가 괴리</th></tr></thead>`;
  const rows = sorted.map((h,i)=>{
    const yt = h.yfinance_ticker || '';
    const md = MD.tickers[yt];
    const w = parseFloat(h.weight_pct)||0;
    const ret = md?.returns ? (md.returns[periodKey] ?? null) : null;
    const contrib = (ret!=null) ? (w*ret/100) : null;
    const tp = md?.fundamentals?.target_price, cp = md?.current_price;
    const gap = (tp&&cp) ? ((tp-cp)/cp*100) : null;
    let badge = '<span class="badge badge-na">N/A</span>';
    if (gap!=null){
      if (gap>=20) badge='<span class="badge badge-buy">📈 BUY</span>';
      else if (gap<=-10) badge='<span class="badge badge-sell">📉 SELL</span>';
      else badge='<span class="badge badge-hold">⚪ HOLD</span>';
    }
    const foreign = !yt.endsWith('.KS') ? '<span class="tag-foreign">해외</span>' : '';
    const rowCls = (i===0 && top1Pct>30) ? 'row-warn' : '';
    const gapCls = gap==null?'': (gap>=20?'green':(gap<=-10?'red':''));
    return `<tr class="${rowCls}"><td>${h.name||yt}${foreign}</td><td>${badge}</td><td>${w.toFixed(1)}%</td>
      <td class="${ret==null?'':(ret>0?'green':'red')}">${fmtPct(ret)}</td>
      <td class="${contrib==null?'':(contrib>0?'green':'red')}">${contrib==null?'—':((contrib>0?'+':'')+contrib.toFixed(2)+'%p')}</td>
      <td class="${gapCls}">${gap==null?'—':fmtPct(gap,true,1)}</td></tr>`;
  }).join('');
  document.getElementById('pm-table').innerHTML = head + '<tbody>'+rows+'</tbody>';
}

// ── RA rendering ──────────────────────────────────────────────────────────
function isExcludedRA(ticker, t){
  const sn = t.fundamentals?.short_name || '';
  // A: ETF keywords
  if (ETF_KEYWORDS.some(k=>sn.toUpperCase().includes(k.toUpperCase()))) return true;
  // B: data empty
  const f = t.fundamentals||{};
  const noData = (f.per_fwd==null && f.pbr==null && f.target_price==null) && (!t.quarterly || !t.quarterly.length);
  if (noData) return true;
  return false;
}
function displayName(ticker, t){
  const sn = t.fundamentals?.short_name || ticker;
  if (BROKEN_NAME_RE.test(sn)) return ticker;
  return sn;
}

function buildRAOptions(){
  const opts = [];
  for (const [tk, t] of Object.entries(MD.tickers)){
    if (t.role !== 'holding') continue;
    if (isExcludedRA(tk, t)) continue;
    opts.push({tk, name: displayName(tk,t)});
  }
  opts.sort((a,b)=>a.name.localeCompare(b.name,'ko'));
  return opts;
}

function renderRA(){
  const tk = state.stock;
  const t = MD.tickers[tk]; if(!t) return;
  const f = t.fundamentals || {};
  const name = displayName(tk, t);
  const cp = t.current_price, tp = f.target_price;
  const gap = (tp && cp) ? ((tp-cp)/cp*100) : null;
  let badge='<span class="badge badge-na">❓ N/A</span>';
  if (gap!=null){
    if (gap>=20) badge='<span class="badge badge-buy">📈 BUY</span>';
    else if (gap<=-10) badge='<span class="badge badge-sell">📉 SELL</span>';
    else badge='<span class="badge badge-hold">⚪ HOLD</span>';
  }
  const sector = f.sector;
  // peer chips
  const peers = Object.entries(MD.tickers).filter(([k,x])=>x.role==='holding' && x.fundamentals?.sector===sector && k!==tk && !isExcludedRA(k,x))
    .sort((a,b)=>(b[1].fundamentals?.market_cap||0)-(a[1].fundamentals?.market_cap||0)).slice(0,5);
  const chips = peers.length>=3 ? `<div class="peer-chips">${peers.map(([k,x])=>`<span class="peer-chip" data-tk="${k}">${displayName(k,x)}</span>`).join('')}</div>` : '';

  const gapCls = gap==null?'mute':(gap>=20?'green':(gap<=-10?'red':'mute'));
  document.getElementById('ra-header').innerHTML =
    `<span class="name">${name}</span><span class="ticker-tag">${tk}</span>${badge}` +
    `<span class="mute">현재가</span><span>${fmtKRW(cp)}</span>` +
    (tp!=null ? `<span class="mute">목표주가</span><span>${fmtKRW(tp)}</span><span class="badge ${gap>=20?'badge-buy':(gap<=-10?'badge-sell':'badge-hold')}">괴리율 ${fmtPct(gap,true,1)}</span>`
              : `<span class="mute">목표주가 미제공</span>`) + chips;

  document.querySelectorAll('.peer-chip').forEach(c=>c.addEventListener('click',()=>{
    state.stock=c.dataset.tk; document.getElementById('ra-select').value=c.dataset.tk; renderRA();
  }));

  // RA KPI
  // Sector avg PER
  const sectorPeers = Object.values(MD.tickers).filter(x=>x.role==='holding' && x.fundamentals?.sector===sector && x.fundamentals?.per_fwd!=null);
  const sectorAvgPER = sectorPeers.length>=3 ? sectorPeers.reduce((s,x)=>s+x.fundamentals.per_fwd,0)/sectorPeers.length : null;
  function kpi(label, value, sub='', cls=''){
    return `<div class="card kpi-card ${cls}"><div class="label">${label}</div><div class="value">${value}</div><div class="sub">${sub}</div></div>`;
  }
  const per = f.per_fwd ?? f.per_ttm;
  const perSub = (sectorAvgPER && per!=null) ? `섹터평균 대비 ${(((per/sectorAvgPER)-1)*100).toFixed(1)}%` : '';
  const roeCls = f.roe==null?'': (f.roe>15?'green':(f.roe<5?'red':''));
  document.getElementById('ra-kpi').innerHTML =
    kpi('PER (12M Fwd)', per==null?'—':per.toFixed(2)+'x', perSub) +
    kpi('PBR', f.pbr==null?'—':f.pbr.toFixed(2)+'x', '') +
    kpi('EPS (TTM)', f.eps_ttm==null?'—':f.eps_ttm.toLocaleString('ko-KR')+'원', '') +
    kpi('ROE', `<span class="${roeCls}">${f.roe==null?'—':f.roe.toFixed(1)+'%'}</span>`, '') +
    kpi('배당수익률', f.dividend_yield==null?'—':f.dividend_yield.toFixed(1)+'%', f.dps?`DPS ${f.dps.toLocaleString('ko-KR')}원`:'');

  renderRABanner(tk, t, gap, sectorAvgPER);
  renderRAPriceChart(t, f);
  renderRASurprise(tk, t);
  renderRAQuarterly(t);
  renderRAPeer(tk, t, sector, sectorAvgPER);
  renderRAFin(tk, t);
  renderRAInsights(tk, t, gap, sectorAvgPER);
}

function renderRABanner(tk, t, gap, sectorAvg){
  const f = t.fundamentals || {};
  const list=[];
  if (gap!=null && gap>=20) list.push({c:'gn', t:`목표주가 대비 ${fmtPct(gap,true,1)} 상승 여력`});
  if (gap!=null && gap<=-10) list.push({c:'r', t:`목표주가 하회 ${fmtPct(gap,true,1)} — 하락 리스크`});
  const cq = CONS.tickers?.[tk]?.quarters;
  if (cq && cq.length){
    const last = cq[cq.length-1];
    if (last.revenue_surprise_pct>=5) list.push({c:'gn', t:`최근 분기 매출 컨센서스 ${fmtPct(last.revenue_surprise_pct,true,1)} 상회`});
    else if (last.revenue_surprise_pct<=-5) list.push({c:'r', t:`최근 분기 매출 컨센서스 ${fmtPct(last.revenue_surprise_pct,true,1)} 하회 — 어닝 쇼크`});
  }
  if (sectorAvg && f.per_fwd!=null && f.per_fwd < sectorAvg*0.8) list.push({c:'gn', t:`섹터 평균 대비 PER 저평가`});
  if (f.roe!=null && f.roe>15) list.push({c:'gn', t:`ROE ${f.roe.toFixed(1)}% — 우수한 자본효율성`});
  if (f.debt_to_equity!=null && f.debt_to_equity>200) list.push({c:'g', t:`부채비율 ${Math.round(f.debt_to_equity)}% — 재무 레버리지 주의`});
  if (!list.length) list.push({c:'gn', t:'밸류에이션 정상 범위'});
  document.getElementById('ra-banner').innerHTML = list.slice(0,3).map(x=>`<div class="banner-item ${x.c}">${x.t}</div>`).join('');
}

function renderRAPriceChart(t, f){
  document.getElementById('ra-price-title').textContent = `주가 추이 vs 목표주가 (${periodLabel(state.period)})`;
  const slice = periodSlice(t.history, state.period);
  destroyChart('ra-price');
  const datasets = [{label:'주가', data:slice.map(x=>x.close), borderColor:'#3A9E9E', borderWidth:2, pointRadius:0, tension:.1}];
  if (f.target_price!=null) datasets.push({label:'목표주가', data:slice.map(()=>f.target_price), borderColor:'#1D9E75', borderDash:[6,3], pointRadius:0, borderWidth:1});
  if (f.week52_high!=null) datasets.push({label:'52주 고가', data:slice.map(()=>f.week52_high), borderColor:'rgba(136,135,128,0.4)', borderWidth:1, pointRadius:0});
  if (f.week52_low!=null) datasets.push({label:'52주 저가', data:slice.map(()=>f.week52_low), borderColor:'rgba(136,135,128,0.4)', borderWidth:1, pointRadius:0});
  charts['ra-price'] = new Chart(document.getElementById('ra-price').getContext('2d'),{
    type:'line', data:{labels:slice.map(x=>x.date), datasets}, options:chartOpts(true)
  });
}

function renderRASurprise(tk, t){
  const card = document.getElementById('ra-surprise-card');
  const cd = CONS.tickers?.[tk];
  if (!cd || !cd.quarters?.length){
    card.style.display='none'; return;
  }
  card.style.display='';
  destroyChart('ra-surprise');
  const qs = cd.quarters;
  const labels = qs.map(q=>q.quarter);
  const cons = qs.map(q=>q.consensus_revenue/1e8);
  const act = qs.map(q=>q.actual_revenue/1e8);
  const surpColors = qs.map(q=>q.revenue_surprise_pct==null?'#888780':(q.revenue_surprise_pct>=0?'#1D9E75':'#E24B4A'));
  charts['ra-surprise'] = new Chart(document.getElementById('ra-surprise').getContext('2d'),{
    type:'bar',
    data:{labels, datasets:[
      {label:'컨센서스 매출(억)', data:cons, backgroundColor:'rgba(136,135,128,0.4)'},
      {label:'실제 매출(억)', data:act, backgroundColor:surpColors}
    ]},
    options:{...chartOpts(true), plugins:{...chartOpts(true).plugins,
      tooltip:{callbacks:{afterLabel:(ctx)=>{ const q=qs[ctx.dataIndex]; return `서프라이즈: ${q.revenue_surprise_pct==null?'—':(q.revenue_surprise_pct>0?'+':'')+q.revenue_surprise_pct+'%'}`; }}}}}
  });
}

function renderRAQuarterly(t){
  destroyChart('ra-quarterly');
  const q = t.quarterly || [];
  if (!q.length){ document.getElementById('ra-quarterly').parentElement.innerHTML='<h3>분기 실적</h3><div class="mute">분기 데이터 없음</div>'; return; }
  charts['ra-quarterly'] = new Chart(document.getElementById('ra-quarterly').getContext('2d'),{
    type:'bar', data:{labels:q.map(x=>x.quarter), datasets:[
      {label:'매출(억)', data:q.map(x=>(x.revenue||0)/1e8), backgroundColor:'#3A9E9E'},
      {label:'영업이익(억)', data:q.map(x=>(x.op_income||0)/1e8), backgroundColor:'#C8963E'}
    ]}, options:chartOpts(true)
  });
}

function renderRAPeer(tk, t, sector, sectorAvgPER){
  const peers = Object.entries(MD.tickers)
    .filter(([k,x])=>x.role==='holding' && x.fundamentals?.sector===sector && x.fundamentals?.per_fwd!=null && k!==tk && !isExcludedRA(k,x))
    .sort((a,b)=>a[1].fundamentals.per_fwd - b[1].fundamentals.per_fwd).slice(0,4);
  const me = [tk, t];
  const rows = [me, ...peers];
  function row([k,x], isMe){
    const f = x.fundamentals||{};
    const per = f.per_fwd;
    let perCls='';
    if (per!=null && sectorAvgPER){
      if (per < sectorAvgPER*0.8) perCls='cell-low';
      else if (per > sectorAvgPER*1.2) perCls='cell-high';
    }
    return `<tr style="${isMe?'background:rgba(58,158,158,0.12);':''}">
      <td>${isMe?'★ ':''}${displayName(k,x)}</td>
      <td class="${perCls}">${per==null?'—':per.toFixed(2)+'x'}</td>
      <td>${f.pbr==null?'—':f.pbr.toFixed(2)+'x'}</td>
      <td>${f.roe==null?'—':f.roe.toFixed(1)+'%'}</td>
      <td>${f.dividend_yield==null?'—':f.dividend_yield.toFixed(1)+'%'}</td></tr>`;
  }
  let html = `<table><thead><tr><th>종목명</th><th>PER</th><th>PBR</th><th>ROE</th><th>배당</th></tr></thead><tbody>`;
  html += rows.map((r,i)=>row(r, i===0)).join('');
  if (sectorAvgPER) html += `<tr style="background:#161B22"><td>섹터 평균</td><td>${sectorAvgPER.toFixed(2)}x</td><td>—</td><td>—</td><td>—</td></tr>`;
  html += `</tbody></table>`;
  const myPER = t.fundamentals?.per_fwd;
  let note='';
  if (sectorAvgPER && myPER!=null){
    if (myPER<sectorAvgPER*0.8) note=`<div class="green" style="margin-top:6px;font-size:var(--fs-sm)">섹터 평균 대비 저평가</div>`;
    else if (myPER>sectorAvgPER*1.2) note=`<div class="red" style="margin-top:6px;font-size:var(--fs-sm)">섹터 평균 대비 고평가</div>`;
  }
  document.getElementById('ra-peer').innerHTML = html + note;
}

function renderRAFin(tk, t){
  const isFin = t.fundamentals?.sector === 'Financial Services';
  // financial_index latest year per metric
  const items = FIN.filter(x=>x.ticker===tk);
  function latest(name){
    const cands = items.filter(x=>x.idx_nm===name && x.idx_val!=null).sort((a,b)=>b.bsns_year.localeCompare(a.bsns_year));
    return cands[0] ? parseFloat(cands[0].idx_val) : null;
  }
  const f = t.fundamentals||{};
  const roe = f.roe ?? latest('ROE');
  const de = f.debt_to_equity ?? latest('부채비율');
  const opm = f.op_margin ?? latest('영업이익률');
  const cur = f.current_ratio ?? latest('유동비율');
  const revG = latest('매출액증가율');

  function bar(label, val, fmt, max, color){
    const pct = val==null ? 0 : Math.min(100, Math.max(0, (val/max)*100));
    return `<div class="fin-row"><div class="top"><span>${label}</span><span>${val==null?'—':fmt(val)}</span></div><div class="progress"><i style="width:${pct}%;background:${color}"></i></div></div>`;
  }
  let deColor='#3A9E9E';
  if (!isFin && de!=null){ if (de>400) deColor='#E24B4A'; else if (de>200) deColor='#C8963E'; }
  const roeColor = roe!=null && roe>15 ? '#1D9E75' : '#3A9E9E';

  document.getElementById('ra-fin').innerHTML =
    bar('ROE', roe, v=>v.toFixed(1)+'%', 30, roeColor) +
    bar('부채비율'+(isFin?' (금융업 — 참고)':''), de, v=>v.toFixed(1)+'%', 500, deColor) +
    bar('영업이익률', opm, v=>v.toFixed(1)+'%', 30, '#3A9E9E') +
    bar('유동비율', cur, v=>v.toFixed(1)+'%', 300, '#3A9E9E') +
    bar('매출액증가율 (YoY)', revG, v=>v.toFixed(1)+'%', 50, '#3A9E9E');
}

function renderRAInsights(tk, t, gap, sectorAvgPER){
  const f = t.fundamentals||{};
  const per = f.per_fwd;
  const perDelta = (sectorAvgPER && per!=null) ? `${(((per/sectorAvgPER)-1)*100).toFixed(1)}%` : '—';
  // valuation
  let val={cls:'gray',msg:'데이터 부족'};
  if (per!=null && sectorAvgPER!=null){
    if (gap>=20 && per<sectorAvgPER*0.8) val={cls:'green',msg:`PER <strong>${per.toFixed(2)}x</strong>로 섹터 평균 대비 <strong>${perDelta}</strong> 저평가 구간. 목표주가 대비 괴리율 <strong>${fmtPct(gap,true,1)}</strong> — <strong>매수 신호 유효</strong>`};
    else if (gap<=-10 && per>sectorAvgPER*1.2) val={cls:'red',msg:`PER <strong>${per.toFixed(2)}x</strong>로 섹터 평균 대비 <strong>${perDelta}</strong> 고평가 구간. 목표주가 대비 괴리율 <strong>${fmtPct(gap,true,1)}</strong> — <strong>매도 신호</strong>`};
    else val={cls:'gray',msg:`PER <strong>${per.toFixed(2)}x</strong>로 섹터 평균 대비 <strong>${perDelta}</strong> 구간. 목표주가 대비 괴리율 <strong>${gap==null?'—':fmtPct(gap,true,1)}</strong> — 중립`};
  }
  // momentum
  const cd = CONS.tickers?.[tk];
  let mom={cls:'teal',msg:'컨센서스 데이터 없음 — 모멘텀 평가 불가'};
  if (cd && cd.quarters?.length){
    const last = cd.quarters[cd.quarters.length-1];
    const sp = last.revenue_surprise_pct;
    const qs = t.quarterly||[];
    let revYoY='—';
    if (qs.length>=5){ const cur=qs[qs.length-1].revenue, prev=qs[qs.length-5].revenue; if (cur&&prev) revYoY=fmtPct((cur-prev)/prev*100,true,1); }
    if (sp>=5) mom={cls:'green',msg:`최근 분기 매출 서프라이즈 <strong>${fmtPct(sp,true,1)}</strong>. 매출 추세 <strong>${revYoY}</strong>. <strong>어닝 모멘텀 강세</strong>`};
    else if (sp<=-5) mom={cls:'red',msg:`최근 분기 매출 서프라이즈 <strong>${fmtPct(sp,true,1)}</strong>. 매출 추세 <strong>${revYoY}</strong>. <strong>어닝 둔화 — 보수적 접근</strong>`};
    else mom={cls:'teal',msg:`최근 분기 매출 서프라이즈 <strong>${fmtPct(sp,true,1)}</strong>. 매출 추세 <strong>${revYoY}</strong>. 중립적 흐름`};
  }
  // risk
  const isFin = f.sector==='Financial Services';
  let risk={cls:'gold',msg:'재무 레버리지 데이터 없음'};
  if (isFin) risk={cls:'gold',msg:'금융업 — 부채비율 적용 제외. 자본적정성 별도 검토 필요'};
  else if (f.debt_to_equity!=null){
    const d = f.debt_to_equity;
    if (d>400) risk={cls:'red',msg:`부채비율 <strong>${Math.round(d)}%</strong> — 재무 위험 구간. 모니터링 필수`};
    else if (d>200) risk={cls:'gold',msg:`부채비율 <strong>${Math.round(d)}%</strong> — 레버리지 주의`};
    else risk={cls:'gold',msg:`부채비율 <strong>${Math.round(d)}%</strong> — 정상 범위`};
  }
  document.getElementById('ra-insights').innerHTML =
    `<div class="card insight-panel ${val.cls}"><h3>밸류에이션 (현재 기준)</h3><div>${val.msg}</div></div>` +
    `<div class="card insight-panel ${mom.cls}"><h3>실적 모멘텀 (최신 공시 기준)</h3><div>${mom.msg}</div></div>` +
    `<div class="card insight-panel ${risk.cls}"><h3>리스크 (최신 공시 기준)</h3><div>${risk.msg}</div></div>`;
}

// ── Debug panel ───────────────────────────────────────────────────────────
function renderDebug(){
  const totalTickers = Object.keys(MD.tickers).length;
  const finCount = FIN.length;
  const consCount = Object.keys(CONS.tickers||{}).length;
  const csvCount = Object.keys(HOLDINGS).length;
  const raExcluded = Object.entries(MD.tickers).filter(([k,t])=>t.role==='holding' && isExcludedRA(k,t)).length;
  const broken = Object.entries(MD.tickers).filter(([k,t])=>t.role==='holding' && BROKEN_NAME_RE.test(t.fundamentals?.short_name||'')).length;
  const finIssue = Object.entries(MD.tickers).filter(([k,t])=>t.role==='holding' && t.fundamentals?.sector==='Financial Services').length;
  const foreign = Object.keys(MD.tickers).filter(k=>!k.endsWith('.KS')).length;
  document.getElementById('debug-panel').innerHTML = `
    <h4>데이터 로드</h4>
    <div>✅ market_data.json (${totalTickers} tickers)</div>
    <div>✅ financial_index.json (${finCount.toLocaleString()})</div>
    <div>✅ sector_targets.json</div>
    <div>✅ consensus_data.json (${consCount})</div>
    <div>✅ etf_holdings_*.csv (${csvCount} files)</div>
    <h4>경로</h4>
    <div>[role-map] PATH=${fitCheck.path}</div>
    ${fitCheck.fit?'':`<div class="mute">reason: ${fitCheck.reasons.join('; ')}</div>`}
    <h4>역할 매핑 (성공)</h4>
    <div>close_role  ← current_price</div>
    <div>weight_role ← weight_pct</div>
    <div>per_role    ← per_fwd</div>
    <div>target_price_role ← target_price</div>
    <h4>필터 적용 결과</h4>
    <div>RA 제외 (조건 A·B): ${raExcluded}건</div>
    <div>이름 깨진 종목 (조건 C): ${broken}건</div>
    <h4>알려진 이슈</h4>
    <div>금융업 holding: ${finIssue}건</div>
    <div>해외 holding (.KS 없음): ${foreign}건</div>
  `;
}

// ── Init ──────────────────────────────────────────────────────────────────
function init(){
  // Period toggle visibility: global toggle only on PM tab, inline toggle only on RA tab
  function syncPeriodToggleVisibility(){
    const g = document.getElementById('period-toggle-global');
    const r = document.getElementById('period-toggle-ra');
    if (g) g.style.display = (state.tab==='pm') ? '' : 'none';
    if (r) r.style.display = (state.tab==='ra') ? '' : 'none';
  }
  // Tabs
  document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{
    state.tab=t.dataset.tab;
    document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===t));
    document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active', v.id==='view-'+state.tab));
    syncPeriodToggleVisibility();
  }));
  syncPeriodToggleVisibility();
  // Period (both global and inline toggles share .period-btn class — clicking any syncs all)
  document.querySelectorAll('.period-btn').forEach(b=>b.addEventListener('click',()=>{
    state.period=b.dataset.p;
    document.querySelectorAll('.period-btn').forEach(x=>x.classList.toggle('active',x.dataset.p===state.period));
    // PM has multiple period-dependent items (KPI, line chart, table, banner) — full re-render
    renderPM();
    // RA: only the price chart depends on period. Surprise/quarterly/peer/fin/KPI use "최신 공시 기준" and stay fixed.
    const tk = state.stock; const t = MD.tickers[tk];
    if (t) renderRAPriceChart(t, t.fundamentals || {});
  }));
  // PM dropdown
  const sel = document.getElementById('etf-select');
  sel.innerHTML = Object.keys(ETF_META).map(k=>`<option value="${k}" ${k===PM_DEFAULT?'selected':''}>${ETF_META[k].name} (${k})</option>`).join('');
  sel.addEventListener('change',()=>{ state.etf=sel.value; renderPM(); });
  // RA dropdown
  const raOpts = buildRAOptions();
  const raSel = document.getElementById('ra-select');
  function fillRA(filter){
    raSel.innerHTML = raOpts.filter(o=>!filter||o.name.toLowerCase().includes(filter.toLowerCase())||o.tk.includes(filter))
      .map(o=>`<option value="${o.tk}" ${o.tk===state.stock?'selected':''}>${o.name} (${o.tk})</option>`).join('');
  }
  fillRA('');
  raSel.value = RA_DEFAULT;
  raSel.addEventListener('change',()=>{ state.stock=raSel.value; renderRA(); });
  document.getElementById('ra-search').addEventListener('input',e=>{ fillRA(e.target.value); });
  // Debug
  document.getElementById('debug-toggle').addEventListener('click',()=>{
    document.getElementById('debug-panel').classList.toggle('open');
  });
  renderDebug();
  renderPM();
  renderRA();
}
init();
</script>
</body>
</html>
"""

# ── Step 3: Inline raw text via safe replace (no f-string with braces) ─────
out = (HTML
       .replace("__MARKET__", safe(market_data_raw))
       .replace("__FIN__", safe(financial_index_raw))
       .replace("__SEC__", safe(sector_targets_raw))
       .replace("__CONS__", safe(consensus_raw))
       .replace("__HOLDINGS__", safe(holdings_js_obj)))

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(out)

print(f"OK → {OUT_PATH}  ({len(out):,} bytes)")
