# B12 synthetic CI failures and corrected same-source quality dependency

Author: B12. Session: 20261104T2243Z-B12-bounded-tree-a9. Issue: PERF-007 and source fixture scope. UTC checkpoint 2026-11-04T22:58:16.930Z.

**Impact:** CI source/harness tests failed while adapting the B12 renderer diagnostic. No user device, native build or original Raft asset was modified. The previous B12 renderer snapshot lacked a traversal allocation cap; source fix remains independently checked by a successful original-managed integration workflow. No false READY claim.

## Observed evidence

- [41928389718](https://github.com/alwansan/raf/actions/runs/41928389718) FAILED because preexisting B12 synthetic assertions still expected the removed unbounded GetRootGameObjects() call; tests updated in 3bed5bd.
- [41928474901](https://github.com/alwansan/raf/actions/runs/41928474901) FAILED: policy test searched the forbidden API name in a *comment* explaining its removal. Production logic did not call that API. Source-only comment masking corrected in e53c7cd and exact regex in 37f52c9.
- [41928576412](https://github.com/alwansan/raf/actions/runs/41928576412) FAILED due incorrect escape layer for the test regex (not proof of production API call); corrected 37f52c9; [41928708023](https://github.com/alwansan/raf/actions/runs/41928708023) later SUCCESS.
- [41929186375](https://github.com/alwansan/raf/actions/runs/41929186375) FAILED C# fixture CS0103 OriginalQualityStateSnapshot missing. Concurrent quality owner added the real helper to AndroidTestDiagnostics; isolated harness extracted the coroutine without its same-source helper. B12 preserved other owner's source and updated generator 02030b2 to include genuine quality helper and synthetic QualitySettings values.
- **Recovery proof:** [41929419050](https://github.com/alwansan/raf/actions/runs/41929419050) COMPLETED SUCCESS: exact production coroutine and co-located helper executed under synthetic CLR scene graph for 8 bounded scenarios, 11 B12 unit tests plus 11 runtime trace tests PASS. [41928807641](https://github.com/alwansan/raf/actions/runs/41928807641) actual original managed offline CI SUCCESS on cdec4c6; subsequent unrelated original-managed [41928829509](https://github.com/alwansan/raf/actions/runs/41928829509) FAILED earlier at an unrelated Raft_Network operation-manifest digest mismatch, not at B12 C# compile. That distinct issue is not silently attributed to this repair.

## Closed reason and residual uncertainty

Fixture/compiler input coverage corrected, no need to rerun equivalent synthetic failure. No reported Android FPS, GPU-memory, original Water FFT, or mesh/shader pixel repair was measured; PERF-007 broader issue remains OPEN. Next device APK test should correlate logged truncated/limit_reason with actual scene performance and graphics errors. Do not change audio, Settings, touch, original asset/meta/GUID or protected branch.
