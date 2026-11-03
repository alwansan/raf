# A1 resumed – SPIR-V image operation coverage

- Session a1-20261103T104800Z-c9d8612a, 2026-11-03T10:48:31.736Z; resumed_from raft-20261103T100100Z-a1c46e79 (paused, parser collision repair completed).
- Live base 802e82fc599822a328057d7da7aee05b045605ad; protected branches main/zip/Unity-Editor untouched; CL read-only.
- Read owner/prompt/STATUS/AGENTS and coordination requirements; previous A1 synthetic CI 41616248165 and SHA-pinned original 41616248166 SUCCESS, but no actual shader equivalence; WATER-001 remains open.
- Other WATER work raft-20261103T103610Z-4e91b2cd (original caller precision; paused) touches probe_fft_caller_policy.py, not image-flow parser. Prior A1 was paused; no evidence of current concurrent edit to image-flow parser. Read WATER-001 plan/discussions before working.
- Focus: check omissions in sampled image/gather resource-use accounting against Khronos SPIR-V grammar; synthetic only, no proprietary shader bytes or GPU execution.
- Next: add regression fixture first, then narrow fail-closed/complete tracing behavior, run local tests and only then source commit. Stay NOT_READY/0-of-3.

## A1 verified scanner repair — 2026-11-03T10:55:27.346Z

- Reproduction: adding synthetic opcode87 with image ID199 to valid fixture leaves prior scanner incorrectly `all_image_operations_uniquely_traced=true`. The test was FAIL before change, PASS after.
- Commit 13bd0330904b48eb58fad73e27b7299e0d08b230; core+ sparse image sampling, gather, query, sparse read/fetch and texel pointer visibility, pointer opcode correction (70 vs68), recognized-image truncation checks. No original game code/assets edited.
- Local 17/17 Python tests PASS. CI https://github.com/alwansan/raf/actions/runs/41622977666 SUCCESS, job125873109925, same source logs 17 tests OK. Authenticated audit https://github.com/alwansan/raf/actions/runs/41622977691 completed/success at checkpoint; do not claim resource success.
- Existing other WATER agent raft-20261103T103610Z-4e91b2cd on caller-policy and raft-20261103T095340Z-a81c6e42 on precision; latest concurrent work is distinct. CL/raft log/lf has only four 2026-11-02 folders, historical APK80 not updated by source fix.
- Branch ref leases on two attempted rebases returned transient GitHub GraphQL UNKNOWN during concurrent pushes; refreshed HEAD and successful expected_sha publish based on 84c027f591c02106b739ad62d4055c848d24ff13, no force or lost-source overwrite.
- This scanner is limited; neither numeric GPU equivalence nor completeness for vendor extensions nor Unity/runtime correctness. WATER-001, RENDER-002, FFT-FORMAT-009 remain OPEN; NOT_READY/0-of-3.
- Scope complete and state paused; no background work.
