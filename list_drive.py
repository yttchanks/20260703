import requests,re,html as ihtml,sys,time
from bs4 import BeautifulSoup

def list_folder(fid, path=''):
    url=f'https://drive.google.com/drive/folders/{fid}'
    text=requests.get(url, timeout=30).text
    # Items represented with JxSEve aria-label and nested data-id
    items=[]
    # use regex around JxSEve blocks
    for m in re.finditer(r'<div class="JxSEve" aria-label="(.*?)".*?</div></div></div></div></div>', text, re.S):
        block=m.group(0)
        label=ihtml.unescape(m.group(1))
        idm=re.search(r'data-id="([^"]+)"', block)
        tt=re.search(r'data-tooltip="(.*?)"', block)
        if idm:
            items.append((label, idm.group(1), ihtml.unescape(tt.group(1)) if tt else ''))
    # dedup
    seen=set(); out=[]
    for label,id,tt in items:
        if id in seen: continue
        seen.add(id); out.append((label,id,tt))
    return out

def rec(fid, path='', depth=0):
    items=list_folder(fid)
    print('  '*depth+path+f' ({fid}) items {len(items)}')
    for label,id,tt in items:
        print('  '*(depth+1)+repr(label)+' ID='+id+' TT='+repr(tt))
        if 'folder' in label.lower():
            rec(id, path+'/'+label, depth+1)

rec('1OfE4hloiNx4HmL8zQjSoFB-wkSIipxVr','root')
