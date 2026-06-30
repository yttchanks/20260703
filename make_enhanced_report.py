import json, re, math
from collections import Counter, defaultdict
from pathlib import Path
D=json.load(open('/home/user/analysis_output/analysis_data.json',encoding='utf-8'))

def sanitize_for_report(obj):
    sensitive={'cname','ename','strn','student_name','學生中文全名','學生聯絡電話(可選擇填寫)','phone','電話'}
    if isinstance(obj, dict):
        return {k:sanitize_for_report(v) for k,v in obj.items() if k not in sensitive}
    if isinstance(obj, list):
        return [sanitize_for_report(x) for x in obj]
    return obj

def pct(a,b): return round(100*a/b,1) if b else None

def fmt(v):
    if v is None: return '—'
    if isinstance(v,float): return str(round(v,1))
    return str(v)

# Precompute richer insights based only on available datasets
insights=[]
# HKAT trends
for subj in sorted(set(r['subject'] for r in D.get('hkat',[]))):
    arr=sorted([r for r in D['hkat'] if r['subject']==subj and r.get('mean') is not None], key=lambda x:x['year'])
    if len(arr)>=2:
        change=round(arr[-1]['mean']-arr[0]['mean'],2)
        direction='上升' if change>0 else '下降' if change<0 else '持平'
        insights.append({'theme':'入學基線','area':subj,'title':f'{subj}入學基線{direction}', 'detail':f"{arr[0]['year']} 至 {arr[-1]['year']} 平均分由 {arr[0]['mean']} 變為 {arr[-1]['mean']}（{change:+.2f}）。", 'action':'用作中一分層、暑期銜接及首學期補底/拔尖分組。'})
# TSA available
for subj in sorted(set(r['subject'] for r in D.get('tsa',[]) if 'SEN' not in r['subject'])):
    arr=sorted([r for r in D['tsa'] if r['subject']==subj and r.get('school_basic_pct') is not None and 'SEN' not in r['subject']], key=lambda x:x['year'])
    if arr:
        last=arr[-1]
        gap=None
        if last.get('hk_basic_pct') is not None: gap=round(last['school_basic_pct']-last['hk_basic_pct'],1)
        insights.append({'theme':'中三基礎能力','area':subj,'title':f'{subj} TSA基本水平', 'detail':f"{last['year']} 學校基本水平 {last['school_basic_pct']}%"+(f"，較全港 {gap:+.1f}百分點。" if gap is not None else '。'), 'action':'把TSA弱項回饋至S1-S3課程地圖及共同備課。'})
# DSE recent subject lows/highs
recent=max([r['year'] for r in D.get('dse_subject',[])], default=None)
if recent:
    arr=[r for r in D['dse_subject'] if r['year']==recent and r.get('lv2_plus') is not None]
    for r in sorted(arr,key=lambda x:x['lv2_plus'])[:6]:
        insights.append({'theme':'DSE達標','area':r['subject'],'title':f"{recent} {r['subject']}達標關注", 'detail':f"Level 2+ {r['lv2_plus']}%，Level 3+ {fmt(r.get('lv3_plus'))}%，Level 4+ {fmt(r.get('lv4_plus'))}%。", 'action':'按卷別/班組拆解，設定邊緣學生清單及考前8週策略。'})
# Internal exam lows
exam2=[r for r in D.get('exam',[]) if r.get('assessment')=='Exam2' and r.get('pass_rate') is not None]
for r in sorted(exam2,key=lambda x:x['pass_rate'])[:8]:
    insights.append({'theme':'校內評估','area':f"{r['form']} {r['subject']}", 'title':'合格率優先跟進', 'detail':f"Exam2 合格率 {r['pass_rate']}%，平均分 {fmt(r.get('mean'))}。", 'action':'檢視題目藍圖、錯題類型及跨科功課/測驗負荷。'})
# Career insights
C=D.get('career',{})
records=C.get('records',[]); linked=C.get('linked_records',[])
if records:
    for y in sorted(set(r['grad_year'] for r in records)):
        arr=[r for r in records if r['grad_year']==y]
        top=Counter(r['level'] for r in arr).most_common(3)
        insights.append({'theme':'升學就業','area':str(y),'title':f'{y}畢業出路結構', 'detail':'、'.join([f'{k} {v}人({pct(v,len(arr))}%)' for k,v in top]), 'action':'按主要去向設計升學講座、院校參觀及個別諮詢資源。'})
    # DSE band insights
    for band in ['20+','15-19','10-14','0-9','3322達標','3322未達標']:
        arr=[r for r in C.get('outcome_by_dse',[]) if r.get('best5_band')==band and r.get('dimension')=='level']
        if arr:
            top=sorted(arr,key=lambda x:x['count'],reverse=True)[:3]
            insights.append({'theme':'DSE→出路','area':band,'title':f'DSE {band} 主要出路', 'detail':'、'.join([f"{r['category']} {r['pct']}%" for r in top]), 'action':'把成績段與出路路徑轉化為學生/家長可理解的選項地圖。'})
# Longitudinal
L=D.get('longitudinal',{})
for r in L.get('cohort_tracking',[]):
    if r.get('stage','').endswith('Exam1') or 'Exam1' in r.get('stage',''):
        if r.get('hkat_exam_corr') is not None:
            insights.append({'theme':'縱向追蹤','area':r['cohort'], 'title':f"{r['cohort']} 入學基線與現時表現", 'detail':f"成功匹配 {r['matched_n']} 人，HKAT與現時考試相關係數 {r['hkat_exam_corr']}，多科不合格率 {fmt(r.get('multi_fail_rate'))}%。", 'action':'把低基線高進步、高基線下滑、持續支援三類學生分開處理。'})

# Strategy cards
strategies=[
 {'lens':'學生發展路徑','question':'學生由入學到畢業，在哪個階段最需要轉介或加速？','use':'HKAT低基線、TSA基本水平、校內試多科不合格、DSE邊緣、畢業出路。','decision':'建立每學期一次的「學生路徑會議」，每級選出補底、拔尖、轉折風險三張清單。'},
 {'lens':'課程與評估','question':'科目成績問題是基礎能力、評估設計，還是學習動機？','use':'HKAT分項、TSA、校內試合格率、DSE Level 2+/3+/4+。','decision':'科組以同一指標追蹤三年，不只看單次考試；低合格率科目要提交錯題及重教計劃。'},
 {'lens':'升學策略','question':'不同DSE成績段最實際的升學路徑是什麼？','use':'Best5 band、3322、課程層級、院校途徑、課程範疇。','decision':'為Best5 20+、15-19、10-14、0-9建立不同升學包：JUPAS/SSSDP、本科、 副學士、高級文憑、VTC/DAE、就業及再進修。'},
 {'lens':'資源投放','question':'支援資源應該投向哪一級、哪一科、哪一類學生？','use':'多科不合格率、DSE低達標科目、TSA差距、出路個案。','decision':'用數據排優先次序：先處理跨科風險，再處理單科邊緣，最後做拔尖延展。'},
 {'lens':'家校及學生溝通','question':'如何令學生及家長理解「成績—選擇—出路」？','use':'DSE與出路連結、熱門院校/課程、成功個案類型。','decision':'把真實出路數據轉成家長晚會圖像，展示多元但有門檻的升學路徑。'}
]

