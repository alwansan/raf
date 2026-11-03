# INPUT-005 A7: queued Mouse0 ghost click after a held gesture

- Author: A7 / `raft-20261103T105625Z-a7d793f4`; observed: 2026-11-03T11:04:54.381Z; scope: original authored platform button queue only.
- Status: **fixed at source level, CPU-only regression verified; phone runtime pending**.
- Evidence: red commit [6c54fdc9](https://github.com/alwansan/raf/commit/6c54fdc9ed140acd7a023c0e40060ad7c6e54ef1), [failed CPU-only platform CI41623753511](https://github.com/alwansan/raf/actions/runs/41623753511), job125875789242, exception `Touch boundary matrix: ghost-tap-after-hold-release`.
- Cause: `TouchPointerButtons` retained an earlier `pending` click when a later `Hold(true)` took ownership, and `BeginUpdate` replayed it only after `Hold(false)`.
- Source fix: [7693ea6c](https://github.com/alwansan/raf/commit/7693ea6c515e0fbea055fd1f68cf728710c51850) clears stale pending clicks at the start of a held gesture; `Tap()` during hold no longer queues phantom input. Subsequent genuine taps after release remain accepted.
- Added tests: [8570d2e6](https://github.com/alwansan/raf/commit/8570d2e6efc5d73000b4f515fa299bbd2582f539), tests two post-hold ghost conditions and a new valid post-release tap, without losing ordinary rapid-tap separation.
- Green CI: [platform41624236216](https://github.com/alwansan/raf/actions/runs/41624236216) (427 gesture checks and53 mapping), [final platform41624267337](https://github.com/alwansan/raf/actions/runs/41624267337) (430 gesture checks and53 mapping), and [offline source41624236295](https://github.com/alwansan/raf/actions/runs/41624236295) all SUCCESS on their exact source SHAs.
- Limits: deliberate prioritization means an undelivered queued short click is discarded on a new hold instead of replayed afterwards. Existing pure rapid-tap queue without hold is retained; Unity InputSystem/UGUI and hardware phone tests have NOT run. No authentic shader, original content, .meta/GUID, APK or build repaired by these tests.
- Recovery: if a later device test shows missed legitimate taps, inspect timestamp/order and design a time-aware event queue rather than re-enabling delayed post-hold pulses. Preserve LEFT Mouse0,500ms and physical devices.
