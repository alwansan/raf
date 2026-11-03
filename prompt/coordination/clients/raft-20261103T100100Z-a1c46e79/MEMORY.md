# A1 – WATER-001 image-flow audit

- Registration UTC: 2026-11-03T10:02:07.944Z; base 2020291470b8c3dce96cfee1ca8ecec68c3e150d; session a1-20261103T100100Z-8e29b73d.
- Read owner instructions, STATUS, latest handoff, coordination protocol/templates, other client files and READINESS.
- Other clients: raft-20261103T095340Z-a81c6e42 (FFT format, paused); raft-20261103T095700Z-a2b31f4d (DISPLAY-003, active); raft-20261103T100042Z-afcedabb (HAPTICS-008, active). No overlapping files planned.
- Scope: synthetic SPIR-V image SSA parser integrity; avoid changing proprietary source/shaders, resource GUIDs, native requests, Unity/APK/OBB/XAPK/release/schedules and CL (read only).
- Prior registration attempt at base0911f614 failed due to GitHub reference error; no changes from that attempt were published, retry from live HEAD.
- Next: reproduce alias collision with test fixture and patch narrow audit logic only if demonstrated, run tests, record evidence and limitations.

## A1 verified patch checkpoint — 2026-11-03T10:07:06.360Z UTC

- Reproduction before patch: illegal duplicate `OpLoad` result20 yields single `write` binding0 although earlier operation defined binding2, with `all_image_operations_uniquely_traced=true`.
- After defensive tracked SSA uniqueness guard, 12/12 local Python tests pass; source [dc8533ba6df694b959fd37cb84c327584961642c](https://github.com/alwansan/raf/commit/dc8533ba6df694b959fd37cb84c327584961642c).
- [Synthetic Actions41616248165](https://github.com/alwansan/raf/actions/runs/41616248165) completed success; [original audit41616248166](https://github.com/alwansan/raf/actions/runs/41616248166) was running. Do not infer original GPU/Unity/device correctness.
- One initial git-ref update failed with unknown GraphQL error after concurrent HEAD movement; inspected HEAD and successfully rebased registration via expected_sha, no force.
- Other clients A2 DISPLAY and HAPTICS work appeared concurrently; no overlapping source edits and no incoming WATER discussion entries as of review.
- Resume from sourcedc8533ba6df694b959fd37cb84c327584961642c; review final original-resource audit then choose next independently scoped numeric/provenance issue. State paused; no background session execution.
