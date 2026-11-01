"""Bounded CI host/container memory evidence without environment, arguments or source output."""
import argparse
import json
from pathlib import Path
import signal
import subprocess
import time

FIELDS=('MemTotal','MemAvailable','SwapTotal','SwapFree')

def memory_fields(text):
    result={}
    for line in text.splitlines():
        name,sep,value=line.partition(':')
        if name in FIELDS: result[name+'_kb']=int(value.strip().split()[0])
    return result

def sample(proc=Path('/proc')):
    row={'unix_time':time.time()}
    try:row.update(memory_fields((proc/'meminfo').read_text()))
    except (OSError,ValueError):row['host_memory']='unavailable'
    processes=[]
    for path in proc.glob('[0-9]*/status'):
        try:
            fields=dict(line.split(':',1) for line in path.read_text().splitlines() if ':' in line)
            rss=int(fields.get('VmRSS','0 kB').split()[0])
            processes.append({'name':fields.get('Name','').strip()[:50],'rss_kb':rss})
        except (OSError,ValueError):continue
    row['largest_processes']=sorted(processes,key=lambda x:x['rss_kb'],reverse=True)[:6]
    return row

def docker_states():
    try:
        ids=subprocess.check_output(['docker','ps','-aq'],text=True,timeout=8).split()
        if not ids:return []
        template='{"id":"{{.Id}}","oom_killed":{{.State.OOMKilled}},"exit_code":{{.State.ExitCode}},"status":"{{.State.Status}}","memory_limit_bytes":{{.HostConfig.Memory}},"memory_swap_limit_bytes":{{.HostConfig.MemorySwap}}}'
        output=subprocess.check_output(['docker','inspect','--format',template,*ids],text=True,timeout=8)
        result=[json.loads(line) for line in output.splitlines()]
        for row in result: row['id']=row['id'][:12]
        return result
    except (OSError,ValueError,subprocess.SubprocessError):return 'unavailable'

def summarize(path):
    if not path.exists():return {'samples':0,'status':'monitor_not_started'}
    rows=[]
    for line in path.read_text().splitlines():
        try: rows.append(json.loads(line))
        except ValueError:continue
    values=lambda key:[r[key] for r in rows if key in r]
    return {'samples':len(rows),'minimum_available_kb':min(values('MemAvailable_kb'),default=None),
            'minimum_swap_free_kb':min(values('SwapFree_kb'),default=None),
            'maximum_top_process_rss_kb':max((p['rss_kb'] for r in rows for p in r.get('largest_processes',[])),default=None),
            'docker_final_states':docker_states()}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--summarize',action='store_true');p.add_argument('--interval',type=float,default=10);p.add_argument('--samples',type=int,default=960);a=p.parse_args()
    if a.summarize:print('RAFT_CI_MEMORY_EVIDENCE '+json.dumps(summarize(a.output),sort_keys=True));return
    if not 0.01<=a.interval<=60 or not 1<=a.samples<=1440:raise ValueError('Unbounded CI monitor configuration')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    stopping=[False]
    signal.signal(signal.SIGTERM,lambda *_:stopping.__setitem__(0,True))
    with a.output.open('x') as out:
        for _ in range(a.samples):
            out.write(json.dumps(sample(),sort_keys=True)+'\n');out.flush()
            if stopping[0]:break
            time.sleep(a.interval)

if __name__=='__main__':main()
