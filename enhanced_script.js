
const P=JSON.parse(document.getElementById('payload').textContent), D=P.data; let sortState={};
function go(id){document.getElementById(id).scrollIntoView({behavior:'smooth'})}
function uniq(a){return [...new Set(a.filter(x=>x!==null&&x!==undefined&&x!==''))].sort((x,y)=>String(x).localeCompare(String(y),'zh-Hant'))}
function opt(sel, arr, all){sel.innerHTML=(all?`<option value="all">${all}</option>`:'')+arr.map(x=>`<option value="${x}">${x}</option>`).join('')}
function fmt(v){if(v===null||v===undefined||Number.isNaN(v))return '—'; if(typeof v==='number')return (Math.round(v*10)/10).toString(); if(typeof v==='object')return JSON.stringify(v); return v}
function label(c){const m={
 'year':'年度','years':'涵蓋年度','n_years':'有效年度數','latest_year':'最新年度','line':'升留班線','below_line':'低於升留班線人數','below_pct':'低於升留班線百分比','students':'學生人數','average_score':'平均分','min_line':'最低升留班線','max_line':'最高升留班線','avg_line':'平均升留班線','latest_line':'最新升留班線','change_first_latest':'首年至最新變化','grad_year':'畢業年度','dse_year':'DSE年度','cohort':'入學年度','cohort_label':'畢業學年','current_form_2025_26':'2025/26級別','stage':'階段','source':'資料來源','metric':'指標','category':'類別','dimension':'分析維度','count':'人數','pct':'百分比','n':'人數','mean':'平均值','median':'中位數','min':'最低值','max':'最高值','sd':'標準差',
 'class':'班別','class_no':'班別及學號','no':'學號','code':'匿名碼','anon':'匿名碼','中文姓名':'中文姓名','英文姓名':'英文姓名','ename':'英文姓名','cname':'中文姓名',
 'subject':'科目','原科目':'原始科目名稱','form':'級別','assessment':'評估','pass_rate':'合格率','lv2_plus':'第二級或以上百分比','lv3_plus':'第三級或以上百分比','lv4_plus':'第四級或以上百分比','hk_basic_pct':'全港基本水平百分比','school_basic_pct':'學校基本水平百分比','value_added':'增值指標',
 'best5':'DSE最佳五科分數','dse_best5':'DSE最佳五科分數','best5_band':'DSE最佳五科分段','meet3322':'是否達到3322','core_ok':'核心科是否達標','中文':'中文等級','英文':'英文等級','數學':'數學等級','選修2級或以上數目':'選修科達第二級或以上數目',
 'status':'升學／就業狀態','status_raw':'原始升學／就業狀態','level':'課程層級','level_detail':'課程層級（細分學位途徑）','課程層級':'課程層級','pathway':'申請途徑','institution_type':'院校／途徑類型','院校途徑':'院校／途徑類型','institution':'院校','院校':'院校','programme':'課程名稱','課程':'課程名稱','field':'學習／職業範疇','範疇':'學習／職業範疇','location':'升學地區','industry':'行業類別',
 'type':'個案類型','個案類型':'個案類型','note':'備註','解讀':'解讀','outcome':'出路','hkat_total':'HKAT總分','exam_avg':'校內試平均分','match_rate':'匹配率','hkat_n':'HKAT人數','matched_n':'成功匹配人數','hkat_total_mean':'HKAT總分平均','matched_hkat_mean':'成功匹配學生HKAT平均','current_exam_avg_mean':'現時校內試平均','hkat_exam_corr':'HKAT與校內試相關係數','multi_fail_rate':'多科不合格率','multi_fail_3plus':'三科或以上不合格人數',
 'row':'原始列號',
 'course_category_raw':'原始課程類別',
 'basic_n':'達基本水平人數',
 'dse_pass_pct':'相應DSE合格率',
 'u_rate':'U級百分比',
 'nine_value':'九位數值',
 'item':'項目',
 'unit':'單位',
 'value':'數值',
 'dse_class_no':'DSE班別及學號',
 'dse_chi':'DSE中文等級',
 'dse_eng':'DSE英文等級',
 'dse_math':'DSE數學等級',
 'elective2_count':'選修科達第二級或以上數目',
 'hkat_avg':'HKAT平均分',
 'hkat_math':'HKAT數學分數',
 'hkat_eng':'HKAT英文分數',
 'hkat_chi':'HKAT中文分數',
 'fails':'不合格科目數目',
 'n_subjects':'科目數目',
 'matched_records':'成功匹配記錄數目',
 'hkat_students':'HKAT學生人數',
 'exam_records':'校內試記錄數目',
 'unmatched_exam_records':'未匹配校內試記錄數目',
 'available':'是否已提供',
 'definition':'定義',
 'main':'主要指標',
 'n_band':'該分段人數',
 'score':'分數','avg':'平均分','total':'總分','math':'數學分數','english':'英文分數','chinese':'中文分數',
 'class_rank':'班名次',
 'form_rank':'級名次',
 'rank':'名次',
 'sex':'性別',
}; return m[c]||c}

