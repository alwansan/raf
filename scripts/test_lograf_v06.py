#!/usr/bin/env python3
"""Structural checks for v0.6 recorder resilience. Device testing still required."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
src=root/"app/src/main/java/com/alwansan/lograf"
capture=(src/"CaptureService.java").read_text()
sampler=(src/"PerformanceSampler.java").read_text()
metrics=(src/"SessionMetricsSummary.java").read_text()
remote=(src/"RemoteLogService.java").read_text()
ui=(src/"MainActivity.java").read_text()
signing=(root/"app/build.gradle").read_text()
checks={
    "pidof probe bounded to 2 seconds": 'p.waitFor(2000,java.util.concurrent.TimeUnit.MILLISECONDS)' in remote and 'p.destroyForcibly()' in remote,
    "pidof output capped with overflow sentinel": 'found.length()<=4096' in remote and '4097-found.length()' in remote,
    "pidof oversized output fails closed": 'if(found.length()>4096)' in remote and 'throw new IOException("pidof_output_overflow")' in remote,
    "reject pidof diagnostic text instead of reporting game absent": 'throw new IOException("pidof_invalid_output")' in remote and 'if(!item.matches("[0-9]+"))' in remote,
    "reject successful but empty pidof as ambiguous": 'if(exit==0 && current.isEmpty())' in remote and 'throw new IOException("pidof_empty_success")' in remote,
    "pidof exit status checked after completion": 'int exit=p.exitValue();' in remote,
    "stable Android app identity": "applicationId 'com.alwansan.lograf'" in signing,
    "stable update signing key": "signing/lograf-public-test.p12" in signing,
    "version v0.6": "versionName '0.6.'" in signing,
    "bounded queue count": "QUEUE_BATCH_LIMIT = 512" in capture,
    "bounded queue bytes": "QUEUE_BYTES_LIMIT = 12L*1024*1024" in capture,
    "async writer thread": '"lograf-saf-writer"' in capture,
    "explicit loss warning": "LOG BUFFER OVERFLOW" in capture,
    "no synchronous SAF in onBatch": "enqueue(source,content);" in capture,
    "accept stop tail batches": "if(!active || stopping)return;" not in capture and "if(!active)return;" in capture,
    "stop remote before disabling sink": capture.index('remote.stop();') < capture.index('active=false;',capture.index('private synchronized void halt')),
    "join writer before closing streams": capture.index('thread.join(18000)')<capture.index('if(output!=null) { try { output.flush(); output.close(); }',capture.index('private synchronized void halt')),
    "stop runs off Android main": '"lograf-stop"' in capture,
    "persist local overflow counters": '"writer_failed_batches"' in capture and '"writer_peak_pending_bytes"' in capture,
    "export session metrics": '"performance_statistics"' in capture,
    "aggregate observed samples": 'readable_samples' in metrics,
    "stale FPS distinguished": '"frame_telemetry_stale"' in sampler and '"fps_tracking_status"' in sampler,
    "do not fake zero for missing fps": 'return 0.0' not in sampler[sampler.index('private Double presentedFps'):],
    "PSS rejection marker": '"rejected_pss_exceeds_rss"' in sampler,
    "queue stats visible in UI": "writer_pending_bytes" in ui and "frame_telemetry_stale" in ui,
    "count only exact game process death events": 'processDeathEvents.incrementAndGet();' in remote[remote.index('packageName.equals(died.group(2).trim())'):] and remote.index('packageName.equals(died.group(2).trim())') < remote.index('processDeathEvents.incrementAndGet();'),
    "no false death on colon worker process": 'packageName.equals(died.group(2).trim())' in remote,
    "exit PID requires exact event package": 'packageName.equals(died.group(2).trim())' in remote,
    "exit PID cannot fall back to stale last known": 'lastDeathPid.set(lastKnownPid.get())' not in remote,
    "stop-time exit evidence": 'remote.finalExitEvidence()' in capture and 'stop_time_android_process_exit_info' in capture,
    "system context rejects substring package names": 'containsExactPackage(line,packageName)' in remote and 'isPackageCharacter(line.charAt(end))' in remote,
    "system context still accepts tracked PID": 'gamePids.contains(m.group(1))' in remote,
    "telemetry uses exact main process": 'return primaryGamePid.get();' in remote and 'packageName.equals(processCmdline(pid))' in remote,
    "no HashSet PID sampling": 'for(String pid:gamePids)' not in remote,
    "no guessed process PID when proc inaccessible": 'return selected;' in remote and 'int selected=-1;' in remote,
    "pidof failure invalidates stale process telemetry": 'primaryGamePid.set(-1);\n                synchronized(gamePids){gamePids.clear();}' in remote,
    "pidof exit status checked": 'int exit=p.exitValue();' in remote and 'if(exit!=0 && !verifiedEmpty)' in remote,
    "pidof no-match exit 1 is not probe failure": 'exit==1 && found.toString().trim().isEmpty()' in remote and 'pidProbeSuccesses.incrementAndGet();' in remote,
    "nonempty failed pidof is unverified": 'if(exit!=0 && !verifiedEmpty)' in remote and 'throw new IOException("pidof_exit_"+exit)' in remote,
    "pid probe failures explicitly measured": '"pid_probe_failures_total"' in remote and 'pidProbeFailures.incrementAndGet();' in remote,
    "pid probe successes measured": '"pid_probe_successes_total"' in remote and 'pidProbeSuccesses.incrementAndGet();' in remote,
    "unverified PID distinguished from stopped game": '"main_cmdline_unverified"' in remote and '"pidof_probe_failed"' in remote,
    "all PIDs retained for context": 'gamePids.addAll(current)' in remote,
    "raw Logcat unchanged target": '"--uid=" + gameUid' in remote,
    "error classes tracked without raw text": '"error_groups"' in remote and (src/"ErrorCategorySummary.java").exists(),
}
bad=[name for name,valid in checks.items() if not valid]
for name,valid in checks.items():print(("PASS" if valid else "FAIL")+" "+name)
if bad:raise SystemExit(f"Failed {len(bad)} checks: {', '.join(bad)}")
