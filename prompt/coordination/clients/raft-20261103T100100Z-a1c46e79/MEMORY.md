# A1 – WATER-001 image-flow audit

- Registration UTC: 2026-11-03T10:02:07.944Z; base 2020291470b8c3dce96cfee1ca8ecec68c3e150d; session a1-20261103T100100Z-8e29b73d.
- Read owner instructions, STATUS, latest handoff, coordination protocol/templates, other client files and READINESS.
- Other clients: raft-20261103T095340Z-a81c6e42 (FFT format, paused); raft-20261103T095700Z-a2b31f4d (DISPLAY-003, active); raft-20261103T100042Z-afcedabb (HAPTICS-008, active). No overlapping files planned.
- Scope: synthetic SPIR-V image SSA parser integrity; avoid changing proprietary source/shaders, resource GUIDs, native requests, Unity/APK/OBB/XAPK/release/schedules and CL (read only).
- Prior registration attempt at base0911f614 failed due to GitHub reference error; no changes from that attempt were published, retry from live HEAD.
- Next: reproduce alias collision with test fixture and patch narrow audit logic only if demonstrated, run tests, record evidence and limitations.
