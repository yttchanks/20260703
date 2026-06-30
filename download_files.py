import json,requests,os,re,html,time
from pathlib import Path
recs=json.load(open('/home/user/drive_manifest.json',encoding='utf-8'))
base=Path('/home/user/drive_data')
base.mkdir(exist_ok=True)
s=requests.Session()

def safe(p):
    p=p.replace('20260703 Staff Development/','')
    parts=[re.sub(r'[\\/:*?"<>|]+','_',x).strip()[:120] for x in p.split('/')]
    return base.joinpath(*parts)

def download_file(fid, out):
    URL='https://drive.google.com/uc?export=download&id='+fid
    r=s.get(URL, stream=True, timeout=60)
    # handle confirm token
    token=None
    for k,v in r.cookies.items():
        if k.startswith('download_warning'): token=v
    if token:
        r=s.get(URL+'&confirm='+token, stream=True, timeout=60)
    # if HTML virus confirm form
    ct=r.headers.get('content-type','')
    content=b''
    first=True
    out.parent.mkdir(parents=True,exist_ok=True)
    with open(out,'wb') as f:
        for chunk in r.iter_content(32768):
            if chunk: f.write(chunk)
    return r.status_code, ct, out.stat().st_size

for t in ['excel','text']:
    items=[r for r in recs if r['type']==t]
    print('download type',t,len(items))
    for i,r in enumerate(items):
        ext=''
        if '.' not in Path(r['name']).name:
            ext='.xlsx' if t=='excel' else '.txt'
        out=safe(r['path']+ext)
        if out.exists() and out.stat().st_size>100: continue
        try:
            st,ct,sz=download_file(r['id'],out)
            print(i+1, st, sz, r['path'])
        except Exception as e:
            print('ERR',r['path'],e)
        time.sleep(0.1)