enhanced={'data':sanitize_for_report(D),'uni':D.get('university_minimum',{}),'insights':insights,'strategies':strategies}
js=json.dumps(enhanced,ensure_ascii=False).replace('</','<\\/')

html=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>學校年度檢討深度互動報告</title>
<style>
:root{{--bg:#f5f7fb;--card:#fff;--ink:#172033;--muted:#667085;--pri:#1f4fd1;--pri2:#eef3ff;--line:#e6eaf0;--good:#087443;--warn:#b54708;--bad:#b42318;--purple:#6941c6;--shadow:0 8px 26px rgba(16,24,40,.08)}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans TC","PingFang TC","Microsoft JhengHei",Arial,sans-serif}} header{{background:linear-gradient(135deg,#102a73,#2364d2 55%,#57a7ff);color:#fff;padding:26px 30px 18px;position:sticky;top:0;z-index:10;box-shadow:0 6px 20px rgba(20,40,90,.2)}} h1{{margin:0 0 8px;font-size:28px}} .sub{{font-size:14px;opacity:.95;line-height:1.55}} .nav{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}} .nav button,.btn{{border:0;background:rgba(255,255,255,.17);color:#fff;border-radius:999px;padding:8px 12px;cursor:pointer;font-weight:700}} .nav button:hover{{background:rgba(255,255,255,.28)}}
.wrap{{max-width:1440px;margin:0 auto;padding:18px}} .grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}} .card{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:16px;box-shadow:var(--shadow)}} .kpi{{grid-column:span 3}} .kpi b{{font-size:27px;color:#153e9f;display:block}} .kpi span{{font-size:13px;color:var(--muted)}} .span3{{grid-column:span 3}} .span4{{grid-column:span 4}} .span5{{grid-column:span 5}} .span6{{grid-column:span 6}} .span7{{grid-column:span 7}} .span8{{grid-column:span 8}} .span9{{grid-column:span 9}} .span12{{grid-column:span 12}}
h2{{font-size:20px;margin:0 0 12px}} h3{{font-size:16px;margin:12px 0 8px}} p,li{{line-height:1.58}} .muted{{color:var(--muted)}} .small{{font-size:12px;color:var(--muted)}} .section{{scroll-margin-top:120px;margin-bottom:15px}}
.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:8px 0 12px}} select,input{{border:1px solid #cfd5e1;border-radius:10px;padding:9px 10px;background:#fff;min-width:150px}} input{{min-width:230px}} .action{{background:var(--pri);color:#fff;border-radius:10px;padding:9px 13px;border:0;cursor:pointer}}
.tag{{display:inline-block;border-radius:999px;padding:4px 9px;margin:2px;background:var(--pri2);color:#173b8f;font-size:12px;font-weight:700}} .tag.good{{background:#eafaf2;color:var(--good)}} .tag.warn{{background:#fff4e5;color:var(--warn)}} .tag.bad{{background:#fff1f1;color:var(--bad)}} .tag.purple{{background:#f3efff;color:var(--purple)}}
.report-block{{border-left:4px solid var(--pri);background:#f8fbff;border-radius:12px;padding:11px 13px;margin:9px 0}} .strategy{{border:1px solid var(--line);border-radius:14px;padding:13px;background:linear-gradient(#fff,#fbfdff)}}
.tablewrap{{max-height:480px;overflow:auto;border:1px solid var(--line);border-radius:12px}} table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{padding:9px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}} th{{background:#f8fafc;position:sticky;top:0;cursor:pointer;z-index:2}} tr:hover td{{background:#fbfdff}}
.svgbox{{width:100%;height:310px;border:1px solid var(--line);border-radius:13px;background:linear-gradient(#fff,#fbfcff)}} .tabs{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}} .tabs button{{border:1px solid #d7deea;background:#fff;border-radius:999px;padding:8px 12px;cursor:pointer}} .tabs button.active{{background:var(--pri);color:#fff;border-color:var(--pri)}}
.heat{{display:grid;gap:4px}} .heat-row{{display:grid;grid-template-columns:150px repeat(6,1fr);gap:4px;align-items:stretch}} .heat-cell{{padding:8px;border-radius:8px;background:#eef3ff;font-size:12px;min-height:36px}} .heat-head{{font-weight:700;background:#f8fafc}} .path-card{{border:1px solid var(--line);border-radius:14px;padding:12px;margin:8px 0;background:#fff}} .path-card b{{color:#153e9f}}

.promotion-heat{{overflow-x:auto;padding-bottom:8px}}
.promotion-heat .heat-row{{gap:6px;margin-bottom:6px}}
.promotion-heat .heat-cell{{min-height:48px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:13px;line-height:1.25;border:1px solid #e6eaf0}}
.promotion-heat .heat-head{{font-weight:800;background:#f8fafc;color:#172033}}
.promotion-legend{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px;color:#667085;font-size:13px}}
.promotion-swatch{{width:34px;height:14px;border-radius:6px;display:inline-block;border:1px solid #d0d5dd}}

@media(max-width:950px){{.kpi,.span3,.span4,.span5,.span6,.span7,.span8,.span9,.span12{{grid-column:span 12}} header{{position:static}} .heat-row{{grid-template-columns:1fr}}}}
@media print{{header,.controls,.nav,.tabs{{display:none}} body{{background:#fff}} .card{{box-shadow:none;break-inside:avoid}} .tablewrap{{max-height:none;overflow:visible}}}}
</style></head><body>
<header><h1>學校年度檢討深度互動報告</h1><div class="sub">聚焦已整理及可分析資料：HKAT、TSA、校內試、DSE、畢業生升學及就業出路。報告以匿名方式呈現個案，支援科組、部門及學校層面決策。</div><div class="nav"><button onclick="go('dash')">總覽</button><button onclick="go('career')">升學就業</button><button onclick="go('uni')">大學入學資格</button><button onclick="go('promotion')">升留班線</button><button onclick="go('subject')">科目分析</button><button onclick="go('strategy')">策略矩陣</button><button onclick="go('cases')">個案線索</button><button onclick="go('data')">數據表</button><button onclick="window.print()">列印/PDF</button></div></header>
<div class="wrap">
<section id="dash" class="section grid"><div class="card kpi"><b id="k1">—</b><span>畢業生出路回覆</span></div><div class="card kpi"><b id="k2">—</b><span>已連結DSE出路記錄</span></div><div class="card kpi"><b id="k3">—</b><span>縱向追蹤匹配評估記錄</span></div><div class="card kpi"><b id="k4">—</b><span>可行動個案線索</span></div><div class="card span8"><h2>多角度重點洞察</h2><div class="controls"><select id="insTheme" onchange="renderInsights()"><option value="all">全部主題</option></select><input id="insSearch" placeholder="搜尋洞察..." oninput="renderInsights()"></div><div id="insights"></div></div><div class="card span4"><h2>年度檢討閱讀方法</h2><div class="report-block"><b>第一步：先看學生路徑。</b><br>由入學基線、初中基礎能力、高中校內表現、DSE結果至畢業出路，判斷學生在不同階段的轉折點。</div><div class="report-block"><b>第二步：再看學生類型。</b><br>把學生分為基礎支援、邊緣達標、拔尖高潛能及出路規劃四類，避免只以單一平均分作判斷。</div><div class="report-block"><b>第三步：最後轉化為行動。</b><br>把分析結果落實至科組KPI、支援名單、生涯規劃活動、家長溝通及下年度資源分配。</div></div><div class="card span6"><h2>入學基線趨勢（HKAT 2021-22至2025-26）</h2><div class="controls"><select id="hkatSub" onchange="drawHKAT()"></select></div><svg id="hkatChart" class="svgbox"></svg><div class="report-block"><b>解讀方法：</b>此圖顯示不同年度中一入學學生在HKAT相關科目的平均表現。上升或下降趨勢可反映入學基礎的變化，並可用作中一分層教學、銜接課程及早期支援名單的依據。</div></div><div class="card span6"><h2>最新畢業出路分佈（2025年畢業生）</h2><div class="controls"><select id="careerDimTop" onchange="drawCareerTop()"><option value="level_detail">課程層級（細分學位途徑）</option><option value="level">課程層級</option><option value="institution_type">院校/途徑</option><option value="field">範疇</option><option value="pathway">申請途徑</option></select></div><svg id="careerTopChart" class="svgbox"></svg><div class="report-block"><b>解讀方法：</b>此圖聚焦最近一屆畢業生的主要出路。切換「課程層級」、「院校／途徑」、「範疇」或「申請途徑」，可分別觀察學生最常進入的升學層級、院校類型及專業方向。</div></div></section>

<section id="career" class="section grid"><div class="card span12"><h2>升學及就業深度分析（2022至2025年畢業生）</h2><div class="grid"><div class="span4"><div class="report-block"><b>分析目的：</b>把畢業生實際出路與DSE成績連結，了解不同成績組別學生的升學及就業路徑。</div></div><div class="span4"><div class="report-block"><b>閱讀方法：</b>先按年度及出路類別觀察整體分佈，再以Best5及3322檢視成績門檻對出路的影響。</div></div><div class="span4"><div class="report-block"><b>應用方法：</b>把結果轉化為高中升學輔導分層方案，包括本科、副學士、高級文憑、VTC、DAE、重讀及就業再進修路徑。</div></div></div><div class="controls"><select id="careerYear" onchange="renderCareer()"><option value="all">全部年度</option></select><select id="careerDim" onchange="renderCareer()"><option value="level_detail">課程層級（細分學位途徑）</option><option value="level">課程層級</option><option value="institution_type">院校/途徑</option><option value="field">學習/職業範疇</option><option value="status">升學/就業狀態</option><option value="location">地區</option></select><input id="careerSearch" placeholder="搜尋院校/課程/範疇..." oninput="renderCareer()"></div></div><div class="card span6"><h2>出路分佈</h2><svg id="careerChart" class="svgbox"></svg><div class="report-block"><b>解讀方法：</b>此圖顯示所選年度及分類維度下，畢業生集中於哪些出路。若某一類別比例偏高，學校可檢視相關升學資訊、院校連繫及家長教育是否需要加強。</div></div><div class="card span6"><h2>不同DSE成績組別的畢業出路分佈</h2><svg id="dseOutcomeChart" class="svgbox"></svg><div class="report-block"><b>解讀方法：</b>此圖比較Best5不同分段學生的主要出路。它可協助判斷哪一個成績組別最需要升學策略支援，例如本科搏位、後備方案或職業導向課程。</div></div><div class="card span12"><h2>DSE成績門檻與升學路徑對照圖</h2><div class="grid"><div class="span6"><div class="report-block"><b>圖表目的：</b>本圖將學生的DSE Best5分段及3322達標情況，與畢業後的實際出路連結，協助學校了解不同成績組別學生通常進入哪些升學或就業路徑。</div></div><div class="span6"><div class="report-block"><b>閱讀方法：</b>橫向比較不同成績組別，縱向比較不同出路類別。顏色越深，代表該成績組別中有較高比例學生進入該類出路。</div></div></div><div id="heatmap" class="heat"></div></div><div class="card span12"><h2>如何解讀DSE與出路圖表</h2><div id="careerExplanation" class="grid"></div></div><div class="card span12"><h2>匿名出路記錄探索器</h2><div class="report-block"><b>解讀方法：</b>此表用於由總體趨勢回到個別路徑。可按年度、課程層級、院校、課程或DSE Best5搜尋，找出可作升學輔導參考的成功路徑或需要跟進的個案；表內只顯示匿名碼。</div><div class="small">可按年度、課程層級、院校、課程、DSE Best5搜尋；只顯示匿名碼。</div><div class="tablewrap"><table id="careerRecordTable"></table></div></div></section>

<section id="uni" class="section grid"><div class="card span12"><h2>取得最低大學入學資格學生分析</h2><div class="grid"><div class="span4"><div class="report-block"><b>分析目的：</b>本部分聚焦已取得最低大學入學資格的學生，分析其初中基礎指標、DSE分數及畢業後出路之間的關係。</div></div><div class="span4"><div class="report-block"><b>閱讀方法：</b>先按年度觀察符合資格人數及Best5表現，再比較其本科、副學士、高級文憑及其他出路分佈。</div></div><div class="span4"><div class="report-block"><b>個案使用：</b>本部分因用於校內精準跟進，個別個案表直接顯示學生姓名；如需對外分享，應先移除姓名欄位。</div></div></div><div class="small" id="uniDef"></div><div class="controls"><select id="uniYear" onchange="renderUni()"><option value="all">全部年度</option></select><select id="uniDim" onchange="renderUni()"><option value="課程層級">課程層級</option><option value="院校途徑">院校途徑</option><option value="範疇">範疇</option><option value="Best5分段">Best5分段</option></select><input id="uniSearch" placeholder="搜尋姓名、班別、院校、課程..." oninput="renderUni()"></div></div><div class="card span12"><h2>符合資格學生名單與出路（2022至2025年DSE）</h2><div class="tablewrap"><table id="uniRecordTable"></table></div></div><div class="card span12"><h2>個別個案檢視（2022至2025年DSE）</h2><div class="report-block"><b>解讀方法：</b>個案分為高分並符合資格、剛達資格／邊緣成功，以及符合資格但選擇非本科路徑。前者可作升學成功案例，後兩者則有助檢視個別輔導、課程選擇及出路配對。</div><div class="tablewrap"><table id="uniCaseTable"></table></div></div></section>


<section id="promotion" class="section grid"><div class="card span12"><h2>升留班線分析（2017-2018至2025-2026）</h2><div class="grid"><div class="span4"><div class="report-block"><b>分析目的：</b>檢視各級升留班線多年變化，了解不同級別的學業要求及支援門檻是否穩定。</div></div><div class="span4"><div class="report-block"><b>閱讀方法：</b>熱圖以年度為橫軸、級別為縱軸；顏色越深，代表該年度該級別的升留班線越高。空白或文字備註表示該年該級別不適用一般數值線。</div></div><div class="span4"><div class="report-block"><b>應用方法：</b>可配合2025/26校內試平均分，估算低於升留班線的學生比例，作為級會、班主任及學習支援組跟進依據。</div></div></div></div><div class="card span12"><h2>升留班線熱圖</h2><div id="promotionHeatmap" class="heat promotion-heat"></div></div><div class="card span6"><h2>各級多年變化摘要</h2><div class="tablewrap"><table id="promotionSummaryTable"></table></div></div><div class="card span6"><h2>2025/26低於升留班線情況</h2><div class="tablewrap"><table id="promotionBelowTable"></table></div></div><div class="card span12"><h2>文字分析</h2><div id="promotionText"></div></div></section>


<section id="subject" class="section grid"><div class="card span12"><h2>DSE科目分析：基線、過程、公開試（只顯示DSE相關科目）</h2><div class="grid"><div class="span4"><div class="report-block"><b>分析目的：</b>以DSE有成績的科目為核心，配對相關的入學基線、初中基礎及校內試資料，避免把非DSE科目混入同一分析。</div></div><div class="span4"><div class="report-block"><b>閱讀方法：</b>先看該DSE科目的Level 2+、Level 3+及Level 4+走勢，再參考同科校內試年度綜合表現；中文、英文及數學另會配對HKAT及TSA基礎資料。</div></div><div class="span4"><div class="report-block"><b>應用方法：</b>科組可聚焦公開試科目，判斷問題源於入學基礎、初中銜接、高中校內評估，還是DSE應試策略。</div></div></div><div class="controls"><select id="subjectSel" onchange="renderSubject()"></select><select id="subjectSrc" onchange="renderSubject()"><option value="all">全部資料源</option><option value="hkat">HKAT</option><option value="tsa">TSA</option><option value="exam">校內試</option><option value="dse">DSE</option></select><input id="subjectQ" placeholder="搜尋科目資料..." oninput="renderSubject()"></div></div><div class="card span12"><div id="subjectText"></div></div><div class="card span12"><div class="tablewrap"><table id="subjectTable"></table></div></div></section>

<section id="strategy" class="section grid"><div class="card span12"><h2>策略矩陣：由數據到行動</h2><div class="grid"><div class="span6"><div class="report-block"><b>解讀方法：</b>策略矩陣不是單純列出問題，而是把數據轉化為可執行的管理問題，例如誰需要支援、何時支援、由哪一個部門負責，以及如何量度成效。</div></div><div class="span6"><div class="report-block"><b>應用方法：</b>建議行政組、科組、學習支援組及升學就業組各自選取一至兩項指標，作為下年度周年計劃及檢討的共同KPI。</div></div></div><div id="strategies" class="grid"></div></div><div class="card span12"><h2>建議年度KPI組合</h2><div class="grid"><div class="span4 strategy"><b>學業基礎KPI</b><ul><li>S1 HKAT低基線學生首學期進步率</li><li>S3 TSA基本水平及校內試合格率</li><li>多科不合格學生比例下降</li></ul></div><div class="span4 strategy"><b>DSE及高中KPI</b><ul><li>核心科邊緣學生達標率</li><li>各科Level 2+/3+/4+變化</li><li>Best5分段向上流動人數</li></ul></div><div class="span4 strategy"><b>出路KPI</b><ul><li>本科/副學士/高級文憑/VTC/DAE等路徑配對率</li><li>3322未達標學生可持續升學路徑比例</li><li>學生完成個別升學諮詢比例</li></ul></div></div></div></section>

<section id="cases" class="section grid"><div class="card span12"><h2>可行動個案線索</h2><div class="grid"><div class="span4"><div class="report-block"><b>分析目的：</b>把大量數據轉化為可跟進的學生線索，包括低基線、高潛能、邊緣達標、多科不合格、出路特殊等類型。</div></div><div class="span4"><div class="report-block"><b>閱讀方法：</b>個案線索是數據提示，不等同最終判斷。實際跟進時仍需結合任課教師觀察、出席、功課、家庭及學生意願等資料。</div></div><div class="span4"><div class="report-block"><b>應用方法：</b>可按來源及類型篩選個案，分派予班主任、科任、支援組或升學就業組，並設定回顧日期及成效指標。</div></div></div><div class="controls"><select id="caseSource" onchange="renderCases()"><option value="all">全部來源</option><option>HKAT</option><option>DSE</option><option>校內試</option><option>縱向追蹤</option><option>升學就業</option></select><select id="caseType" onchange="renderCases()"><option value="all">全部類型</option></select><input id="caseQ" placeholder="搜尋匿名碼、班號、備註..." oninput="renderCases()"><select id="caseN" onchange="renderCases()"><option>100</option><option>250</option><option>500</option></select></div><div class="tablewrap"><table id="caseTable"></table></div></div></section>

<section id="data" class="section grid"><div class="card span12"><h2>互動數據表</h2><div class="report-block"><b>解讀方法：</b>此區提供較完整的原始標準化數據及摘要表，適合在需要核實圖表、追查分類或進一步篩選時使用。表格可搜尋及排序，方便不同部門按自身需要提取資料。</div><div class="controls"><select id="dataSel" onchange="renderData()"><option value="career.records">升學就業標準化記錄</option><option value="career.summary">升學就業摘要</option><option value="career.outcome_by_dse">DSE與出路</option><option value="university_minimum.records">最低大學入學資格學生</option><option value="university_minimum.summary">最低大學入學資格摘要</option><option value="promotion_line.records">升留班線</option><option value="promotion_line.below_line_2025_26">低於升留班線情況</option><option value="longitudinal.cohort_tracking">縱向cohort追蹤</option><option value="hkat">HKAT摘要</option><option value="tsa">TSA摘要</option><option value="exam">校內試摘要</option><option value="dse_subject">DSE科目摘要</option></select><input id="dataQ" placeholder="搜尋數據..." oninput="renderData()"></div><div class="tablewrap"><table id="dataTable"></table></div></div></section>
</div>
<script id="payload" type="application/json">{js}</script>
<script>
const P=JSON.parse(document.getElementById('payload').textContent), D=P.data; let sortState={{}};
function go(id){{document.getElementById(id).scrollIntoView({{behavior:'smooth'}})}}
function uniq(a){{return [...new Set(a.filter(x=>x!==null&&x!==undefined&&x!==''))].sort((x,y)=>String(x).localeCompare(String(y),'zh-Hant'))}}
function opt(sel, arr, all){{sel.innerHTML=(all?`<option value="all">${{all}}</option>`:'')+arr.map(x=>`<option value="${{x}}">${{x}}</option>`).join('')}}
function fmt(v){{if(v===null||v===undefined||Number.isNaN(v))return '—'; if(typeof v==='number')return (Math.round(v*10)/10).toString(); if(typeof v==='object')return JSON.stringify(v); return v}}
function label(c){{const m={{
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
}}; return m[c]||c}}

function rangeText(vals, suffix=''){{
 vals=[...new Set((vals||[]).filter(v=>v!==null&&v!==undefined&&v!==''))].map(v=>String(v)).sort((a,b)=>a.localeCompare(b,'zh-Hant'));
 if(!vals.length) return '';
 if(vals.length===1) return vals[0]+suffix;
 return vals[0]+'至'+vals[vals.length-1]+suffix;
}}
function makeTable(el, rows, cols){{ if(!rows||!rows.length){{el.innerHTML='<tr><td>沒有符合條件資料</td></tr>'; return}} cols=cols||Object.keys(rows[0]); el._rows=rows; el._cols=cols; el.innerHTML='<thead><tr>'+cols.map(c=>`<th onclick="sortTable('${{el.id}}','${{c}}')">${{label(c)}}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>`<td>${{fmt(r[c])}}</td>`).join('')+'</tr>').join('')+'</tbody>'}}
function sortTable(id,c){{const el=document.getElementById(id);let rows=[...(el._rows||[])],dir=sortState[id+c]==='asc'?'desc':'asc';sortState[id+c]=dir;rows.sort((a,b)=>{{let x=a[c],y=b[c]; if(typeof x==='number'&&typeof y==='number')return dir==='asc'?x-y:y-x; return dir==='asc'?String(x).localeCompare(String(y),'zh-Hant'):String(y).localeCompare(String(x),'zh-Hant')}}); makeTable(el,rows,el._cols)}}
function lineChart(svg, rows, xKey, yKey, gKey, title){{const W=svg.clientWidth||700,H=310,p=42;svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);rows=rows.filter(r=>r[yKey]!=null&&!isNaN(+r[yKey])); if(!rows.length){{svg.innerHTML='<text x="20" y="35">沒有足夠數據</text>';return}};const xs=uniq(rows.map(r=>r[xKey]));const ys=rows.map(r=>+r[yKey]);const ymin=Math.min(...ys),ymax=Math.max(...ys),pad=(ymax-ymin)*.15||1;const xp=x=>p+(xs.indexOf(x)/Math.max(1,xs.length-1))*(W-p*1.7-p);const yp=y=>H-p-((y-(ymin-pad))/(ymax-ymin+pad*2))*(H-p*2);let html=`<text x="${{p}}" y="22" font-size="13" font-weight="700">${{title}}</text>`;for(let i=0;i<5;i++){{let y=p+i*(H-p*2)/4;html+=`<line x1="${{p}}" y1="${{y}}" x2="${{W-p}}" y2="${{y}}" stroke="#e6eaf0"/><text x="5" y="${{y+4}}" font-size="11" fill="#667085">${{(ymax+pad-i*(ymax-ymin+pad*2)/4).toFixed(1)}}</text>`}} const gs=gKey?uniq(rows.map(r=>r[gKey])):[''];const colors=['#1f4fd1','#087443','#b54708','#6941c6','#b42318','#0086a8','#d97706','#475467'];gs.forEach((g,gi)=>{{let arr=rows.filter(r=>!gKey||r[gKey]===g).sort((a,b)=>xs.indexOf(a[xKey])-xs.indexOf(b[xKey]));let pts=arr.map(r=>[xp(r[xKey]),yp(+r[yKey]),r]); if(pts.length>1)html+=`<polyline fill="none" stroke="${{colors[gi%colors.length]}}" stroke-width="3" points="${{pts.map(p=>p[0]+','+p[1]).join(' ')}}"/>`; pts.forEach(pt=>html+=`<circle cx="${{pt[0]}}" cy="${{pt[1]}}" r="4" fill="${{colors[gi%colors.length]}}"><title>${{g}} ${{pt[2][xKey]}}: ${{fmt(pt[2][yKey])}}</title></circle>`); if(gKey)html+=`<text x="${{W-170}}" y="${{42+gi*16}}" font-size="12" fill="${{colors[gi%colors.length]}}">● ${{g}}</text>`}}); xs.forEach(x=>html+=`<text x="${{xp(x)-10}}" y="${{H-12}}" font-size="10" fill="#667085" transform="rotate(-20 ${{xp(x)}} ${{H-12}})">${{String(x).slice(0,14)}}</text>`); svg.innerHTML=html}}
function barChart(svg, rows, labelKey, valueKey, title){{
 const W=svg.clientWidth||760; rows=rows.filter(r=>r[valueKey]!=null).slice(0,12);
 const rowH=34, top=44, bottom=24, left=190, right=58;
 const H=Math.max(310, top+bottom+rows.length*rowH);
 svg.style.height=H+'px'; svg.setAttribute('viewBox',`0 0 ${{W}} ${{H}}`);
 if(!rows.length){{svg.innerHTML='<text x="20" y="35" font-size="14">沒有足夠數據</text>';return}}
 const max=Math.max(...rows.map(r=>+r[valueKey]),1);
 let html=`<text x="18" y="24" font-size="15" font-weight="700" fill="#172033">${{title}}</text>`;
 html+=`<line x1="${{left}}" y1="${{top-8}}" x2="${{W-right}}" y2="${{top-8}}" stroke="#e6eaf0"/>`;
 rows.forEach((r,i)=>{{
   const y=top+i*rowH;
   const labelText=String(r[labelKey]??'未分類');
   const short=labelText.length>18?labelText.slice(0,18)+'…':labelText;
   const barW=Math.max(2,(+r[valueKey]/max)*(W-left-right));
   const color=['#1f4fd1','#087443','#b54708','#6941c6','#0086a8','#d97706','#b42318','#475467'][i%8];
   html+=`<text x="${{left-10}}" y="${{y+18}}" font-size="13" text-anchor="end" fill="#172033"><title>${{labelText}}</title>${{short}}</text>`;
   html+=`<rect x="${{left}}" y="${{y+3}}" width="${{barW}}" height="22" rx="6" fill="${{color}}"><title>${{labelText}}: ${{fmt(r[valueKey])}}</title></rect>`;
   html+=`<text x="${{Math.min(W-right+4,left+barW+8)}}" y="${{y+19}}" font-size="13" font-weight="700" fill="#172033">${{fmt(r[valueKey])}}</text>`;
   html+=`<line x1="${{left}}" y1="${{y+31}}" x2="${{W-right}}" y2="${{y+31}}" stroke="#f0f2f5"/>`;
 }});
 svg.innerHTML=html;
}}
function allCases(){{return [...(D.hkat_cases||[]).map(c=>({{source:'HKAT',year:c.year,code:c.code,class_no:'—',type:c.type,metric:c.total,note:c.note}})),...(D.dse_cases||[]).map(c=>({{source:'DSE',year:c.year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note}})),...(D.exam_cases||[]).map(c=>({{source:'校內試',year:'2025/26',code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:c.note}})),...((D.longitudinal&&D.longitudinal.longitudinal_cases)||[]).map(c=>({{source:'縱向追蹤',year:c.cohort,code:c.code,class_no:c.class_no,type:c.type,metric:c.exam_avg,note:c.note}})),...((D.career&&D.career.cases)||[]).map(c=>({{source:'升學就業',year:c.grad_year,code:c.code,class_no:c.class_no,type:c.type,metric:c.metric,note:(c.outcome||'')+' '+(c.institution||'')+' '+(c.programme||'')+'｜'+(c.note||'')}}))]}}
function init(){{const C=D.career||{{records:[],linked_records:[],cases:[]}}, L=D.longitudinal||{{}}; k1.textContent=C.records.length; k2.textContent=C.linked_records.length; k3.textContent=L.matched_records||0; k4.textContent=allCases().length; opt(insTheme,uniq(P.insights.map(x=>x.theme)),'全部主題'); renderInsights(); opt(hkatSub,uniq(D.hkat.map(r=>r.subject))); hkatSub.value='中文'; drawHKAT(); drawCareerTop(); opt(careerYear,uniq(C.records.map(r=>r.grad_year)),'全部年度'); renderCareer(); renderCareerExplanation(); renderUniInit(); renderPromotion(); const subs=uniq((D.dse_subject||[]).map(r=>r.subject)); opt(subjectSel,subs); subjectSel.value=subs.includes('英文')?'英文':subs[0]; renderSubject(); document.getElementById('strategies').innerHTML=P.strategies.map(s=>`<div class="span4 strategy"><span class="tag purple">${{s.lens}}</span><h3>${{s.question}}</h3><p><b>可用數據：</b>${{s.use}}</p><p><b>決策：</b>${{s.decision}}</p></div>`).join(''); opt(caseType,uniq(allCases().map(c=>c.type)),'全部類型'); renderCases(); renderData();}}
function renderInsights(){{let t=insTheme.value,q=insSearch.value.toLowerCase();let arr=P.insights.filter(x=>(t==='all'||x.theme===t)&&(!q||JSON.stringify(x).toLowerCase().includes(q))).slice(0,60); insights.innerHTML=arr.map(x=>`<div class="report-block"><span class="tag">${{x.theme}}</span><span class="tag good">${{x.area}}</span><br><b>${{x.title}}</b><br>${{x.detail}}<br><span class="muted">建議：${{x.action}}</span></div>`).join('')}}
function drawHKAT(){{let rows=D.hkat.filter(r=>r.subject===hkatSub.value); lineChart(hkatChart,rows,'year','mean',null,hkatSub.value+' HKAT平均分（'+rangeText(rows.map(r=>r.year))+'）')}}
function drawCareerTop(){{const C=D.career||{{summary:[],records:[]}}; let y=Math.max(...C.records.map(r=>r.grad_year).filter(Boolean)); let dim=careerDimTop.value; let rows=C.summary.filter(r=>r.grad_year===y&&r.dimension===dim).sort((a,b)=>b.count-a.count).map(r=>({{label:r.category,value:r.count}})); barChart(careerTopChart,rows,'label','value',y+'年出路分佈')}}

function renderCareerExplanation(){{
 const el=document.getElementById('careerExplanation'); if(!el) return;
 el.innerHTML=`
 <div class="span4 strategy"><span class="tag">一、Best5分段的意義</span><p>DSE Best5是學生最佳五科成績的總和，可用作概括學生整體公開試表現。本報告把Best5分為0–9、10–14、15–19及20+，目的不是為學生貼標籤，而是分析不同成績組別的實際升學路徑。</p><p><b>解讀重點：</b>若Best5較高組別集中進入本科，代表高成就學生的升學銜接較清晰；若中間組別分散於本科、副學士及高級文憑，則顯示該組學生最需要精準的升學策略。</p></div>
 <div class="span4 strategy"><span class="tag good">二、3322門檻的意義</span><p>3322通常指中文、英文達第3級，數學及其他科目達第2級，是本地本科升學的重要參考門檻之一。本報告把「3322達標」與「3322未達標」學生的實際出路分開比較。</p><p><b>解讀重點：</b>若3322達標學生多進入本科，反映核心科達標對升學有明顯影響；若未達3322學生仍能透過副學士、高級文憑、VTC或DAE延續升學，則可作多元升學路徑的具體例證。</p></div>
 <div class="span4 strategy"><span class="tag purple">三、出路類別的分拆</span><p>本報告已將學位課程進一步分為JUPAS／SSSDP及Non-JUPAS／自資／其他路徑，並同時分開副學士及高級文憑，避免把不同層級及不同入學途徑的專上課程混合分析。</p><p><b>解讀重點：</b>副學士通常較偏向升讀學位銜接；高級文憑較多與專業技能或職業導向相關。兩者對學生未來路徑的意義不同，應分開檢視。</p></div>
 <div class="span6 strategy"><span class="tag warn">四、學校層面的啟示</span><p>圖表可協助學校把升學輔導由「放榜後支援」提前至高中階段。Best5 20+學生可聚焦JUPAS、SSSDP、面試及學科配對；Best5 15–19學生宜同時準備本科及副學士／高級文憑方案；Best5 10–14及未達3322學生則需要及早認識VTC、DAE、職專、重讀及就業再進修等路徑。</p></div>
 <div class="span6 strategy"><span class="tag bad">五、個案跟進角度</span><p>圖表亦有助找出值得深入了解的特殊個案，例如：高Best5但未進入本科、未達3322但成功進入本科或學位路徑、低Best5但有清晰專業出路。這些個案可分別用於檢視升學策略、總結成功因素及優化個別輔導。</p></div>`;
}}

function renderCareer(){{const C=D.career||{{records:[],linked_records:[],summary:[],outcome_by_dse:[]}};let y=careerYear.value,dim=careerDim.value,q=careerSearch.value.toLowerCase();let rec=C.records.filter(r=>(y==='all'||String(r.grad_year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));let linked=(C.linked_records||[]).filter(r=>(y==='all'||String(r.grad_year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));let counts={{}};rec.forEach(r=>counts[r[dim]]=(counts[r[dim]]||0)+1);barChart(careerChart,Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([label,value])=>({{label,value}})),'label','value','出路分佈（'+(y==='all'?rangeText((C.records||[]).map(r=>r.grad_year),'年'):y+'年')+'）');let by=C.outcome_by_dse.filter(r=>r.dimension==='level_detail'&&['0-9','10-14','15-19','20+'].includes(r.best5_band));barChart(dseOutcomeChart,by.filter(r=>['學位課程（JUPAS/SSSDP）','學位課程（Non-JUPAS/自資/其他）','副學士','高級文憑','文憑/基礎/職專'].includes(r.category)).map(r=>({{label:r.best5_band+' '+r.category,value:r.count}})),'label','value','不同DSE成績組別的主要畢業出路（'+rangeText((C.linked_records||[]).map(r=>r.grad_year),'年')+'）'); renderHeat(by); makeTable(careerRecordTable, linked.slice(0,500), ['grad_year','anon','class','status','level','institution_type','institution','programme','field','dse_best5','meet3322']);}}
function renderHeat(rows){{let bands=['0-9','10-14','15-19','20+','3322達標','3322未達標']; let cats=uniq(rows.concat((D.career||{{outcome_by_dse:[]}}).outcome_by_dse).filter(r=>r.dimension==='level_detail').map(r=>r.category)).slice(0,6); let all=(D.career||{{outcome_by_dse:[]}}).outcome_by_dse.filter(r=>r.dimension==='level_detail'); let html='<div class="heat-row"><div class="heat-cell heat-head">出路 / 成績</div>'+bands.map(b=>`<div class="heat-cell heat-head">${{b}}</div>`).join('')+'</div>'; cats.forEach(cat=>{{html+=`<div class="heat-row"><div class="heat-cell heat-head">${{cat}}</div>`+bands.map(b=>{{let r=all.find(x=>x.best5_band===b&&x.category===cat); let val=r?r.pct:0; let alpha=Math.min(.95,(val||0)/100+.08); return `<div class="heat-cell" style="background:rgba(31,79,209,${{alpha}});color:${{alpha>.45?'#fff':'#172033'}}"><b>${{fmt(val)}}%</b><br><span>${{r?r.count:0}}人</span></div>`}}).join('')+'</div>'}}); heatmap.innerHTML=html}}

function renderUniInit(){{
 const U=P.uni||{{records:[],summary:[],trend:[],cases:[]}}; if(!document.getElementById('uniYear')) return;
 uniDef.textContent=U.definition||'';
 opt(uniYear, uniq((U.records||[]).map(r=>r.year)), '全部年度');
 renderUni();
}}
function renderUni(){{
 const U=P.uni||{{records:[],summary:[],trend:[],cases:[]}};
 const y=uniYear.value, dim=uniDim.value, q=uniSearch.value.toLowerCase();
 let rec=(U.records||[]).filter(r=>(y==='all'||String(r.year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));
 makeTable(uniRecordTable, rec.slice(0,300), ['year','class','no','中文姓名','英文姓名','best5','中文','英文','數學','選修2級或以上數目','課程層級','院校途徑','院校','課程','範疇']);
 let cases=(U.cases||[]).filter(r=>(y==='all'||String(r.year)===String(y))&&(!q||JSON.stringify(r).toLowerCase().includes(q)));
 makeTable(uniCaseTable, cases.slice(0,120), ['year','class','no','中文姓名','英文姓名','個案類型','best5','中文','英文','數學','課程層級','院校','課程','解讀']);
}}



function coreEquivalent(subj){{
 if(subj==='中文' || subj==='中國語文' || subj==='Ch Lang') return {{hkat:'中文',tsa:'中國語文',exam:['中文','中國語文'],dse:['中文','中國語文','Ch Lang']}};
 if(subj==='英文' || subj==='Eng Lang') return {{hkat:'英文',tsa:'英文',exam:['英文','English'],dse:['英文','Eng Lang']}};
 if(subj==='數學' || subj==='Maths') return {{hkat:'數學',tsa:'數學',exam:['數學','Maths'],dse:['數學','Maths']}};
 return {{hkat:null,tsa:null,exam:[subj],dse:[subj]}};
}}
function subjectMatch(value, list){{return list.some(x=>String(value)===String(x))}}

function aggregateExamSubject(subj){{
 const groups={{}}; const eq=coreEquivalent(subj);
 (D.exam||[]).filter(r=>subjectMatch(r.subject,eq.exam)).forEach(r=>{{
   const y=r.year||'未列年度';
   if(!groups[y]) groups[y]={{source:'校內試',year:y,subject:subj,n:0,mean_num:0,mean_den:0,pass_num:0,pass_den:0,forms:new Set(),assessments:new Set()}};
   const g=groups[y], n=Number(r.n)||0;
   g.n+=n; if(r.form) g.forms.add(r.form); if(r.assessment) g.assessments.add(r.assessment);
   if(r.mean!==null&&r.mean!==undefined&&n){{g.mean_num+=Number(r.mean)*n; g.mean_den+=n;}}
   if(r.pass_rate!==null&&r.pass_rate!==undefined&&n){{g.pass_num+=Number(r.pass_rate)*n; g.pass_den+=n;}}
 }});
 return Object.values(groups).map(g=>{{
   const mean=g.mean_den?Math.round((g.mean_num/g.mean_den)*10)/10:null;
   const pass=g.pass_den?Math.round((g.pass_num/g.pass_den)*10)/10:null;
   return {{source:'校內試',year:g.year,subject:g.subject,n:g.n,mean:mean,pass_rate:pass,form:[...g.forms].sort().join('、'),assessment:'全年綜合',main:pass!==null?pass:mean}};
 }}).sort((a,b)=>String(a.year).localeCompare(String(b.year),'zh-Hant'));
}}


function renderPromotion(){{
 const Pm=D.promotion_line||{{records:[],summary:[],below_line_2025_26:[]}}; if(!document.getElementById('promotionHeatmap')) return;
 const years=uniq(Pm.records.map(r=>r.year)); const forms=uniq(Pm.records.map(r=>r.form));
 const vals=Pm.records.filter(r=>r.line!==null&&r.line!==undefined).map(r=>Number(r.line)); const min=Math.min(...vals), max=Math.max(...vals);
 const gridCols=`140px repeat(${{years.length}}, minmax(92px, 1fr))`;
 const minWidth=140+years.length*100;
 const rowStyle=`grid-template-columns:${{gridCols}};min-width:${{minWidth}}px`;
 let html='<div class="promotion-legend"><b>閱讀方法：</b><span>顏色越深代表升留班線越高</span><span class="promotion-swatch" style="background:rgba(31,79,209,.18)"></span><span>較低</span><span class="promotion-swatch" style="background:rgba(31,79,209,.85)"></span><span>較高</span></div>';
 html+='<div class="heat-row" style="'+rowStyle+'"><div class="heat-cell heat-head">級別 / 年度</div>'+years.map(y=>`<div class="heat-cell heat-head">${{y}}</div>`).join('')+'</div>';
 forms.forEach(f=>{{
   html+=`<div class="heat-row" style="${{rowStyle}}"><div class="heat-cell heat-head">${{f}}</div>`+years.map(y=>{{
     let r=Pm.records.find(x=>x.year===y&&x.form===f);
     if(!r) return '<div class="heat-cell">—</div>';
     if(r.line===null||r.line===undefined) return `<div class="heat-cell" style="background:#f8fafc;color:#667085;font-size:12px">${{r.note||'—'}}</div>`;
     let alpha=.16+(Number(r.line)-min)/(max-min||1)*.72;
     return `<div class="heat-cell" style="background:rgba(31,79,209,${{alpha}});color:${{alpha>.48?'#fff':'#172033'}}"><b>${{fmt(r.line)}}</b></div>`;
   }}).join('')+'</div>';
 }});
 promotionHeatmap.innerHTML=html;
 makeTable(promotionSummaryTable, Pm.summary||[], ['form','years','n_years','min_line','max_line','avg_line','latest_year','latest_line','change_first_latest']);
 makeTable(promotionBelowTable, Pm.below_line_2025_26||[], ['year','form','assessment','line','students','below_line','below_pct','average_score']);
 const latest=(Pm.summary||[]).map(r=>`${{r.form}}最新升留班線為${{fmt(r.latest_line)}}分，較首年變化${{fmt(r.change_first_latest)}}分`).join('；');
 const below=(Pm.below_line_2025_26||[]).sort((a,b)=>(b.below_pct||0)-(a.below_pct||0)).slice(0,5).map(r=>`${{r.form}} ${{r.assessment}}低於線比例${{fmt(r.below_pct)}}%`).join('；');
 promotionText.innerHTML=`<div class="report-block"><b>多年趨勢：</b>${{latest}}。</div><div class="report-block"><b>2025/26風險提示：</b>${{below}}。此比例只反映以現時校內試平均分與升留班線作初步比較，實際升留班決定仍需結合學生全年表現、操行、出席及教師專業判斷。</div>`;
}}

function renderSubject(){{
 let s=subjectSel.value,src=subjectSrc.value,q=subjectQ.value.toLowerCase(),rows=[];
 const eq=coreEquivalent(s);
 if(src==='all'||src==='hkat'){{
   if(eq.hkat) rows.push(...D.hkat.filter(r=>r.subject===eq.hkat).map(r=>({{source:'HKAT入學基線',year:r.year,subject:s,原科目:r.subject,n:r.n,mean:r.mean,main:r.mean}})));
 }}
 if(src==='all'||src==='tsa'){{
   if(eq.tsa) rows.push(...D.tsa.filter(r=>r.subject===eq.tsa).map(r=>({{source:'TSA初中基礎',year:r.year,subject:s,原科目:r.subject,n:r.n,mean:r.school_basic_pct,main:r.school_basic_pct,hk_basic_pct:r.hk_basic_pct,value_added:r.value_added}})));
 }}
 if(src==='all'||src==='exam') rows.push(...aggregateExamSubject(s).map(r=>({{...r,source:'校內試年度綜合',subject:s}})));
 if(src==='all'||src==='dse') rows.push(...D.dse_subject.filter(r=>subjectMatch(r.subject,eq.dse)).map(r=>({{source:'DSE公開試',year:r.year,subject:s,原科目:r.subject,n:r.n,mean:r.mean,lv2_plus:r.lv2_plus,lv3_plus:r.lv3_plus,lv4_plus:r.lv4_plus,main:r.lv2_plus}})));
 if(q)rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q));
 const years=rangeText(rows.map(r=>String(r.year).split(' ')[0]));
 subjectText.innerHTML=`<div class="report-block"><b>${{s}}</b><br>本部分只以DSE有成績的科目作選項，並把同名或等同科目的資料配對。表格列出DSE Level 2+、Level 3+、Level 4+、平均等級，以及校內試年度綜合表現；校內試已按年度綜合計算。中文、英文及數學會額外顯示HKAT及TSA基礎資料，其他選修科則主要比較校內試與DSE表現。</div>`;
 makeTable(subjectTable,rows,['source','year','subject','原科目','n','mean','pass_rate','lv2_plus','lv3_plus','lv4_plus','hk_basic_pct','value_added']);
}}

function renderCases(){{let rows=allCases(),src=caseSource.value,t=caseType.value,q=caseQ.value.toLowerCase(),n=+caseN.value; if(src!=='all')rows=rows.filter(r=>r.source===src); if(t!=='all')rows=rows.filter(r=>r.type===t); if(q)rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(caseTable,rows.slice(0,n),['source','year','code','class_no','type','metric','note'])}}
function getPath(obj,path){{return path.split('.').reduce((o,k)=>o&&o[k],obj)}}
function renderData(){{let rows=[]; if(dataSel.value==='university_minimum.records') rows=[...((P.uni&&P.uni.records)||[])]; else if(dataSel.value==='university_minimum.summary') rows=[...((P.uni&&P.uni.summary)||[])]; else if(dataSel.value==='promotion_line.records') rows=[...((D.promotion_line&&D.promotion_line.records)||[])]; else if(dataSel.value==='promotion_line.below_line_2025_26') rows=[...((D.promotion_line&&D.promotion_line.below_line_2025_26)||[])]; else rows=[...(getPath(D,dataSel.value)||[])]; let q=dataQ.value.toLowerCase(); if(q)rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)); makeTable(dataTable,rows.slice(0,1000))}}
window.addEventListener('load',init);
</script></body></html>'''
Path('/home/user/school_annual_review_enhanced_report.html').write_text(html,encoding='utf-8')
print('written enhanced',len(html),'insights',len(insights))
