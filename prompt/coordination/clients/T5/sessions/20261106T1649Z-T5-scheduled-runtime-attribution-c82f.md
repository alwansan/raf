# T5 scheduled — LogRaft process epoch attribution guard

- session_id: 20261106T1649Z-T5-scheduled-runtime-attribution-c82f
- origin: scheduled
- issue: PERF-007
- base_sha: 2fc2a5c2237fc63df67e23a76d320418746a0033
- work reservation: prompt/coordination/work/PERF-007/20261106T1649Z-T5-scheduled-runtime-attribution-c82f.json (commit bb0c9ec7a99de9e15076db41a937159c0a9c94ee)
- resumed_from: 20261106T0138Z-T5-chat-performance-cohort-7ab4.md; 20261106T1541Z-T5-chat-obb-routes-b8a1.md
- source commits: 858e7f129dd86255ddf3d05c292e7e23e9d0d761 and 28906440a71b02126e524f79593e389cfb955353
- source files: scripts/t5_cl_pid_epoch_audit.py; tests/test_t5_cl_pid_epoch_audit.py
- experiment_key: T5-owner42058825739-LogRaft-SurfaceFlinger-vs-Unity-HUD-attribution-readonly-v1
- status: SOURCE_FIXED / awaiting independent CI or local regression execution

## Findings
The existing LogRaft cohort parser validates increasing timestamps and verified PID *per sample*, but does not forbid aggregating samples across verified PID changes (Raft process restarts). This is a concrete comparability gap: the same session can mix different process lifetimes, masking a restart or introducing false FPS improvements. Added a source-free process-epoch guard which separates verified PID transitions and unverified running-PID intervals, reports only epoch indices/counts (never actual PIDs), and refuses whole-session aggregation unless one verified process epoch is established. Added four regression cases: stable PID, verified PID change, unknown PID interval, and empty input. No original device logs, assets, .rgd, Unity, APK/OBB, shaders or shared workflows changed.

## Existing verified evidence (not re-run)
- Owner device 42058825739: world entry/save/exit/reentry succeeded on original e9c358e, while package publication failed.
- Original signed APK SHA/signature CI42228262902 and OBB full SHA/CRC CI42230326050; optional patch GUID warning does not establish main OBB corruption.
- Signed main OBB route metadata CI42248117179 confirms FMOD/Haptics paths only, not installed device mount.
- Reported LogRaft presentation FPS is SurfaceFlinger estimate, not Unity frame time or GPU duration. Owner's 18.27 FPS / p95 82.82ms HUD screenshot must not be treated as equivalent to GPU p95.

## Boundaries and next step
This source guard is not yet connected to the existing comparison CLI and its new unit tests have not been independently run in Actions; do not claim CI PASS or improved device performance. Before integration, run `python -m unittest tests.test_t5_cl_pid_epoch_audit` and decide whether to reject or segment PID restarts in the existing cohort CLI after coordinating with chat T5. Then link exact installed APK/OBB hash and same-scene phone telemetry. No native build or duplicate CI requested. NOT_READY 0/3.
