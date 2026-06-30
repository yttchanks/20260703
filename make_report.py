import json, html
from pathlib import Path
DATA=json.load(open('/home/user/analysis_output/analysis_data.json',encoding='utf-8'))
def sanitize_for_report(obj):
    sensitive={'cname','ename','strn','student_name','學生中文全名','學生聯絡電話(可選擇填寫)','phone','電話'}
    if isinstance(obj, dict):
        return {k:sanitize_for_report(v) for k,v in obj.items() if k not in sensitive}
    if isinstance(obj, list):
        return [sanitize_for_report(x) for x in obj]
    return obj
DATA=sanitize_for_report(DATA)
json_text=json.dumps(DATA,ensure_ascii=False).replace('</','<\/')
html_doc=f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>學校年度檢討互動報告｜2025/26</title>
<style>
:root {{--bg:#f6f7fb;--card:#fff;--ink:#172033;--muted:#667085;--pri:#2952cc;--pri2:#eef3ff;--good:#0a7f52;--warn:#b54708;--bad:#b42318;--line:#e5e7eb;--shadow:0 8px 25px rgba(16,24,40,.08);}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC","PingFang TC","Microsoft JhengHei",Arial,sans-serif;}}
header{{background:linear-gradient(135deg,#183a9e,#3273dc 60%,#68a8ff);color:#fff;padding:28px 30px 22px;position:sticky;top:0;z-index:5;box-shadow:0 6px 18px rgba(10,30,90,.18)}}
h1{{margin:0 0 8px;font-size:28px;letter-spacing:.5px}} .sub{{opacity:.92;font-size:14px;line-height:1.6}} .wrap{{max-width:1360px;margin:0 auto;padding:22px}}
.nav{{display:flex;gap:8px;flex-wrap:wrap;margin-top:15px}} .nav button,.pill{{border:1px solid rgba(255,255,255,.35);background:rgba(255,255,255,.14);color:#fff;border-radius:999px;padding:8px 12px;cursor:pointer;font-weight:600}} .nav button:hover{{background:rgba(255,255,255,.25)}}
.grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:var(--shadow)}}
.kpi{{grid-column:span 3}} .kpi b{{font-size:28px;display:block;color:#173b8f}} .kpi span{{font-size:13px;color:var(--muted)}}
.span4{{grid-column:span 4}} .span5{{grid-column:span 5}} .span6{{grid-column:span 6}} .span7{{grid-column:span 7}} .span8{{grid-column:span 8}} .span12{{grid-column:span 12}}
h2{{font-size:20px;margin:0 0 12px}} h3{{font-size:16px;margin:12px 0 8px}} p{{line-height:1.65}} .muted{{color:var(--muted)}} .small{{font-size:12px;color:var(--muted)}}
.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 14px}} select,input{{border:1px solid #cfd5e1;border-radius:10px;padding:9px 10px;background:#fff;min-width:150px}} input{{min-width:230px}} button.action{{background:var(--pri);border:0;border-radius:10px;color:#fff;padding:9px 13px;cursor:pointer}}
.tag{{display:inline-block;background:var(--pri2);color:#173b8f;border-radius:999px;padding:4px 9px;margin:2px;font-size:12px;font-weight:700}} .tag.warn{{background:#fff4e5;color:var(--warn)}} .tag.bad{{background:#ffefef;color:var(--bad)}} .tag.good{{background:#eafaf2;color:var(--good)}}
ul.clean{{padding-left:18px;margin:8px 0}} li{{margin:5px 0;line-height:1.5}}
table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{padding:9px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}} th{{background:#f8fafc;position:sticky;top:0;z-index:1;cursor:pointer}} tr:hover td{{background:#fbfdff}} .tablewrap{{max-height:470px;overflow:auto;border:1px solid var(--line);border-radius:12px}}
.svgbox{{width:100%;height:260px;border:1px solid var(--line);border-radius:12px;background:linear-gradient(#fff,#fbfcff)}} .swot{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}} .swot div{{border-radius:12px;padding:12px;border:1px solid var(--line)}} .S{{background:#eef8f3}} .W{{background:#fff7ed}} .O{{background:#eef4ff}} .T{{background:#fff1f2}}
.report-block{{border-left:4px solid var(--pri);padding:10px 12px;background:#f8fbff;border-radius:10px;margin:10px 0}} .section{{scroll-margin-top:125px;margin-bottom:18px}}
@media(max-width:900px){{.kpi,.span4,.span5,.span6,.span7,.span8,.span12{{grid-column:span 12}} header{{position:static}} .swot{{grid-template-columns:1fr}}}}
@media print{{header,.controls,.nav{{display:none}} body{{background:#fff}} .card{{box-shadow:none;break-inside:avoid}} .tablewrap{{max-height:none;overflow:visible}}}}
</style>
</head>
<body>
<header>
  <h1>學校年度檢討互動報告（2025/26）</h1>
  <div class="sub">資料來源：Google Workspace「20260703 Staff Development」｜產生日期：2026-06-29｜涵蓋 HKAT、HKDSE、Internal Exam、大榜、TSA 及行政/文件清單。<br>私隱提示：所有「特別個案」預設以匿名碼/班號呈現，不顯示學生姓名。</div>
  <div class="nav">
    <button onclick="go('overview')">總覽</button><button onclick="go('longitudinal')">縱向追蹤</button><button onclick="go('career')">升學就業</button><button onclick="go('dept')">部門報告</button><button onclick="go('subject')">科目報告</button><button onclick="go('cases')">特別個案</button><button onclick="go('tables')">互動數據表</button><button onclick="window.print()">列印/PDF</button>
  </div>
</header>
<div class="wrap">
  <section id="overview" class="section grid">
    <div class="card kpi"><b id="kFiles">—</b><span>Drive項目（含PDF/Excel/資料夾）</span></div>
    <div class="card kpi"><b id="kExcel">—</b><span>已下載/量化Excel</span></div>
    <div class="card kpi"><b id="kMetrics">—</b><span>量化指標列數</span></div>
    <div class="card kpi"><b id="kCases">—</b><span>匿名特別個案線索</span></div>
    <div class="card span8"><h2>一頁式重點摘要</h2><div id="highlights"></div></div>
    <div class="card span4"><h2>資料質素及限制</h2><ul class="clean" id="quality"></ul><div class="report-block"><b>建議使用方式</b><br>先以「部門報告」作科組會議討論，再以「科目報告」及「特別個案」落實支援/拔尖名單；所有個案須回到原始Excel作校內核實。</div></div>
    <div class="card span6"><h2>HKAT 中一入學基線趨勢</h2><div class="controls"><select id="hkatSub" onchange="drawHKAT()"></select></div><svg id="hkatChart" class="svgbox"></svg></div>
    <div class="card span6"><h2>DSE / TSA / 校內試近期關注</h2><svg id="focusChart" class="svgbox"></svg></div>
  </section>

  <section id="longitudinal" class="section grid">
    <div class="card span12"><h2>學生縱向追蹤：入學 → 中三/高中 → DSE → 升學/就業</h2><div class="report-block"><b>目的：</b>將中一入學基線（HKAT）連結至中三及高中校內試、DSE結果、畢業後升學/就業，建立「早識別、早介入、可量度成效」的學生發展追蹤模型。</div></div>
    <div class="card kpi"><b id="lk1">—</b><span>HKAT學生基線人數</span></div>
    <div class="card kpi"><b id="lk2">—</b><span>HKAT→校內試匿名匹配記錄</span></div>
    <div class="card kpi"><b id="lk3">—</b><span>縱向特別個案線索</span></div>
    <div class="card kpi"><b id="lk4">—</b><span>DSE cohort proxy 年份</span></div>
    <div class="card span6"><h2>各入學 cohort 追蹤概況</h2><div class="controls"><select id="longAssess" onchange="renderLongitudinal()"><option>Exam1</option><option>FT2</option><option>Exam2</option></select></div><svg id="longChart" class="svgbox"></svg></div>
    <div class="card span6"><h2>分析方法及現有缺口</h2><ul class="clean" id="longNotes"></ul><div id="careerStatus" class="report-block"></div></div>
    <div class="card span12"><h2>入學基線 → 現時校內試 cohort 表</h2><div class="tablewrap"><table id="longTable"></table></div></div>
    <div class="card span12"><h2>縱向特別個案：進步、下滑、持續支援</h2><div class="controls"><select id="longCaseType" onchange="renderLongitudinal()"><option value="all">全部類型</option></select><input id="longCaseSearch" placeholder="搜尋cohort、班號、匿名碼..." oninput="renderLongitudinal()"></div><div class="tablewrap"><table id="longCaseTable"></table></div></div>
    <div class="card span12"><h2>DSE cohort proxy 與升學/就業銜接</h2><p class="muted">由於現有HKAT只覆蓋2021-22起的入學cohort，而DSE 2020-2025考生約於2014-15至2019-20入讀中一，暫未能逐人由HKAT追到DSE；下表先以DSE年份推算入學cohort作整體趨勢參考。</p><div class="tablewrap"><table id="dseProxyTable"></table></div></div>
  </section>

  <section id="career" class="section grid">
    <div class="card span12"><h2>畢業生升學及就業出路分析（2022–2025）</h2><div class="report-block"><b>新增分析：</b>已將畢業生出路表與DSE成績作匿名連結，分析Best5 / 3322 / 核心科達標與升學、就業、VTC、DAE、重讀等路徑的關係。</div></div>
    <div class="card kpi"><b id="ck1">—</b><span>出路回覆總數</span></div>
    <div class="card kpi"><b id="ck2">—</b><span>成功連結DSE記錄</span></div>
    <div class="card kpi"><b id="ck3">—</b><span>需核實/未連結</span></div>
    <div class="card kpi"><b id="ck4">—</b><span>出路特別個案</span></div>
    <div class="card span6"><h2>各年度出路類型分佈</h2><div class="controls"><select id="careerDim" onchange="renderCareer()"><option value="level">課程層級</option><option value="institution_type">院校/途徑類型</option><option value="field">學習/職業範疇</option><option value="status">升學/就業狀態</option><option value="location">地區</option></select></div><svg id="careerChart" class="svgbox"></svg></div>
    <div class="card span6"><h2>DSE Best5 / 3322 與出路</h2><svg id="careerDseChart" class="svgbox"></svg></div>
    <div class="card span12"><h2>出路摘要表</h2><div class="controls"><input id="careerSummarySearch" placeholder="搜尋年度、類別、項目..." oninput="renderCareer()"></div><div class="tablewrap"><table id="careerSummaryTable"></table></div></div>
    <div class="card span12"><h2>DSE成績連結後的出路分佈</h2><div class="tablewrap"><table id="careerDseTable"></table></div></div>
    <div class="card span12"><h2>升學/就業特別個案線索</h2><div class="controls"><select id="careerCaseType" onchange="renderCareer()"><option value="all">全部類型</option></select><input id="careerCaseSearch" placeholder="搜尋年度、匿名碼、院校、課程..." oninput="renderCareer()"></div><div class="tablewrap"><table id="careerCaseTable"></table></div></div>
    <div class="card span12"><h2>熱門院校 / 課程 / 範疇 / 途徑</h2><div class="tablewrap"><table id="careerTopTable"></table></div></div>
  </section>

  <section id="dept" class="section grid">
    <div class="card span12"><h2>各部門專屬報告</h2><div class="controls"><select id="deptSelect" onchange="renderDept()"></select><button class="action" onclick="copyDept()">複製部門報告文字</button></div><div id="deptReport"></div></div>
  </section>

  <section id="subject" class="section grid">
    <div class="card span12"><h2>各科目專屬報告</h2><div class="controls"><select id="subjectSelect" onchange="renderSubject()"></select><select id="metricSource" onchange="renderSubject()"><option value="all">全部資料源</option><option value="hkat">HKAT</option><option value="dse">DSE</option><option value="exam">校內試</option><option value="tsa">TSA</option></select><input id="subjectSearch" placeholder="搜尋科目/年級/評估..." oninput="renderSubject()"></div><div class="grid"><div class="span5"><div id="subjectNarrative"></div></div><div class="span7"><svg id="subjectChart" class="svgbox"></svg></div><div class="span12 tablewrap"><table id="subjectTable"></table></div></div></div>
  </section>

  <section id="cases" class="section grid">
    <div class="card span12"><h2>特別個案線索（可篩選/排序）</h2><div class="controls"><select id="caseType" onchange="renderCases()"><option value="all">全部類型</option></select><input id="caseSearch" placeholder="搜尋年份、班號、匿名碼、備註..." oninput="renderCases()"><select id="caseLimit" onchange="renderCases()"><option>50</option><option>100</option><option>250</option><option>500</option></select></div><div class="small">注意：本表是「值得留意」的數據線索，不等於結論；需配合教師觀察、出席、功課、SEN/家庭背景等資料核實。</div><div class="tablewrap"><table id="caseTable"></table></div></div>
  </section>

  <section id="tables" class="section grid">
    <div class="card span12"><h2>互動數據表</h2><div class="controls"><select id="tableSelect" onchange="renderDataTable()"><option value="hkat">HKAT摘要</option><option value="dse_subject">DSE科目摘要</option><option value="exam">校內試摘要</option><option value="tsa">TSA摘要</option><option value="nine_value">九位數/增值</option><option value="dse_passrate">DSE歷年達標/科目合格</option><option value="career_records">升學就業原始標準化</option><option value="career_summary">升學就業摘要</option><option value="career_outcome_by_dse">DSE與出路</option></select><input id="tableSearch" placeholder="搜尋表格..." oninput="renderDataTable()"></div><div class="tablewrap"><table id="dataTable"></table></div></div>
  </section>
</div>
<script id="data" type="application/json">{json_text}</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
let sortState={{}};
function go(id){{document.getElementById(id).scrollIntoView({{behavior:'smooth'}})}}
function fmt(v){{ if(v===null||v===undefined||Number.isNaN(v)) return '—'; if(typeof v==='number') return (Math.round(v*10)/10).toString(); if(typeof v==='object') return JSON.stringify(v); return v; }}
function uniq(a){{return [...new Set(a.filter(x=>x!==null&&x!==undefined&&x!==''))].sort((x,y)=>String(x).localeCompare(String(y),'zh-Hant'));}}
function opt(sel, arr, allLabel=null){{sel.innerHTML=(allLabel?`<option value="all">${{allLabel}}</option>`:'')+arr.map(x=>`<option>${{x}}</option>`).join('')}}
function pctClass(v){{ if(v===null||v===undefined) return ''; if(v>=80) return 'good'; if(v<50) return 'bad'; if(v<65) return 'warn'; return '';}}
function makeTable(el, rows, cols){{
 if(!rows.length){{el.innerHTML='<tr><td>沒有符合資料</td></tr>';return}}
 cols=cols||Object.keys(rows[0]);
 el.innerHTML='<thead><tr>'+cols.map(c=>`<th onclick="sortTable('${{el.id}}','${{c}}')">${{c}}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>`<td>${{fmt(r[c])}}</td>`).join('')+'</tr>').join('')+'</tbody>';
 el._rows=rows; el._cols=cols;
}}
function sortTable(id,c){{const el=document.getElementById(id); let rows=[...(el._rows||[])]; let dir=sortState[id+c]==='asc'?'desc':'asc'; sortState[id+c]=dir; rows.sort((a,b)=>{{let x=a[c],y=b[c]; if(typeof x==='number'&&typeof y==='number') return dir==='asc'?x-y:y-x; return dir==='asc'?String(x).localeCompare(String(y),'zh-Hant'):String(y).localeCompare(String(x),'zh-Hant')}}); makeTable(el,rows,el._cols)}}
function lineChart(svg, rows, xKey, yKey, groupKey, title){{
 const W=svg.clientWidth||700,H=260,p=38; svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`); svg.innerHTML='';
 rows=rows.filter(r=>r[yKey]!==null&&r[yKey]!==undefined&&!isNaN(+r[yKey])); if(!rows.length){{svg.innerHTML='<text x="20" y="35">沒有足夠數據</text>';return}}
 const xs=uniq(rows.map(r=>r[xKey])); const ys=rows.map(r=>+r[yKey]); const ymin=Math.min(...ys), ymax=Math.max(...ys), pad=(ymax-ymin)*.12||1;
 const xPos=x=>p+(xs.indexOf(x)/(Math.max(1,xs.length-1)))*(W-p*1.5-p); const yPos=y=>H-p-((y-(ymin-pad))/(ymax-ymin+pad*2))*(H-p*2);
 let grid=''; for(let i=0;i<5;i++){{let y=p+i*(H-p*2)/4; grid+=`<line x1="${{p}}" y1="${{y}}" x2="${{W-p*.8}}" y2="${{y}}" stroke="#e5e7eb"/><text x="5" y="${{y+4}}" font-size="11" fill="#667085">${{(ymax+pad-i*(ymax-ymin+pad*2)/4).toFixed(1)}}</text>`}}
 svg.innerHTML=grid+`<text x="${{p}}" y="20" font-size="13" font-weight="700">${{title||''}}</text>`;
 const groups=groupKey?uniq(rows.map(r=>r[groupKey])):['']; const colors=['#2952cc','#0a7f52','#b54708','#7a2cc9','#b42318','#0086a8','#6b7280','#d97706'];
 groups.forEach((g,gi)=>{{let arr=rows.filter(r=>!groupKey||r[groupKey]===g).sort((a,b)=>xs.indexOf(a[xKey])-xs.indexOf(b[xKey])); let pts=arr.map(r=>[xPos(r[xKey]),yPos(+r[yKey]),r]); if(pts.length>1) svg.innerHTML+=`<polyline fill="none" stroke="${{colors[gi%colors.length]}}" stroke-width="3" points="${{pts.map(p=>p[0]+','+p[1]).join(' ')}}"/>`; pts.forEach(pt=>svg.innerHTML+=`<circle cx="${{pt[0]}}" cy="${{pt[1]}}" r="4" fill="${{colors[gi%colors.length]}}"><title>${{g}} ${{pt[2][xKey]}}: ${{fmt(pt[2][yKey])}}</title></circle>`); if(groupKey) svg.innerHTML+=`<text x="${{W-150}}" y="${{38+gi*16}}" font-size="12" fill="${{colors[gi%colors.length]}}">● ${{g}}</text>`; }});
 xs.forEach(x=>svg.innerHTML+=`<text x="${{xPos(x)-12}}" y="${{H-12}}" font-size="11" fill="#667085">${{x}}</text>`);
}}
function barChart(svg, rows, labelKey, valueKey, title){{
 const W=svg.clientWidth||700,H=260,p=38; svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`); rows=rows.filter(r=>r[valueKey]!==null&&r[valueKey]!==undefined).slice(0,10); if(!rows.length){{svg.innerHTML='<text x="20" y="35">沒有足夠數據</text>';return}}
 const max=Math.max(...rows.map(r=>+r[valueKey]),1); let bw=(W-p*2)/rows.length*.68; svg.innerHTML=`<text x="${{p}}" y="20" font-size="13" font-weight="700">${{title||''}}</text>`;
 rows.forEach((r,i)=>{{let x=p+i*(W-p*2)/rows.length+8, h=(+r[valueKey]/max)*(H-p*2), y=H-p-h; let cls=pctClass(+r[valueKey]); let color=cls==='bad'?'#b42318':cls==='warn'?'#b54708':'#2952cc'; svg.innerHTML+=`<rect x="${{x}}" y="${{y}}" width="${{bw}}" height="${{h}}" rx="5" fill="${{color}}"><title>${{r[labelKey]}}: ${{fmt(r[valueKey])}}</title></rect><text x="${{x}}" y="${{y-4}}" font-size="10">${{fmt(r[valueKey])}}</text><text transform="translate(${{x+bw/2}},${{H-12}}) rotate(-35)" font-size="10" text-anchor="end" fill="#667085">${{String(r[labelKey]).slice(0,16)}}</text>`}})
}}
function init(){{
 const counts=D.summary.manifest_counts||{{}}; const total=Object.values(counts).reduce((a,b)=>a+b,0);
 kFiles.textContent=total; kExcel.textContent=counts.excel||0; kMetrics.textContent=D.hkat.length+D.dse_subject.length+D.exam.length+D.tsa.length+D.nine_value.length; kCases.textContent=D.hkat_cases.length+D.dse_cases.length+D.exam_cases.length+((D.longitudinal&&D.longitudinal.longitudinal_cases)||[]).length+((D.career&&D.career.cases)||[]).length;
 highlights.innerHTML=D.highlights.map(h=>`<div class="report-block"><span class="tag">${{h.area}}</span><br><b>${{h.finding}}</b><br><span class="muted">${{h.implication}}</span></div>`).join('');
 quality.innerHTML=D.quality_notes.map(q=>`<li>${{q}}</li>`).join('');
 opt(hkatSub, uniq(D.hkat.map(r=>r.subject))); hkatSub.value='中文'; drawHKAT();
 barChart(focusChart, D.highlights.filter(h=>h.finding.includes('合格率')).map(h=>{{let m=h.finding.match(/合格率 ([\d.]+)/); return {{label:h.area,value:m?+m[1]:0}}}}), 'label','value','近期校內試最低合格率（節錄）');
 renderLongitudinalInit(); renderCareerInit();
 opt(deptSelect, Object.keys(D.swot)); renderDept();
 const subjects=uniq([...(D.hkat||[]).map(r=>r.subject),...(D.dse_subject||[]).map(r=>r.subject),...(D.exam||[]).map(r=>r.subject),...(D.tsa||[]).map(r=>r.subject)]); opt(subjectSelect,subjects); subjectSelect.value=subjects.includes('英文')?'英文':subjects[0]; renderSubject();
 const cases=allCases(); opt(caseType, uniq(cases.map(c=>c.type)), '全部類型'); renderCases(); renderDataTable();
}}
function drawHKAT(){{lineChart(hkatChart,D.hkat.filter(r=>r.subject===hkatSub.value),'year','mean',null,`${{hkatSub.value}}平均分`)}}
function deptMetrics(dept){{ const terms=(D.subject_groups[dept]||[]).map(x=>String(x).toLowerCase()); const hit=s=>terms.some(t=>String(s).toLowerCase().includes(t)||t.includes(String(s).toLowerCase())); return {{hkat:D.hkat.filter(r=>hit(r.subject)),dse:D.dse_subject.filter(r=>hit(r.subject)),exam:D.exam.filter(r=>hit(r.subject)),tsa:D.tsa.filter(r=>hit(r.subject))}} }}


function renderCareerInit(){{
 const C=D.career||{{records:[],linked_records:[],summary:[],outcome_by_dse:[],cases:[],top:[]}};
 if(!document.getElementById('ck1')) return;
 ck1.textContent=(C.records||[]).length; ck2.textContent=(C.linked_records||[]).length; ck3.textContent=C.unlinked_count||0; ck4.textContent=(C.cases||[]).length;
 opt(careerCaseType, uniq((C.cases||[]).map(c=>c.type)), '全部類型');
 renderCareer();
}}
function renderCareer(){{
 const C=D.career||{{records:[],linked_records:[],summary:[],outcome_by_dse:[],cases:[],top:[]}};
 const dim=careerDim.value;
 let sum=(C.summary||[]).filter(r=>r.dimension===dim);
 const q=careerSummarySearch.value.toLowerCase(); if(q) sum=sum.filter(r=>JSON.stringify(r).toLowerCase().includes(q));
 makeTable(careerSummaryTable, sum, ['grad_year','dimension','category','count','pct']);
 const latestYear=Math.max(...(C.records||[]).map(r=>r.grad_year).filter(Boolean),0);
 let chartRows=(C.summary||[]).filter(r=>r.dimension===dim && r.grad_year===latestYear).sort((a,b)=>b.count-a.count).map(r=>({{label:r.category,value:r.count}}));
 barChart(careerChart, chartRows, 'label','value', latestYear+'年 '+careerDim.options[careerDim.selectedIndex].text+' 分佈');
 let byD=(C.outcome_by_dse||[]).filter(r=>r.dimension==='level');
 makeTable(careerDseTable, byD, ['best5_band','dimension','category','count','pct','n_band']);
 barChart(careerDseChart, byD.filter(r=>r.best5_band==='20+' || r.best5_band==='3322達標').sort((a,b)=>b.count-a.count).map(r=>({{label:r.best5_band+' '+r.category,value:r.count}})), 'label','value','高Best5/3322達標學生出路');
 let cases=[...(C.cases||[])]; const t=careerCaseType.value, cq=careerCaseSearch.value.toLowerCase(); if(t!=='all') cases=cases.filter(c=>c.type===t); if(cq) cases=cases.filter(c=>JSON.stringify(c).toLowerCase().includes(cq));
 makeTable(careerCaseTable, cases, ['grad_year','code','class_no','type','metric','outcome','institution','programme','note']);
 makeTable(careerTopTable, (C.top||[]).slice(0,120), ['dimension','item','count']);
}}

function renderLongitudinalInit(){{
 const L=D.longitudinal||{{cohort_tracking:[],longitudinal_cases:[],dse_cohort_proxy:[],method_notes:[],career_status:{{}}}};
 if(!document.getElementById('lk1')) return;
 lk1.textContent=L.hkat_students||0; lk2.textContent=L.matched_records||0; lk3.textContent=(L.longitudinal_cases||[]).length; lk4.textContent=(L.dse_cohort_proxy||[]).length;
 longNotes.innerHTML=(L.method_notes||[]).map(x=>`<li>${{x}}</li>`).join('');
 careerStatus.innerHTML=`<b>升學/就業資料狀態：</b><br>${{(L.career_status&&L.career_status.note)||'未有資料'}}`;
 opt(longCaseType, uniq((L.longitudinal_cases||[]).map(c=>c.type)), '全部類型');
 renderLongitudinal();
}}
function renderLongitudinal(){{
 const L=D.longitudinal||{{cohort_tracking:[],longitudinal_cases:[],dse_cohort_proxy:[]}};
 const assess=document.getElementById('longAssess')?longAssess.value:'Exam1';
 let rows=(L.cohort_tracking||[]).filter(r=>String(r.stage||'').includes(assess));
 makeTable(longTable, rows, ['cohort','current_form_2025_26','stage','hkat_n','matched_n','match_rate','hkat_total_mean','matched_hkat_mean','current_exam_avg_mean','hkat_exam_corr','multi_fail_3plus','multi_fail_rate']);
 lineChart(longChart, rows.map(r=>({{year:r.cohort+'→'+r.current_form_2025_26, metric:'入學總分平均', value:r.matched_hkat_mean}})).concat(rows.map(r=>({{year:r.cohort+'→'+r.current_form_2025_26, metric:'現時考試平均', value:r.current_exam_avg_mean}}))), 'year','value','metric', '入學基線與現時校內試平均比較');
 let cs=[...(L.longitudinal_cases||[])]; const t=longCaseType.value, q=longCaseSearch.value.toLowerCase(); if(t!=='all') cs=cs.filter(c=>c.type===t); if(q) cs=cs.filter(c=>JSON.stringify(c).toLowerCase().includes(q));
 makeTable(longCaseTable, cs.slice(0,300), ['cohort','form','assessment','code','class_no','type','hkat_total','exam_avg','note']);
 makeTable(dseProxyTable, L.dse_cohort_proxy||[], ['dse_year','estimated_s1_entry','candidates','33222_pct','22222_pct','any5_2plus_pct','overall_2plus']);
}}

function renderDept(){{
 const dept=deptSelect.value, s=D.swot[dept], m=deptMetrics(dept);
 const recent=[...m.dse.filter(r=>r.year==='2025').map(r=>`${{r.subject}} DSE L2+ ${{fmt(r.lv2_plus)}}%`),...m.exam.filter(r=>r.assessment==='Exam2').sort((a,b)=>(a.pass_rate||999)-(b.pass_rate||999)).slice(0,5).map(r=>`${{r.form}} ${{r.subject}}校內試合格率 ${{fmt(r.pass_rate)}}%`),...m.tsa.slice(-4).map(r=>`${{r.year}} ${{r.subject}}TSA ${{fmt(r.school_basic_pct)}}%`)].slice(0,12);
 deptReport.innerHTML=`<div class="grid"><div class="span5"><h3>願景</h3><p>${{s.vision}}</p><h3>現況重點</h3>${{recent.length?'<ul class="clean">'+recent.map(x=>'<li>'+x+'</li>').join('')+'</ul>':'<p class="muted">此部門在結構化數據中可直接對應資料較少，建議補充科組文件/PDF摘要。</p>'}}</div><div class="span7"><svg id="deptChart" class="svgbox"></svg></div><div class="span12 swot"><div class="S"><b>S 優勢</b><ul>${{s.S.map(x=>'<li>'+x+'</li>').join('')}}</ul></div><div class="W"><b>W 弱項</b><ul>${{s.W.map(x=>'<li>'+x+'</li>').join('')}}</ul></div><div class="O"><b>O 機遇</b><ul>${{s.O.map(x=>'<li>'+x+'</li>').join('')}}</ul></div><div class="T"><b>T 威脅</b><ul>${{s.T.map(x=>'<li>'+x+'</li>').join('')}}</ul></div></div><div class="span12"><h3>建議行動</h3><ol><li>以本報告指標選定2–3個年度KPI（如核心科達標、低分群減少、SEN基本水平提升）。</li><li>每次考績後更新同一指標，科組會議先看趨勢，再看個案。</li><li>將「特別個案」分為補底、拔尖、邊緣達標三類，指定負責老師及回顧日期。</li></ol></div></div>`;
 const chartRows=m.dse.length?m.dse.filter(r=>r.lv2_plus!=null).map(r=>({{year:r.year,subject:r.subject,value:r.lv2_plus}})):m.exam.filter(r=>r.pass_rate!=null).map(r=>({{year:r.form+' '+r.assessment,subject:r.subject,value:r.pass_rate}}));
 lineChart(document.getElementById('deptChart'), chartRows, 'year','value','subject', dept+' 主要指標趨勢/分佈');
}}
function copyDept(){{navigator.clipboard&&navigator.clipboard.writeText(deptReport.innerText); alert('已複製部門報告文字（如瀏覽器允許）。')}}
function renderSubject(){{
 const subj=subjectSelect.value, src=metricSource.value, q=subjectSearch.value.toLowerCase(); let rows=[];
 if(src==='all'||src==='hkat') rows.push(...D.hkat.filter(r=>r.subject===subj).map(r=>({{source:'HKAT',year:r.year,form:'S1入學',assessment:'AT',subject:r.subject,mean:r.mean,n:r.n,pass_rate:'',lv2_plus:''}})));
 if(src==='all'||src==='dse') rows.push(...D.dse_subject.filter(r=>r.subject===subj).map(r=>({{source:'DSE',year:r.year,form:'S6',assessment:'HKDSE',subject:r.subject,mean:r.mean,n:r.n,pass_rate:r.lv2_plus,lv2_plus:r.lv2_plus,lv3_plus:r.lv3_plus,lv4_plus:r.lv4_plus}})));
 if(src==='all'||src==='exam') rows.push(...D.exam.filter(r=>r.subject===subj).map(r=>({{source:'校內試',year:r.year,form:r.form,assessment:r.assessment,subject:r.subject,mean:r.mean,n:r.n,pass_rate:r.pass_rate,lv2_plus:''}})));
 if(src==='all'||src==='tsa') rows.push(...D.tsa.filter(r=>r.subject===subj).map(r=>({{source:'TSA',year:r.year,form:'S3',assessment:'TSA',subject:r.subject,mean:r.school_basic_pct,n:r.n,pass_rate:r.school_basic_pct,hk_basic_pct:r.hk_basic_pct,value_added:r.value_added}})));
 if(q) rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q));
 const latest=rows.slice().sort((a,b)=>String(b.year).localeCompare(String(a.year)))[0];
 subjectNarrative.innerHTML=`<div class="card" style="box-shadow:none"><h3>${{subj}}：現況、走勢、願景</h3><p><b>現況：</b>${{latest?`最近資料源為${{latest.source}} / ${{latest.year}}，平均/主要百分率為 ${{fmt(latest.mean)}}，人數 n=${{fmt(latest.n)}}。`:'未有直接對應量化資料。'}}</p><p><b>走勢：</b>請參考右方折線/柱狀圖；若不同資料源量尺不同，應分開詮釋（分數、合格率、DSE Level 2+不可直接相加）。</p><p><b>願景：</b>建立「基線—過程—公開試」同一科目追蹤，將低成就、邊緣達標、高潛能三類學生各自配對策略。</p></div>`;
 lineChart(subjectChart, rows.map(r=>({{year:String(r.year)+' '+(r.form||''),source:r.source,value: (r.pass_rate!==''&&r.pass_rate!=null)?r.pass_rate:r.mean}})), 'year','value','source', subj+' 指標（分數/百分率混合顯示）');
 makeTable(subjectTable, rows, ['source','year','form','assessment','subject','n','mean','pass_rate','lv2_plus','lv3_plus','lv4_plus','hk_basic_pct','value_added']);
}}
function allCases(){{return [...D.hkat_cases.map(c=>({{source:'HKAT',year:c.year,code:c.code,class_no:'—',type:c.type,metric:c.total,note:c.note}})),...D.dse_cases.map(c=>({{source:'DSE',year:c.year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note}})),...D.exam_cases.map(c=>({{source:'校內試',year:'2025/26',code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note,form:c.form,assessment:c.assessment}})),...((D.career&&D.career.cases)||[]).map(c=>({{source:'升學就業',year:c.grad_year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:(c.outcome||'')+' '+(c.institution||'')+' '+(c.programme||'')+'｜'+(c.note||'')}}))]}}
function renderCases(){{ let rows=allCases(); const t=caseType.value,q=caseSearch.value.toLowerCase(),lim=+caseLimit.value; if(t!=='all') rows=rows.filter(r=>r.type===t); if(q) rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(caseTable, rows.slice(0,lim), ['source','year','form','assessment','code','class_no','type','metric','note']);}}
function renderDataTable(){{const key=tableSelect.value,q=tableSearch.value.toLowerCase(); let rows=[]; if(key==='career_records') rows=[...((D.career&&D.career.records)||[])]; else if(key==='career_summary') rows=[...((D.career&&D.career.summary)||[])]; else if(key==='career_outcome_by_dse') rows=[...((D.career&&D.career.outcome_by_dse)||[])]; else rows=[...(D[key]||[])]; if(q) rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(dataTable, rows.slice(0,1000));}}
window.addEventListener('load',init);
</script>
</body></html>'''
Path('/home/user/school_annual_review_interactive_report.html').write_text(html_doc,encoding='utf-8')
print('written', Path('/home/user/school_annual_review_interactive_report.html').stat().st_size)
