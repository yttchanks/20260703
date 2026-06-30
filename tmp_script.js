
const D=JSON.parse(document.getElementById('data').textContent);
let sortState={};
function go(id){document.getElementById(id).scrollIntoView({behavior:'smooth'})}
function fmt(v){ if(v===null||v===undefined||Number.isNaN(v)) return '—'; if(typeof v==='number') return (Math.round(v*10)/10).toString(); if(typeof v==='object') return JSON.stringify(v); return v; }
function uniq(a){return [...new Set(a.filter(x=>x!==null&&x!==undefined&&x!==''))].sort((x,y)=>String(x).localeCompare(String(y),'zh-Hant'));}
function opt(sel, arr, allLabel=null){sel.innerHTML=(allLabel?`<option value="all">${allLabel}</option>`:'')+arr.map(x=>`<option>${x}</option>`).join('')}
function pctClass(v){ if(v===null||v===undefined) return ''; if(v>=80) return 'good'; if(v<50) return 'bad'; if(v<65) return 'warn'; return '';}
function makeTable(el, rows, cols){
 if(!rows.length){el.innerHTML='<tr><td>沒有符合資料</td></tr>';return}
 cols=cols||Object.keys(rows[0]);
 el.innerHTML='<thead><tr>'+cols.map(c=>`<th onclick="sortTable('${el.id}','${c}')">${c}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>`<td>${fmt(r[c])}</td>`).join('')+'</tr>').join('')+'</tbody>';
 el._rows=rows; el._cols=cols;
}
function sortTable(id,c){const el=document.getElementById(id); let rows=[...(el._rows||[])]; let dir=sortState[id+c]==='asc'?'desc':'asc'; sortState[id+c]=dir; rows.sort((a,b)=>{let x=a[c],y=b[c]; if(typeof x==='number'&&typeof y==='number') return dir==='asc'?x-y:y-x; return dir==='asc'?String(x).localeCompare(String(y),'zh-Hant'):String(y).localeCompare(String(x),'zh-Hant')}); makeTable(el,rows,el._cols)}
function lineChart(svg, rows, xKey, yKey, groupKey, title){
 const W=svg.clientWidth||700,H=260,p=38; svg.setAttribute('viewBox',`0 0 ${W} ${H}`); svg.innerHTML='';
 rows=rows.filter(r=>r[yKey]!==null&&r[yKey]!==undefined&&!isNaN(+r[yKey])); if(!rows.length){svg.innerHTML='<text x="20" y="35">沒有足夠數據</text>';return}
 const xs=uniq(rows.map(r=>r[xKey])); const ys=rows.map(r=>+r[yKey]); const ymin=Math.min(...ys), ymax=Math.max(...ys), pad=(ymax-ymin)*.12||1;
 const xPos=x=>p+(xs.indexOf(x)/(Math.max(1,xs.length-1)))*(W-p*1.5-p); const yPos=y=>H-p-((y-(ymin-pad))/(ymax-ymin+pad*2))*(H-p*2);
 let grid=''; for(let i=0;i<5;i++){let y=p+i*(H-p*2)/4; grid+=`<line x1="${p}" y1="${y}" x2="${W-p*.8}" y2="${y}" stroke="#e5e7eb"/><text x="5" y="${y+4}" font-size="11" fill="#667085">${(ymax+pad-i*(ymax-ymin+pad*2)/4).toFixed(1)}</text>`}
 svg.innerHTML=grid+`<text x="${p}" y="20" font-size="13" font-weight="700">${title||''}</text>`;
 const groups=groupKey?uniq(rows.map(r=>r[groupKey])):['']; const colors=['#2952cc','#0a7f52','#b54708','#7a2cc9','#b42318','#0086a8','#6b7280','#d97706'];
 groups.forEach((g,gi)=>{let arr=rows.filter(r=>!groupKey||r[groupKey]===g).sort((a,b)=>xs.indexOf(a[xKey])-xs.indexOf(b[xKey])); let pts=arr.map(r=>[xPos(r[xKey]),yPos(+r[yKey]),r]); if(pts.length>1) svg.innerHTML+=`<polyline fill="none" stroke="${colors[gi%colors.length]}" stroke-width="3" points="${pts.map(p=>p[0]+','+p[1]).join(' ')}"/>`; pts.forEach(pt=>svg.innerHTML+=`<circle cx="${pt[0]}" cy="${pt[1]}" r="4" fill="${colors[gi%colors.length]}"><title>${g} ${pt[2][xKey]}: ${fmt(pt[2][yKey])}</title></circle>`); if(groupKey) svg.innerHTML+=`<text x="${W-150}" y="${38+gi*16}" font-size="12" fill="${colors[gi%colors.length]}">● ${g}</text>`; });
 xs.forEach(x=>svg.innerHTML+=`<text x="${xPos(x)-12}" y="${H-12}" font-size="11" fill="#667085">${x}</text>`);
}
function barChart(svg, rows, labelKey, valueKey, title){
 const W=svg.clientWidth||700,H=260,p=38; svg.setAttribute('viewBox',`0 0 ${W} ${H}`); rows=rows.filter(r=>r[valueKey]!==null&&r[valueKey]!==undefined).slice(0,10); if(!rows.length){svg.innerHTML='<text x="20" y="35">沒有足夠數據</text>';return}
 const max=Math.max(...rows.map(r=>+r[valueKey]),1); let bw=(W-p*2)/rows.length*.68; svg.innerHTML=`<text x="${p}" y="20" font-size="13" font-weight="700">${title||''}</text>`;
 rows.forEach((r,i)=>{let x=p+i*(W-p*2)/rows.length+8, h=(+r[valueKey]/max)*(H-p*2), y=H-p-h; let cls=pctClass(+r[valueKey]); let color=cls==='bad'?'#b42318':cls==='warn'?'#b54708':'#2952cc'; svg.innerHTML+=`<rect x="${x}" y="${y}" width="${bw}" height="${h}" rx="5" fill="${color}"><title>${r[labelKey]}: ${fmt(r[valueKey])}</title></rect><text x="${x}" y="${y-4}" font-size="10">${fmt(r[valueKey])}</text><text transform="translate(${x+bw/2},${H-12}) rotate(-35)" font-size="10" text-anchor="end" fill="#667085">${String(r[labelKey]).slice(0,16)}</text>`})
}
function init(){
 const counts=D.summary.manifest_counts||{}; const total=Object.values(counts).reduce((a,b)=>a+b,0);
 kFiles.textContent=total; kExcel.textContent=counts.excel||0; kMetrics.textContent=D.hkat.length+D.dse_subject.length+D.exam.length+D.tsa.length+D.nine_value.length; kCases.textContent=D.hkat_cases.length+D.dse_cases.length+D.exam_cases.length+((D.longitudinal&&D.longitudinal.longitudinal_cases)||[]).length+((D.career&&D.career.cases)||[]).length;
 highlights.innerHTML=D.highlights.map(h=>`<div class="report-block"><span class="tag">${h.area}</span><br><b>${h.finding}</b><br><span class="muted">${h.implication}</span></div>`).join('');
 quality.innerHTML=D.quality_notes.map(q=>`<li>${q}</li>`).join('');
 opt(hkatSub, uniq(D.hkat.map(r=>r.subject))); hkatSub.value='中文'; drawHKAT();
 barChart(focusChart, D.highlights.filter(h=>h.finding.includes('合格率')).map(h=>{let m=h.finding.match(/合格率 ([\d.]+)/); return {label:h.area,value:m?+m[1]:0}}), 'label','value','近期校內試最低合格率（節錄）');
 renderLongitudinalInit(); renderCareerInit();
 opt(deptSelect, Object.keys(D.swot)); renderDept();
 const subjects=uniq([...(D.hkat||[]).map(r=>r.subject),...(D.dse_subject||[]).map(r=>r.subject),...(D.exam||[]).map(r=>r.subject),...(D.tsa||[]).map(r=>r.subject)]); opt(subjectSelect,subjects); subjectSelect.value=subjects.includes('英文')?'英文':subjects[0]; renderSubject();
 const cases=allCases(); opt(caseType, uniq(cases.map(c=>c.type)), '全部類型'); renderCases(); renderDataTable();
}
function drawHKAT(){lineChart(hkatChart,D.hkat.filter(r=>r.subject===hkatSub.value),'year','mean',null,`${hkatSub.value}平均分`)}
function deptMetrics(dept){ const terms=(D.subject_groups[dept]||[]).map(x=>String(x).toLowerCase()); const hit=s=>terms.some(t=>String(s).toLowerCase().includes(t)||t.includes(String(s).toLowerCase())); return {hkat:D.hkat.filter(r=>hit(r.subject)),dse:D.dse_subject.filter(r=>hit(r.subject)),exam:D.exam.filter(r=>hit(r.subject)),tsa:D.tsa.filter(r=>hit(r.subject))} }


function renderCareerInit(){
 const C=D.career||{records:[],linked_records:[],summary:[],outcome_by_dse:[],cases:[],top:[]};
 if(!document.getElementById('ck1')) return;
 ck1.textContent=(C.records||[]).length; ck2.textContent=(C.linked_records||[]).length; ck3.textContent=C.unlinked_count||0; ck4.textContent=(C.cases||[]).length;
 opt(careerCaseType, uniq((C.cases||[]).map(c=>c.type)), '全部類型');
 renderCareer();
}
function renderCareer(){
 const C=D.career||{records:[],linked_records:[],summary:[],outcome_by_dse:[],cases:[],top:[]};
 const dim=careerDim.value;
 let sum=(C.summary||[]).filter(r=>r.dimension===dim);
 const q=careerSummarySearch.value.toLowerCase(); if(q) sum=sum.filter(r=>JSON.stringify(r).toLowerCase().includes(q));
 makeTable(careerSummaryTable, sum, ['grad_year','dimension','category','count','pct']);
 const latestYear=Math.max(...(C.records||[]).map(r=>r.grad_year).filter(Boolean),0);
 let chartRows=(C.summary||[]).filter(r=>r.dimension===dim && r.grad_year===latestYear).sort((a,b)=>b.count-a.count).map(r=>({label:r.category,value:r.count}));
 barChart(careerChart, chartRows, 'label','value', latestYear+'年 '+careerDim.options[careerDim.selectedIndex].text+' 分佈');
 let byD=(C.outcome_by_dse||[]).filter(r=>r.dimension==='level');
 makeTable(careerDseTable, byD, ['best5_band','dimension','category','count','pct','n_band']);
 barChart(careerDseChart, byD.filter(r=>r.best5_band==='20+' || r.best5_band==='3322達標').sort((a,b)=>b.count-a.count).map(r=>({label:r.best5_band+' '+r.category,value:r.count})), 'label','value','高Best5/3322達標學生出路');
 let cases=[...(C.cases||[])]; const t=careerCaseType.value, cq=careerCaseSearch.value.toLowerCase(); if(t!=='all') cases=cases.filter(c=>c.type===t); if(cq) cases=cases.filter(c=>JSON.stringify(c).toLowerCase().includes(cq));
 makeTable(careerCaseTable, cases, ['grad_year','code','class_no','type','metric','outcome','institution','programme','note']);
 makeTable(careerTopTable, (C.top||[]).slice(0,120), ['dimension','item','count']);
}

function renderLongitudinalInit(){
 const L=D.longitudinal||{cohort_tracking:[],longitudinal_cases:[],dse_cohort_proxy:[],method_notes:[],career_status:{}};
 if(!document.getElementById('lk1')) return;
 lk1.textContent=L.hkat_students||0; lk2.textContent=L.matched_records||0; lk3.textContent=(L.longitudinal_cases||[]).length; lk4.textContent=(L.dse_cohort_proxy||[]).length;
 longNotes.innerHTML=(L.method_notes||[]).map(x=>`<li>${x}</li>`).join('');
 careerStatus.innerHTML=`<b>升學/就業資料狀態：</b><br>${(L.career_status&&L.career_status.note)||'未有資料'}`;
 opt(longCaseType, uniq((L.longitudinal_cases||[]).map(c=>c.type)), '全部類型');
 renderLongitudinal();
}
function renderLongitudinal(){
 const L=D.longitudinal||{cohort_tracking:[],longitudinal_cases:[],dse_cohort_proxy:[]};
 const assess=document.getElementById('longAssess')?longAssess.value:'Exam1';
 let rows=(L.cohort_tracking||[]).filter(r=>String(r.stage||'').includes(assess));
 makeTable(longTable, rows, ['cohort','current_form_2025_26','stage','hkat_n','matched_n','match_rate','hkat_total_mean','matched_hkat_mean','current_exam_avg_mean','hkat_exam_corr','multi_fail_3plus','multi_fail_rate']);
 lineChart(longChart, rows.map(r=>({year:r.cohort+'→'+r.current_form_2025_26, metric:'入學總分平均', value:r.matched_hkat_mean})).concat(rows.map(r=>({year:r.cohort+'→'+r.current_form_2025_26, metric:'現時考試平均', value:r.current_exam_avg_mean}))), 'year','value','metric', '入學基線與現時校內試平均比較');
 let cs=[...(L.longitudinal_cases||[])]; const t=longCaseType.value, q=longCaseSearch.value.toLowerCase(); if(t!=='all') cs=cs.filter(c=>c.type===t); if(q) cs=cs.filter(c=>JSON.stringify(c).toLowerCase().includes(q));
 makeTable(longCaseTable, cs.slice(0,300), ['cohort','form','assessment','code','class_no','type','hkat_total','exam_avg','note']);
 makeTable(dseProxyTable, L.dse_cohort_proxy||[], ['dse_year','estimated_s1_entry','candidates','33222_pct','22222_pct','any5_2plus_pct','overall_2plus']);
}

function renderDept(){
 const dept=deptSelect.value, s=D.swot[dept], m=deptMetrics(dept);
 const recent=[...m.dse.filter(r=>r.year==='2025').map(r=>`${r.subject} DSE L2+ ${fmt(r.lv2_plus)}%`),...m.exam.filter(r=>r.assessment==='Exam2').sort((a,b)=>(a.pass_rate||999)-(b.pass_rate||999)).slice(0,5).map(r=>`${r.form} ${r.subject}校內試合格率 ${fmt(r.pass_rate)}%`),...m.tsa.slice(-4).map(r=>`${r.year} ${r.subject}TSA ${fmt(r.school_basic_pct)}%`)].slice(0,12);
 deptReport.innerHTML=`<div class="grid"><div class="span5"><h3>願景</h3><p>${s.vision}</p><h3>現況重點</h3>${recent.length?'<ul class="clean">'+recent.map(x=>'<li>'+x+'</li>').join('')+'</ul>':'<p class="muted">此部門在結構化數據中可直接對應資料較少，建議補充科組文件/PDF摘要。</p>'}</div><div class="span7"><svg id="deptChart" class="svgbox"></svg></div><div class="span12 swot"><div class="S"><b>S 優勢</b><ul>${s.S.map(x=>'<li>'+x+'</li>').join('')}</ul></div><div class="W"><b>W 弱項</b><ul>${s.W.map(x=>'<li>'+x+'</li>').join('')}</ul></div><div class="O"><b>O 機遇</b><ul>${s.O.map(x=>'<li>'+x+'</li>').join('')}</ul></div><div class="T"><b>T 威脅</b><ul>${s.T.map(x=>'<li>'+x+'</li>').join('')}</ul></div></div><div class="span12"><h3>建議行動</h3><ol><li>以本報告指標選定2–3個年度KPI（如核心科達標、低分群減少、SEN基本水平提升）。</li><li>每次考績後更新同一指標，科組會議先看趨勢，再看個案。</li><li>將「特別個案」分為補底、拔尖、邊緣達標三類，指定負責老師及回顧日期。</li></ol></div></div>`;
 const chartRows=m.dse.length?m.dse.filter(r=>r.lv2_plus!=null).map(r=>({year:r.year,subject:r.subject,value:r.lv2_plus})):m.exam.filter(r=>r.pass_rate!=null).map(r=>({year:r.form+' '+r.assessment,subject:r.subject,value:r.pass_rate}));
 lineChart(document.getElementById('deptChart'), chartRows, 'year','value','subject', dept+' 主要指標趨勢/分佈');
}
function copyDept(){navigator.clipboard&&navigator.clipboard.writeText(deptReport.innerText); alert('已複製部門報告文字（如瀏覽器允許）。')}
function renderSubject(){
 const subj=subjectSelect.value, src=metricSource.value, q=subjectSearch.value.toLowerCase(); let rows=[];
 if(src==='all'||src==='hkat') rows.push(...D.hkat.filter(r=>r.subject===subj).map(r=>({source:'HKAT',year:r.year,form:'S1入學',assessment:'AT',subject:r.subject,mean:r.mean,n:r.n,pass_rate:'',lv2_plus:''})));
 if(src==='all'||src==='dse') rows.push(...D.dse_subject.filter(r=>r.subject===subj).map(r=>({source:'DSE',year:r.year,form:'S6',assessment:'HKDSE',subject:r.subject,mean:r.mean,n:r.n,pass_rate:r.lv2_plus,lv2_plus:r.lv2_plus,lv3_plus:r.lv3_plus,lv4_plus:r.lv4_plus})));
 if(src==='all'||src==='exam') rows.push(...D.exam.filter(r=>r.subject===subj).map(r=>({source:'校內試',year:r.year,form:r.form,assessment:r.assessment,subject:r.subject,mean:r.mean,n:r.n,pass_rate:r.pass_rate,lv2_plus:''})));
 if(src==='all'||src==='tsa') rows.push(...D.tsa.filter(r=>r.subject===subj).map(r=>({source:'TSA',year:r.year,form:'S3',assessment:'TSA',subject:r.subject,mean:r.school_basic_pct,n:r.n,pass_rate:r.school_basic_pct,hk_basic_pct:r.hk_basic_pct,value_added:r.value_added})));
 if(q) rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q));
 const latest=rows.slice().sort((a,b)=>String(b.year).localeCompare(String(a.year)))[0];
 subjectNarrative.innerHTML=`<div class="card" style="box-shadow:none"><h3>${subj}：現況、走勢、願景</h3><p><b>現況：</b>${latest?`最近資料源為${latest.source} / ${latest.year}，平均/主要百分率為 ${fmt(latest.mean)}，人數 n=${fmt(latest.n)}。`:'未有直接對應量化資料。'}</p><p><b>走勢：</b>請參考右方折線/柱狀圖；若不同資料源量尺不同，應分開詮釋（分數、合格率、DSE Level 2+不可直接相加）。</p><p><b>願景：</b>建立「基線—過程—公開試」同一科目追蹤，將低成就、邊緣達標、高潛能三類學生各自配對策略。</p></div>`;
 lineChart(subjectChart, rows.map(r=>({year:String(r.year)+' '+(r.form||''),source:r.source,value: (r.pass_rate!==''&&r.pass_rate!=null)?r.pass_rate:r.mean})), 'year','value','source', subj+' 指標（分數/百分率混合顯示）');
 makeTable(subjectTable, rows, ['source','year','form','assessment','subject','n','mean','pass_rate','lv2_plus','lv3_plus','lv4_plus','hk_basic_pct','value_added']);
}
function allCases(){return [...D.hkat_cases.map(c=>({source:'HKAT',year:c.year,code:c.code,class_no:'—',type:c.type,metric:c.total,note:c.note})),...D.dse_cases.map(c=>({source:'DSE',year:c.year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note})),...D.exam_cases.map(c=>({source:'校內試',year:'2025/26',code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note,form:c.form,assessment:c.assessment})),...((D.career&&D.career.cases)||[]).map(c=>({source:'升學就業',year:c.grad_year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:(c.outcome||'')+' '+(c.institution||'')+' '+(c.programme||'')+'｜'+(c.note||'')}))]}
function renderCases(){ let rows=allCases(); const t=caseType.value,q=caseSearch.value.toLowerCase(),lim=+caseLimit.value; if(t!=='all') rows=rows.filter(r=>r.type===t); if(q) rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(caseTable, rows.slice(0,lim), ['source','year','form','assessment','code','class_no','type','metric','note']);}
function renderDataTable(){const key=tableSelect.value,q=tableSearch.value.toLowerCase(); let rows=[]; if(key==='career_records') rows=[...((D.career&&D.career.records)||[])]; else if(key==='career_summary') rows=[...((D.career&&D.career.summary)||[])]; else if(key==='career_outcome_by_dse') rows=[...((D.career&&D.career.outcome_by_dse)||[])]; else rows=[...(D[key]||[])]; if(q) rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(dataTable, rows.slice(0,1000));}
window.addEventListener('load',init);
