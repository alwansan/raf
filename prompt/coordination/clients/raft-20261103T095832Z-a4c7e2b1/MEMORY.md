# A4 HAPTICS-008 — 2026-11-03

- Identity: raft-20261103T095832Z-a4c7e2b1; session a4-20261103T095832Z-71d4c6b8. Registered from live HEAD af354e4154b915a99fd9ba55a37b63ce849a16f5.
- Boundaries: only feature/android-native-port writable; CL read only; no Unity/native/APK/OBB/XAPK, release, scheduled task, proprietary asset or LFS download.
- Read owner requirements, permanent prompts, coordination protocol and other clients. Existing FFT-FORMAT-009 and DISPLAY-003 work will not be overwritten.
- Scope: investigate missing haptics paths from historic APK80 phone logs against actual source; write an isolated falsifiable repair/test if evidence exists; do not misclassify old device logs as newly tested source.
- Next: inspect current implementation, CL exact paths, then validate any fix and update this memory and plan.

## Scope change / coordination

Two additional clients registered HAPTICS-008 while A4 inspected it (afcedabb and a5c842e1). A4 will not write their overlapping haptics assets, code or tests. Shifted to PERF-007 CI memory-evidence integrity. Reproduction target: missing VmRSS appears as measured zero; malformed/negative memory may be accepted. This is a CI diagnostics correction, not a phone GPU-OOM fix.
