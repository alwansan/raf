# A12R incident — original Blur SHA-pinned third LFS owner unavailable in W1 cache

- Author: raft-20261103T190657Z-9004f68d, session a12r-20261103T190657Z-dbd4a448, UTC 2026-11-03T19:21:14.648Z
- Issue: WATER-001, [CPU-only run41701535937](https://github.com/alwansan/raf/actions/runs/41701535937), source [e378eeaf](https://github.com/alwansan/raf/commit/e378eeaf0dd14751e259cf643671e11b38a1e7f1)
- Actual outcome: 7/7 synthetic tests PASS, cached SHA-pointer checks PASS, W1 cache restore PASS. `git lfs checkout` printed skipped `Raft/Raft_Data/sharedassets36.assets`, content not local; original 14-owner provenance check refused, diagnostic original_verified=false; job126145781465 FAILED. This is not evidence of a shader parser or compiled CB mismatch.
- Impact: no authenticated original DXBC/RDEF CB comparison occurred; no ShaderLab installed; no change to original materials/GUIDs, no Unity build/phone trial.
- Privacy: [numeric-only artifact13263124031](https://github.com/alwansan/raf/actions/runs/41701535937/artifacts/13263124031) published safe status; no private source, CB name, DXBC or shader text.
- Safest recovery: locate/reuse authorized SHA-pinned 110149324-byte sharedassets36 owner in existing caches or source artifacts; never bypass `original_shader` 14-owner identity checks, invent bindings or silently fetch large LFS. When owner is present rerun same CPU-only experiment. Source readiness remains NOT_READY 0/3.
- Status: BLOCKED, safe rollback none needed.
