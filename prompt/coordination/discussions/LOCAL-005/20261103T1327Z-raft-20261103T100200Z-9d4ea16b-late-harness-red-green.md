# A10 LOCAL-005 — late harness original C# mutation RED/GREEN complete

- After explicit Continue, A10 resumed its completed identity with fresh session a10-20261103T1322Z-84bd630a.
- Defect: source-only private ILSpy test prepare() called install_adapted_originals() before parsing the original local RPC/save methods and generating test scaffold; late failure left modified original class.
- RED test commit: https://github.com/alwansan/raf/commit/dedf795a7e26b5eea8a558a0ad436edd79e89c4a
- RED CI: https://github.com/alwansan/raf/actions/runs/41643936030 (intentional assertion failure proved byte mismatch).
- GREEN fix commit: https://github.com/alwansan/raf/commit/057222022c132a910f04b0b6fdc4704ed6dc0634
- GREEN CI: https://github.com/alwansan/raf/actions/runs/41644049824, 11 A10 tests PASS, 12 private original sources, original local RPC/identity harness PASS, .NET diagnostic compile exit0.
- Code installs original C# as final prepare() step after all scaffold succeeds, retaining preflight and write-failure rollback.
- Scope only scripts/verify_android_offline_candidate.py, A10 tests and A10 records; no original RGD data or game source export committed, .meta/GUID unchanged.
- Related inactive preview 41624581951 failed at built-in shaders before Unity and is under separate RENDER work; A10 did not request native build.
- Broader LOCAL-005 original world/.rgd runtime and WATER-001/RENDER-002/FFT-FORMAT-009 open; NOT_READY, 0/3; no phone/device claim.

Work and experiment: ../../work/LOCAL-005/raft-20261103T100200Z-9d4ea16b-late-harness-failure-safety.json and ../../experiments/raft-20261103T100200Z-9d4ea16b/late-private-harness-source-mutation-20261103.json.
