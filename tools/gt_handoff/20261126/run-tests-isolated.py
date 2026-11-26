import concurrent.futures,json,subprocess,time
from pathlib import Path
root=Path('/home/a/Documents/Codex/2026-11-13/new-chat/work/raf')
out=Path('/home/a/Documents/Codex/2026-11-20/new-chat-2/work/isolated-tests');out.mkdir(exist_ok=True)
python='/home/a/Documents/Codex/2026-11-13/new-chat/work/unity-reader/bin/python'
def run(p):
 start=time.monotonic()
 try:
  r=subprocess.run([python,'-m','unittest','discover','-s','tests','-p',p.name],cwd=root,capture_output=True,text=True,timeout=75)
  code=r.returncode;log=r.stdout+r.stderr
 except subprocess.TimeoutExpired as e:
  code=124;log=str(e)
 (out/(p.stem+'.log')).write_text(log)
 return dict(file=p.name,code=code,seconds=round(time.monotonic()-start,2))
files=sorted((root/'tests').glob('test_*.py'))
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(run,files):
  results.append(r)
  if r['code']: print(json.dumps(r),flush=True)
(out/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(dict(total=len(results),passed=sum(x['code']==0 for x in results),failed=sum(x['code']!=0 for x in results))),flush=True)
