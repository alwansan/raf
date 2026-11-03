# A9 / LOCAL-005 — independent client memory

- Session: `A9-20261103T100326Z-d3a8c7f1`. Registered 2026-11-03T10:03:26Z from live branch HEAD `cb95d4bb8b736013f996a7583e434775a5160223`.
- Owner constraints: feature/android-native-port only; CL read-only. No Unity/native build/APK/OBB/XAPK/release, no task changes; keep water authenticity gate and original .rgd/.meta/GUID intact. LEFT Mouse0/500ms and touch-to-mouse false unaffected.
- Read permanent prompts, AGENTS.md, current owner requirements, coordination README and templates, latest handoff/readiness synopsis.
- Coordination checked: A1 WATER-001, A2 DISPLAY-003, A3/A4/A5/A6 HAPTICS-008, previous FFT-FORMAT-009; no LOCAL-005 recorded at registration. Do not overwrite concurrent code.
- Initial goal: verify original offline single-player world initialization and .rgd save/load contract; identify a reproducible source-level defect and fix with CPU-only tests if supportable, not a fabricated world-success flag.
- Prior original/device evidence is historic to APK80; no new phone/Unity execution.
- Next: inspect exact current code and existing regression tests, decide bounded scope, update independent work/experiment records. 
