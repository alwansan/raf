"""Pinned original-source resource lifetime repair and honest Android offline Party boundary."""
import argparse
import hashlib
from pathlib import Path
import re

PINS={
'Dx11FFT':('8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0',1),
'WavesRendererFFT':('e7f6b8fd477f321120fc626781f0653fe1168f0e86daad0cdf8d9c4e56b323e9',3),
'PlayFabMultiplayerManager':('e71cd10249c028c7ae0b13e06e4cbe8826ec87d39a1c54778d6e288e97ca6087',0)}
DECL=r'(?P<indent>[ \t]*)TemporaryRenderTexture (?P<name>temporary\d*) = [\w.]+\.GetTemporary\(\);\n'


def protect_temporaries(text,expected):
    declaration=re.compile(DECL)
    groups=[];cursor=0;count=0
    while True:
        first=declaration.search(text,cursor)
        if not first: break
        rows=[first];end=first.end()
        while True:
            more=declaration.match(text,end)
            if not more: break
            rows.append(more);end=more.end()
        indent=first['indent'];names=[r['name'] for r in rows]
        cleanup=''.join(indent+n+'.Dispose();\n' for n in names)
        stop=text.find(cleanup,end)
        if stop<0: raise ValueError('Original temporary cleanup sequence changed')
        body=text[end:stop]
        replacement=''
        for depth,row in enumerate(rows):
            replacement+='\t'*depth+row[0]+indent+'\t'*depth+'try\n'+indent+'\t'*depth+'{\n'
        replacement+=''.join('\t'*len(rows)+line if line.strip() else line for line in body.splitlines(keepends=True))
        for depth in reversed(range(len(rows))):
            prefix=indent+'\t'*depth
            replacement+=prefix+'}\n'+prefix+'finally\n'+prefix+'{\n'+prefix+'\t'+names[depth]+'.Dispose();\n'+prefix+'}\n'
        groups.append((first.start(),stop+len(cleanup),replacement));cursor=stop+len(cleanup);count+=len(rows)
    if count!=expected: raise ValueError('Unexpected temporary acquisition coverage')
    for start,end,replacement in reversed(groups):text=text[:start]+replacement+text[end:]
    return text


def adapt(stem,text):
    digest,expected=PINS[stem]
    normalized=text.replace('\r\n','\n')
    if hashlib.sha256(normalized.encode()).hexdigest()!=digest: raise ValueError('Unknown original source revision: '+stem)
    if expected: normalized=protect_temporaries(normalized,expected)
    else:
        signature='\t\tprivate void InitializeImpl()\n\t\t{\n'
        if normalized.count(signature)!=1: raise ValueError('Ambiguous original Party initialization boundary')
        normalized=normalized.replace(signature,signature+'''#if UNITY_ANDROID && !UNITY_EDITOR
            // Solo adapter: no Windows Party backend or fabricated remote initialization.
            enabled = false;
            return;
#endif
''',1)
    return normalized.replace('\n','\r\n') if '\r\n' in text else normalized


def apply(root,backup):
    if backup.resolve().is_relative_to(root.resolve()):raise ValueError('Backup must be outside original source/project')
    plan=[]
    for stem in PINS:
        candidates=[p for p in root.rglob(stem+'.cs') if 'Assembly-CSharp' in str(p) or not (root/'Assets').exists()]
        if len(candidates)!=1:raise ValueError('Original source identity ambiguous: '+stem)
        p=candidates[0];raw=p.read_bytes();text=raw.decode('utf-8-sig');changed=adapt(stem,text)
        meta=Path(str(p)+'.meta');meta_bytes=meta.read_bytes() if meta.exists() else None
        plan.append((p,raw,(b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+changed.encode(),meta,meta_bytes))
    backup.mkdir(parents=True,exist_ok=False)
    for p,raw,changed,meta,meta_bytes in plan:
        q=backup/p.relative_to(root);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
        if meta_bytes is not None:Path(str(q)+'.meta').write_bytes(meta_bytes)
    try:
        for p,raw,changed,meta,meta_bytes in plan:
            p.write_bytes(changed)
            if meta_bytes is not None and meta.read_bytes()!=meta_bytes:raise ValueError('Original source GUID changed')
    except BaseException:
        for p,raw,changed,meta,meta_bytes in plan:p.write_bytes(raw)
        raise
    print('RAFT_ANDROID_RENDER_LIFETIMES temporaryResources=4 exceptionSafe=true windowsPartyInitializationBypassed=true originalMetasUnchanged=true')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--backup',type=Path,required=True);args=p.parse_args();apply(args.source,args.backup)
