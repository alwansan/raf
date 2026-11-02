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
    "raw Logcat unchanged target": '"--uid=" + gameUid' in remote,
}
bad=[name for name,valid in checks.items() if not valid]
for name,valid in checks.items():print(("PASS" if valid else "FAIL")+" "+name)
if bad:raise SystemExit(f"Failed {len(bad)} checks: {', '.join(bad)}")
