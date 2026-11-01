"""Bounded CI host/container memory evidence without environment, arguments or source output."""
import argparse
import json
from pathlib import Path
import signal
import subprocess
import time

FIELDS=('MemTotal','MemAvailable','SwapTotal','SwapFree')
CGROUP_FIELDS=('low','high','max','oom','oom_kill','oom_group_kill')

def memory_fields(text):
    result={}
    for line in text.splitlines():
        name,sep,value=line.partition(':')
        if name in FIELDS: result[name+'_kb']=int(value.strip().split()[0])
    return result

def cgroup_memory_events(root):
    # Cgroup-v2 counters are evidence for the observed cgroup, not proof
    # that Unity or its Docker container caused a host OOM kill.
    try:
        values={}
        for line in (root/'memory.events').read_text().splitlines():
            fields=line.split()
            if len(fields)==2 and fields[0] in CGROUP_FIELDS:
                number=int(fields[1])
                if number<0:raise ValueError('Negative cgroup event counter')
                values[fields[0]]=number
        return values if 'oom' in values and 'oom_kill' in values else None
    except (OSError,ValueError):
        return None

def sample(proc=Path('/proc'),cgroup=Path('/sys/fs/cgroup')):
    row={'unix_time':time.time()}
    try:row.update(memory_fields((proc/'meminfo').read_text()))
    except (OSError,ValueError):row['host_memory']='unavailable'
    events=cgroup_memory_events(cgroup)
    row['cgroup_v2_memory_events']=events if events is not None else 'unavailable'
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
    event_rows=[r['cgroup_v2_memory_events'] for r in rows
                if isinstance(r.get('cgroup_v2_memory_events'),dict)]
    def event_delta(key):
        if len(event_rows)<2 or key not in event_rows[0] or key not in event_rows[-1]:
            return None
        difference=event_rows[-1][key]-event_rows[0][key]
        return difference if difference>=0 else None
    return {'samples':len(rows),'minimum_available_kb':min(values('MemAvailable_kb'),default=None),
            'minimum_swap_free_kb':min(values('SwapFree_kb'),default=None),
            'maximum_top_process_rss_kb':max((p['rss_kb'] for r in rows for p in r.get('largest_processes',[])),default=None),
            'cgroup_v2_oom_delta':event_delta('oom'),
            'cgroup_v2_oom_kill_delta':event_delta('oom_kill'),
            'cgroup_v2_scope':'observed_monitor_cgroup_not_attributed_to_unity',
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
