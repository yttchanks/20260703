import requests,re,html,json,time,sys
from urllib.parse import quote
session=requests.Session()
seen_folders=set()

def list_folder(fid):
    text=session.get(f'https://drive.google.com/drive/folders/{fid}',timeout=30).text
    items=[]
    for m in re.finditer(r'<div class="JxSEve" aria-label="(.*?)".*?</div></div></div></div></div>', text, re.S):
        block=m.group(0)
        label=html.unescape(m.group(1))
        idm=re.search(r'data-id="([^"]+)"', block)
        tt=re.search(r'data-tooltip="(.*?)"', block)
        if not idm: continue
        item_id=idm.group(1)
        tooltip=html.unescape(tt.group(1)) if tt else ''
        name=tooltip
        ftype='other'
        low=label.lower()
        if 'shared folder' in low:
            ftype='folder'; name=label.replace(' Shared folder','')
        elif 'google sheets' in low:
            ftype='gsheet'; name=tooltip.replace(' Google Sheets','')
        elif 'microsoft excel' in low:
            ftype='excel'; name=tooltip.replace(' Microsoft Excel','')
        elif 'pdf' in low:
            ftype='pdf'; name=tooltip.replace(' PDF','')
        elif 'text' in low:
            ftype='text'; name=tooltip.replace(' Text','')
        elif 'compressed archive' in low:
            ftype='zip'; name=tooltip.replace(' Compressed archive','')
        if 'unavailable' in low or 'original item deleted' in tooltip.lower():
            ftype='unavailable'
        items.append({'id':item_id,'label':label,'tooltip':tooltip,'name':name,'type':ftype})
    out=[]; seen=set()
    for it in items:
        if it['id'] in seen: continue
        seen.add(it['id']); out.append(it)
    return out

def crawl(fid,path='root'):
    if fid in seen_folders: return []
    seen_folders.add(fid)
    try:
        items=list_folder(fid)
    except Exception as e:
        return [{'id':fid,'path':path,'type':'folder_error','error':str(e)}]
    records=[]
    for it in items:
        it['path']=path+'/'+it['name']
        records.append(it)
        if it['type']=='folder':
            records.extend(crawl(it['id'],it['path']))
            time.sleep(0.05)
    return records

records=crawl('1OfE4hloiNx4HmL8zQjSoFB-wkSIipxVr','20260703 Staff Development')
open('/home/user/drive_manifest.json','w',encoding='utf-8').write(json.dumps(records,ensure_ascii=False,indent=2))
from collections import Counter
print('records',len(records),Counter(r['type'] for r in records))
for t,c in Counter(r['type'] for r in records).items(): print(t,c)