function rangeText(vals, suffix=''){
 vals=[...new Set((vals||[]).filter(v=>v!==null&&v!==undefined&&v!==''))].map(v=>String(v)).sort((a,b)=>a.localeCompare(b,'zh-Hant'));
 if(!vals.length) return '';
 if(vals.length===1) return vals[0]+suffix;
 return vals[0]+'至'+vals[vals.length-1]+suffix;
}
function makeTable(el, rows, cols){ if(!rows||!rows.length){el.innerHTML='<tr><td>沒有符合條件資料</td></tr>'; return} cols=cols||Object.keys(rows[0]); el._rows=rows; el._cols=cols; el.innerHTML='<thead><tr>'+cols.map(c=>`<th onclick="sortTable('${el.id}','${c}')">${label(c)}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>`<td>${fmt(r[c])}</td>`).join('')+'</tr>').join('')+'</tbody>'}
function sortTable(id,c){const el=document.getElementById(id);let rows=[...(el._rows||[])],dir=sortState[id+c]==='asc'?'desc':'asc';sortState[id+c]=dir;rows.sort((a,b)=>{let x=a[c],y=b[c]; if(typeof x==='number'&&typeof y==='number')return dir==='asc'?x-y:y-x; return dir==='asc'?String(x).localeCompare(String(y),'zh-Hant'):String(y).localeCompare(String(x),'zh-Hant')}); makeTable(el,rows,el._cols)}
function lineChart(svg, rows, xKey, yKey, gKey, title){const W=svg.clientWidth||700,H=310,p=42;svg.setAttribute('viewBox',`0 0 ${W} ${H}`);rows=rows.filter(r=>r[yKey]!=null&&!isNaN(+r[yKey])); if(!rows.length){svg.innerHTML='<text x="20" y="35">沒有足夠數據</text>';return};const xs=uniq(rows.map(r=>r[xKey]));const ys=rows.map(r=>+r[yKey]);const ymin=Math.min(...ys),ymax=Math.max(...ys),pad=(ymax-ymin)*.15||1;const xp=x=>p+(xs.indexOf(x)/Math.max(1,xs.length-1))*(W-p*1.7-p);const yp=y=>H-p-((y-(ymin-pad))/(ymax-ymin+pad*2))*(H-p*2);let html=`<text x="${p}" y="22" font-size="13" font-weight="700">${title}</text>`;for(let i=0;i<5;i++){let y=p+i*(H-p*2)/4;html+=`<line x1="${p}" y1="${y}" x2="${W-p}" y2="${y}" stroke="#e6eaf0"/><text x="5" y="${y+4}" font-size="11" fill="#667085">${(ymax+pad-i*(ymax-ymin+pad*2)/4).toFixed(1)}</text>`} const gs=gKey?uniq(rows.map(r=>r[gKey])):[''];const colors=['#1f4fd1','#087443','#b54708','#6941c6','#b42318','#0086a8','#d97706','#475467'];gs.forEach((g,gi)=>{let arr=rows.filter(r=>!gKey||r[gKey]===g).sort((a,b)=>xs.indexOf(a[xKey])-xs.indexOf(b[xKey]));let pts=arr.map(r=>[xp(r[xKey]),yp(+r[yKey]),r]); if(pts.length>1)html+=`<polyline fill="none" stroke="${colors[gi%colors.length]}" stroke-width="3" points="${pts.map(p=>p[0]+','+p[1]).join(' ')}"/>`; pts.forEach(pt=>html+=`<circle cx="${pt[0]}" cy="${pt[1]}" r="4" fill="${colors[gi%colors.length]}"><title>${g} ${pt[2][xKey]}: ${fmt(pt[2][yKey])}</title></circle>`); if(gKey)html+=`<text x="${W-170}" y="${42+gi*16}" font-size="12" fill="${colors[gi%colors.length]}">● ${g}</text>`}); xs.forEach(x=>html+=`<text x="${xp(x)-10}" y="${H-12}" font-size="10" fill="#667085" transform="rotate(-20 ${xp(x)} ${H-12})">${String(x).slice(0,14)}</text>`); svg.innerHTML=html}
function barChart(svg, rows, labelKey, valueKey, title){
 const W=svg.clientWidth||760; rows=rows.filter(r=>r[valueKey]!=null).slice(0,12);
 const rowH=34, top=44, bottom=24, left=190, right=58;
 const H=Math.max(310, top+bottom+rows.length*rowH);
 svg.style.height=H+'px'; svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
 if(!rows.length){svg.innerHTML='<text x="20" y="35" font-size="14">沒有足夠數據</text>';return}
 const max=Math.max(...rows.map(r=>+r[valueKey]),1);
 let html=`<text x="18" y="24" font-size="15" font-weight="700" fill="#172033">${title}</text>`;
 html+=`<line x1="${left}" y1="${top-8}" x2="${W-right}" y2="${top-8}" stroke="#e6eaf0"/>`;
 rows.forEach((r,i)=>{
   const y=top+i*rowH;
   const labelText=String(r[labelKey]??'未分類');
   const short=labelText.length>18?labelText.slice(0,18)+'…':labelText;
   const barW=Math.max(2,(+r[valueKey]/max)*(W-left-right));
   const color=['#1f4fd1','#087443','#b54708','#6941c6','#0086a8','#d97706','#b42318','#475467'][i%8];
   html+=`<text x="${left-10}" y="${y+18}" font-size="13" text-anchor="end" fill="#172033"><title>${labelText}</title>${short}</text>`;
   html+=`<rect x="${left}" y="${y+3}" width="${barW}" height="22" rx="6" fill="${color}"><title>${labelText}: ${fmt(r[valueKey])}</title></rect>`;
   html+=`<text x="${Math.min(W-right+4,left+barW+8)}" y="${y+19}" font-size="13" font-weight="700" fill="#172033">${fmt(r[valueKey])}</text>`;
   html+=`<line x1="${left}" y1="${y+31}" x2="${W-right}" y2="${y+31}" stroke="#f0f2f5"/>`;
 });
 svg.innerHTML=html;
}
function allCases(){return [...(D.hkat_cases||[]).map(c=>({source:'HKAT',year:c.year,code:c.code,class_no:'—',type:c.type,metric:c.total,note:c.note})),...(D.dse_cases||[]).map(c=>({source:'DSE',year:c.year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note})),...(D.exam_cases||[]).map(c=>({source:'校內試',year:'2025/26',code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note})),...((D.longitudinal&&D.longitudinal.longitudinal_cases)||[]).map(c=>({source:'縱向追蹤',year:c.cohort,code:c.code,class_no:c.class_no,type:c.type,metric:c.exam_avg,note:c.note})),...((D.career&&D.career.cases)||[]).map(c=>({source:'升學就業',year:c.grad_year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:(c.outcome||'')+' '+(c.institution||'')+' '+(c.programme||'')+'｜'+(c.note||'')}))]}
function init(){const C=D.career||{records:[],linked_records:[],cases:[]}, L=D.longitudinal||{}; k1.textContent=C.records.length; k2.textContent=C.linked_records.length; k3.textContent=L.matched_records||0; k4.textContent=allCases().length; opt(insTheme,uniq(P.insights.map(x=>x.theme)),'全部主題'); renderInsights(); opt(hkatSub,uniq(D.hkat.map(r=>r.subject))); hkatSub.value='中文'; drawHKAT(); drawCareerTop(); opt(careerYear,uniq(C.records.map(r=>r.grad_year)),'全部年度'); renderCareer(); renderCareerExplanation(); renderUniInit(); renderPromotion(); const subs=uniq((D.dse_subject||[]).map(r=>r.subject)); opt(subjectSel,subs); subjectSel.value=subs.includes('英文')?'英文':subs[0]; renderSubject(); document.getElementById('strategies').innerHTML=P.strategies.map(s=>`<div class="span4 strategy"><span class="tag purple">${s.lens}</span><h3>${s.question}</h3><p><b>可用數據：</b>${s.use}</p><p><b>決策：</b>${s.decision}</p></div>`).join(''); opt(caseType,uniq(allCases().map(c=>c.type)),'全部類型'); renderCases(); renderData();}
function renderInsights(){let t=insTheme.value,q=insSearch.value.toLowerCase();let arr=P.insights.filter(x=>(t==='all'||x.theme===t)&&(!q||JSON.stringify(x).toLowerCase().includes(q))).slice(0,60); insights.innerHTML=arr.map(x=>`<div class="report-block"><span class="tag">${x.theme}</span><span class="tag good">${x.area}</span><br><b>${x.title}</b><br>${x.detail}<br><span class="muted">建議：${x.action}</span></div>`).join('')}
function drawHKAT(){let rows=D.hkat.filter(r=>r.subject===hkatSub.value); lineChart(hkatChart,rows,'year','mean',null,hkatSub.value+' HKAT平均分（'+rangeText(rows.map(r=>r.year))+'）')}
function drawCareerTop(){const C=D.career||{summary:[],records:[]}; let y=Math.max(...C.records.map(r=>r.grad_year).filter(Boolean)); let dim=careerDimTop.value; let rows=C.summary.filter(r=>r.grad_year===y&&r.dimension===dim).sort((a,b)=>b.count-a.count).map(r=>({label:r.category,value:r.count})); barChart(careerTopChart,rows,'label','value',y+'年出路分佈')}

function renderCareerExplanation(){
 const el=document.getElementById('careerExplanation'); if(!el) return;
 el.innerHTML=`
 <div class="span4 strategy"><span class="tag">一、Best5分段的意義</span><p>DSE Best5是學生最佳五科成績的總和，可用作概括學生整體公開試表現。本報告把Best5分為0–9、10–14、15–19及20+，目的不是為學生貼標籤，而是分析不同成績組別的實際升學路徑。</p><p><b>解讀重點：</b>若Best5較高組別集中進入本科，代表高成就學生的升學銜接較清晰；若中間組別分散於本科、副學士及高級文憑，則顯示該組學生最需要精準的升學策略。</p></div>
 <div class="span4 strategy"><span class="tag good">二、3322門檻的意義</span><p>3322通常指中文、英文達第3級，數學及其他科目達第2級，是本地本科升學的重要參考門檻之一。本報告把「3322達標」與「3322未達標」學生的實際出路分開比較。</p><p><b>解讀重點：</b>若3322達標學生多進入本科，反映核心科達標對升學有明顯影響；若未達3322學生仍能透過副學士、高級文憑、VTC或DAE延續升學，則可作多元升學路徑的具體例證。</p></div>
 <div class="span4 strategy"><span class="tag purple">三、出路類別的分拆</span><p>本報告已將學位課程進一步分為JUPAS／SSSDP及Non-JUPAS／自資／其他路徑，並同時分開副學士及高級文憑，避免把不同層級及不同入學途徑的專上課程混合分析。</p><p><b>解讀重點：</b>副學士通常較偏向升讀學位銜接；高級文憑較多與專業技能或職業導向相關。兩者對學生未來路徑的意義不同，應分開檢視。</p></div>
 <div class="span6 strategy"><span class="tag warn">四、學校層面的啟示</span><p>圖表可協助學校把升學輔導由「放榜後支援」提前至高中階段。Best5 20+學生可聚焦JUPAS、SSSDP、面試及學科配對；Best5 15–19學生宜同時準備本科及副學士／高級文憑方案；Best5 10–14及未達3322學生則需要及早認識VTC、DAE、職專、重讀及就業再進修等路徑。</p></div>
 <div class="span6 strategy"><span class="tag bad">五、個案跟進角度</span><p>圖表亦有助找出值得深入了解的特殊個案，例如：高Best5但未進入本科、未達3322但成功進入本科或學位路徑、低Best5但有清晰專業出路。這些個案可分別用於檢視升學策略、總結成功因素及優化個別輔導。</p></div>`;
}

function renderCareer(){const C=D.career||{records:[],linked_records:[],summary:[],outcome_by_dse:[]};let y=careerYear.value,dim=careerDim.value,q=careerSearch.value.toLowerCase();let rec=C.records.filter(r=>(y==='all'||String(r.grad_year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));let linked=(C.linked_records||[]).filter(r=>(y==='all'||String(r.grad_year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));let counts={};rec.forEach(r=>counts[r[dim]]=(counts[r[dim]]||0)+1);barChart(careerChart,Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([label,value])=>({label,value})),'label','value','出路分佈（'+(y==='all'?rangeText((C.records||[]).map(r=>r.grad_year),'年'):y+'年')+'）');let by=C.outcome_by_dse.filter(r=>r.dimension==='level_detail'&&['0-9','10-14','15-19','20+'].includes(r.best5_band));barChart(dseOutcomeChart,by.filter(r=>['學位課程（JUPAS/SSSDP）','學位課程（Non-JUPAS/自資/其他）','副學士','高級文憑','文憑/基礎/職專'].includes(r.category)).map(r=>({label:r.best5_band+' '+r.category,value:r.count})),'label','value','不同DSE成績組別的主要畢業出路（'+rangeText((C.linked_records||[]).map(r=>r.grad_year),'年')+'）'); renderHeat(by); makeTable(careerRecordTable, linked.slice(0,500), ['grad_year','anon','class','status','level','institution_type','institution','programme','field','dse_best5','meet3322']);}
function renderHeat(rows){let bands=['0-9','10-14','15-19','20+','3322達標','3322未達標']; let cats=uniq(rows.concat((D.career||{outcome_by_dse:[]}).outcome_by_dse).filter(r=>r.dimension==='level_detail').map(r=>r.category)).slice(0,6); let all=(D.career||{outcome_by_dse:[]}).outcome_by_dse.filter(r=>r.dimension==='level_detail'); let html='<div class="heat-row"><div class="heat-cell heat-head">出路 / 成績</div>'+bands.map(b=>`<div class="heat-cell heat-head">${b}</div>`).join('')+'</div>'; cats.forEach(cat=>{html+=`<div class="heat-row"><div class="heat-cell heat-head">${cat}</div>`+bands.map(b=>{let r=all.find(x=>x.best5_band===b&&x.category===cat); let val=r?r.pct:0; let alpha=Math.min(.95,(val||0)/100+.08); return `<div class="heat-cell" style="background:rgba(31,79,209,${alpha});color:${alpha>.45?'#fff':'#172033'}"><b>${fmt(val)}%</b><br><span>${r?r.count:0}人</span></div>`}).join('')+'</div>'}); heatmap.innerHTML=html}

function renderUniInit(){
 const U=P.uni||{records:[],summary:[],trend:[],cases:[]}; if(!document.getElementById('uniYear')) return;
 uniDef.textContent=U.definition||'';
 opt(uniYear, uniq((U.records||[]).map(r=>r.year)), '全部年度');
 renderUni();
}
function renderUni(){
 const U=P.uni||{records:[],summary:[],trend:[],cases:[]};
 const y=uniYear.value, dim=uniDim.value, q=uniSearch.value.toLowerCase();
 let rec=(U.records||[]).filter(r=>(y==='all'||String(r.year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));
 makeTable(uniRecordTable, rec.slice(0,300), ['year','class','no','中文姓名','英文姓名','best5','中文','英文','數學','選修2級或以上數目','課程層級','院校途徑','院校','課程','範疇']);
 let cases=(U.cases||[]).filter(r=>(y==='all'||String(r.year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));
 makeTable(uniCaseTable, cases.slice(0,120), ['year','class','no','中文姓名','英文姓名','個案類型','best5','中文','英文','數學','課程層級','院校','課程','解讀']);
}



function coreEquivalent(subj){
 if(subj==='中文' || subj==='中國語文' || subj==='Ch Lang') return {hkat:'中文',tsa:'中國語文',exam:['中文','中國語文'],dse:['中文','中國語文','Ch Lang']};
 if(subj==='英文' || subj==='Eng Lang') return {hkat:'英文',tsa:'英文',exam:['英文','English'],dse:['英文','Eng Lang']};
 if(subj==='數學' || subj==='Maths') return {hkat:'數學',tsa:'數學',exam:['數學','Maths'],dse:['數學','Maths']};
 return {hkat:null,tsa:null,exam:[subj],dse:[subj]};
}
function subjectMatch(value, list){return list.some(x=>String(value)===String(x))}

function aggregateExamSubject(subj){
 const groups={}; const eq=coreEquivalent(subj);
 (D.exam||[]).filter(r=>subjectMatch(r.subject,eq.exam)).forEach(r=>{
   const y=r.year||'未列年度';
   if(!groups[y]) groups[y]={source:'校內試',year:y,subject:subj,n:0,mean_num:0,mean_den:0,pass_num:0,pass_den:0,forms:new Set(),assessments:new Set()};
   const g=groups[y], n=Number(r.n)||0;
   g.n+=n; if(r.form) g.forms.add(r.form); if(r.assessment) g.assessments.add(r.assessment);
   if(r.mean!==null&&r.mean!==undefined&&n){g.mean_num+=Number(r.mean)*n; g.mean_den+=n;}
   if(r.pass_rate!==null&&r.pass_rate!==undefined&&n){g.pass_num+=Number(r.pass_rate)*n; g.pass_den+=n;}
 });
 return Object.values(groups).map(g=>{
   const mean=g.mean_den?Math.round((g.mean_num/g.mean_den)*10)/10:null;
   const pass=g.pass_den?Math.round((g.pass_num/g.pass_den)*10)/10:null;
   return {source:'校內試',year:g.year,subject:g.subject,n:g.n,mean:mean,pass_rate:pass,form:[...g.forms].sort().join('、'),assessment:'全年綜合',main:pass!==null?pass:mean};
 }).sort((a,b)=>String(a.year).localeCompare(String(b.year),'zh-Hant'));
}


function renderPromotion(){
 const Pm=D.promotion_line||{records:[],summary:[],below_line_2025_26:[]}; if(!document.getElementById('promotionHeatmap')) return;
 const years=uniq(Pm.records.map(r=>r.year)); const forms=uniq(Pm.records.map(r=>r.form));
 const vals=Pm.records.filter(r=>r.line!==null&&r.line!==undefined).map(r=>Number(r.line)); const min=Math.min(...vals), max=Math.max(...vals);
 const gridCols=`140px repeat(${years.length}, minmax(92px, 1fr))`;
 const minWidth=140+years.length*100;
 const rowStyle=`grid-template-columns:${gridCols};min-width:${minWidth}px`;
 let html='<div class="promotion-legend"><b>閱讀方法：</b><span>顏色越深代表升留班線越高</span><span class="promotion-swatch" style="background:rgba(31,79,209,.18)"></span><span>較低</span><span class="promotion-swatch" style="background:rgba(31,79,209,.85)"></span><span>較高</span></div>';
 html+='<div class="heat-row" style="'+rowStyle+'"><div class="heat-cell heat-head">級別 / 年度</div>'+years.map(y=>`<div class="heat-cell heat-head">${y}</div>`).join('')+'</div>';
 forms.forEach(f=>{
   html+=`<div class="heat-row" style="${rowStyle}"><div class="heat-cell heat-head">${f}</div>`+years.map(y=>{
     let r=Pm.records.find(x=>x.year===y&&x.form===f);
     if(!r) return '<div class="heat-cell">—</div>';
     if(r.line===null||r.line===undefined) return `<div class="heat-cell" style="background:#f8fafc;color:#667085;font-size:12px">${r.note||'—'}</div>`;
     let alpha=.16+(Number(r.line)-min)/(max-min||1)*.72;
     return `<div class="heat-cell" style="background:rgba(31,79,209,${alpha});color:${alpha>.48?'#fff':'#172033'}"><b>${fmt(r.line)}</b></div>`;
   }).join('')+'</div>';
 });
 promotionHeatmap.innerHTML=html;
 makeTable(promotionSummaryTable, Pm.summary||[], ['form','years','n_years','min_line','max_line','avg_line','latest_year','latest_line','change_first_latest']);
 makeTable(promotionBelowTable, Pm.below_line_2025_26||[], ['year','form','assessment','line','students','below_line','below_pct','average_score']);
 const latest=(Pm.summary||[]).map(r=>`${r.form}最新升留班線為${fmt(r.latest_line)}分，較首年變化${fmt(r.change_first_latest)}分`).join('；');
 const below=(Pm.below_line_2025_26||[]).sort((a,b)=>(b.below_pct||0)-(a.below_pct||0)).slice(0,5).map(r=>`${r.form} ${r.assessment}低於線比例${fmt(r.below_pct)}%`).join('；');
 promotionText.innerHTML=`<div class="report-block"><b>多年趨勢：</b>${latest}。</div><div class="report-block"><b>2025/26風險提示：</b>${below}。此比例只反映以現時校內試平均分與升留班線作初步比較，實際升留班決定仍需結合學生全年表現、操行、出席及教師專業判斷。</div>`;
}

function renderSubject(){
 let s=subjectSel.value,src=subjectSrc.value,q=subjectQ.value.toLowerCase(),rows=[];
 const eq=coreEquivalent(s);
 if(src==='all'||src==='hkat'){
   if(eq.hkat) rows.push(...D.hkat.filter(r=>r.subject===eq.hkat).map(r=>({source:'HKAT入學基線',year:r.year,subject:s,原科目:r.subject,n:r.n,mean:r.mean,main:r.mean})));
 }
 if(src==='all'||src==='tsa'){
   if(eq.tsa) rows.push(...D.tsa.filter(r=>r.subject===eq.tsa).map(r=>({source:'TSA初中基礎',year:r.year,subject:s,原科目:r.subject,n:r.n,mean:r.school_basic_pct,main:r.school_basic_pct,hk_basic_pct:r.hk_basic_pct,value_added:r.value_added})));
 }
 if(src==='all'||src==='exam') rows.push(...aggregateExamSubject(s).map(r=>({...r,source:'校內試年度綜合',subject:s})));
 if(src==='all'||src==='dse') rows.push(...D.dse_subject.filter(r=>subjectMatch(r.subject,eq.dse)).map(r=>({source:'DSE公開試',year:r.year,subject:s,原科目:r.subject,n:r.n,mean:r.mean,lv2_plus:r.lv2_plus,lv3_plus:r.lv3_plus,lv4_plus:r.lv4_plus,main:r.lv2_plus})));
 if(q)rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q));
 const years=rangeText(rows.map(r=>String(r.year).split(' ')[0]));
 subjectText.innerHTML=`<div class="report-block"><b>${s}</b><br>本部分只以DSE有成績的科目作選項，並把同名或等同科目的資料配對。表格列出DSE Level 2+、Level 3+、Level 4+、平均等級，以及校內試年度綜合表現；校內試已按年度綜合計算。中文、英文及數學會額外顯示HKAT及TSA基礎資料，其他選修科則主要比較校內試與DSE表現。</div>`;
 makeTable(subjectTable,rows,['source','year','subject','原科目','n','mean','pass_rate','lv2_plus','lv3_plus','lv4_plus','hk_basic_pct','value_added']);
}

function renderCases(){let rows=allCases(),src=caseSource.value,t=caseType.value,q=caseQ.value.toLowerCase(),n=+caseN.value; if(src!=='all')rows=rows.filter(r=>r.source===src); if(t!=='all')rows=rows.filter(r=>r.type===t); if(q)rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(caseTable,rows.slice(0,n),['source','year','code','class_no','type','metric','note'])}
function getPath(obj,path){return path.split('.').reduce((o,k)=>o&&o[k],obj)}
function renderData(){let rows=[]; if(dataSel.value==='university_minimum.records') rows=[...((P.uni&&P.uni.records)||[])]; else if(dataSel.value==='university_minimum.summary') rows=[...((P.uni&&P.uni.summary)||[])]; else if(dataSel.value==='promotion_line.records') rows=[...((D.promotion_line&&D.promotion_line.records)||[])]; else if(dataSel.value==='promotion_line.below_line_2025_26') rows=[...((D.promotion_line&&D.promotion_line.below_line_2025_26)||[])]; else rows=[...(getPath(D,dataSel.value)||[])]; let q=dataQ.value.toLowerCase(); if(q)rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(dataTable,rows.slice(0,1000))}
window.addEventListener('load',init);
