# A4 HAPTICS-008 — 2026-11-03

- Identity: raft-20261103T095832Z-a4c7e2b1; session a4-20261103T095832Z-71d4c6b8. Registered from live HEAD af354e4154b915a99fd9ba55a37b63ce849a16f5.
- Boundaries: only feature/android-native-port writable; CL read only; no Unity/native/APK/OBB/XAPK, release, scheduled task, proprietary asset or LFS download.
- Read owner requirements, permanent prompts, coordination protocol and other clients. Existing FFT-FORMAT-009 and DISPLAY-003 work will not be overwritten.
- Scope: investigate missing haptics paths from historic APK80 phone logs against actual source; write an isolated falsifiable repair/test if evidence exists; do not misclassify old device logs as newly tested source.
- Next: inspect current implementation, CL exact paths, then validate any fix and update this memory and plan.

## Scope change / coordination

Two additional clients registered HAPTICS-008 while A4 inspected it (afcedabb and a5c842e1). A4 will not write their overlapping haptics assets, code or tests. Shifted to PERF-007 CI memory-evidence integrity. Reproduction target: missing VmRSS appears as measured zero; malformed/negative memory may be accepted. This is a CI diagnostics correction, not a phone GPU-OOM fix.


<!-- A4-PERF007-FINAL-20261103 -->
## Verified A4 result and next checkpoint

- Source 1b37647587e94b4e3a7baf6e34865c634a442216 adjusted only `scripts/ci_memory_watch.py` and `tests/test_ci_memory_watch.py`: absent VmRSS no longer fabricates measured zero; negative/malformed units and fake PID prefix excluded; actual 0 remains valid.
- https://github.com/alwansan/raf/actions/runs/41616939992, job125852628608: **COMPLETED SUCCESS**, eight Python tests incl. two new negative controls; live 3-sample runner monitor and 256MiB swap capability PASS. Also [preflight 41616940049](https://github.com/alwansan/raf/actions/runs/41616940049) success on same SHA. Neither runs original game or phone.
- Status/handoff evidence saved in [0b847d4c](https://github.com/alwansan/raf/commit/0b847d4c526b7612f52238de1c5d803a4a078509). HAPTICS code left untouched because concurrent clients registered it; A4 scope moved to PERF-007.
- Multiple transient GitHub GraphQL update_ref errors under moving HEAD were safely re-based with expected SHA. No forced ref update or interrupted jobs.
- No gameplay GPU OOM, water shader/FFT, Unity, phone acceptance, APK/OBB/XAPK or readiness claim; NOT_READY/0-of-3. No .meta/GUID, left Mouse0/500ms, UGUI/controller, LFS, CL or task change. A4 scoped task completed; no asynchronous activity.
