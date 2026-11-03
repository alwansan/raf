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
        if name in FIELDS:
            pieces=value.strip().split()
            if len(pieces)!=2 or pieces[1]!='kB':
                raise ValueError('Missing/invalid host-memory unit')
            amount=int(pieces[0])
            if amount<0:raise ValueError('Negative host-memory counter')
            result[name+'_kb']=amount
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
        if not path.parent.name.isascii() or not path.parent.name.isdecimal():
            continue  # A path with a numeric prefix is not necessarily a /proc PID.
        try:
            fields=dict(line.split(':',1) for line in path.read_text().splitlines() if ':' in line)
            raw_rss=fields.get('VmRSS')
            if raw_rss is None:
                continue  # Missing data is unavailable, not a measured zero.
            pieces=raw_rss.split()
            if len(pieces)!=2 or pieces[1]!='kB':
                continue
            rss=int(pieces[0])
            name=fields.get('Name','').strip()[:50]
            if rss<0 or not name:
                continue
            processes.append({'name':name,'rss_kb':rss})
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
    stream_complete=True
    for line in path.read_text().splitlines():
        try: row=json.loads(line)
        except ValueError:
            stream_complete=False
            continue
        if not isinstance(row,dict):
            stream_complete=False
            continue
        rows.append(row)
    values=lambda key:[r[key] for r in rows if key in r]
    def event_deltas():
        # A reset or a missing/corrupt intermediate sample makes both deltas
        # unknown; first/last subtraction alone can falsely report an OOM.
        if not stream_complete or len(rows)<2:return None,None
        observations=[]
        for row in rows:
            events=row.get('cgroup_v2_memory_events')
            if not isinstance(events,dict):return None,None
            oom,kill=events.get('oom'),events.get('oom_kill')
            if (type(oom) is not int or type(kill) is not int or
                    oom<0 or kill<0):return None,None
            observations.append((oom,kill))
        if any(curr[0]<prev[0] or curr[1]<prev[1]
               for prev,curr in zip(observations,observations[1:])):
            return None,None
        return (observations[-1][0]-observations[0][0],
                observations[-1][1]-observations[0][1])
    oom_delta,oom_kill_delta=event_deltas()
    return {'samples':len(rows),'minimum_available_kb':min(values('MemAvailable_kb'),default=None),
            'minimum_swap_free_kb':min(values('SwapFree_kb'),default=None),
            'maximum_top_process_rss_kb':max((p['rss_kb'] for r in rows for p in r.get('largest_processes',[])),default=None),
            'cgroup_v2_oom_delta':oom_delta,
            'cgroup_v2_oom_kill_delta':oom_kill_delta,
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
