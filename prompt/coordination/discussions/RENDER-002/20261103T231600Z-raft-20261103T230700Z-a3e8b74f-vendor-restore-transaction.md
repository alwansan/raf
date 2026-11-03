# A3 RENDER-002 — vendor restoration transaction fixed, independently verified

Scope: shared `scripts/restore_tmp_shaders.restore` consumed by original TMP 3.0.6, PostFX v1 and VolumetricLights restorers. This was not W1's built-in shader path, A1's FFT or W2/W3 materials.

[RED CI41737057615](https://github.com/alwansan/raf/actions/runs/41737057615) failed 4/5 synthetic production-code tests as expected: newly added shader includes and notice stranded during rollback, partial backup persisted and symlinked output parent redirected outside Unity. [Source fix ab556f12](https://github.com/alwansan/raf/commit/ab556f12d398e91b58fa6ed395d71ac6af2f1024) ensures safe original shader/meta-preserving backup and recoverable exclusive dependency publication. [GREEN CI41737411435](https://github.com/alwansan/raf/actions/runs/41737411435) SUCCESS: 5 new A3 +4 TMP+3 PostFX+6 Volumetric=18/18 tests.

No vendor original bytes downloaded, no .meta/GUID/ZIP2/LFS modified, no Unity/Android native build, pixel/GPU/phone result or scheduler change. W1/A1/W2/W3 work untouched. This closes only the source tool transaction defect; **RENDER-002/WATER-001/FFT-FORMAT-009 remain OPEN**, game **NOT_READY,0/3**. [Full report](../../../../docs/A3_VENDOR_SHADER_RESTORE_TRANSACTION_2026-11-04.md). Client `raft-20261103T230700Z-a3e8b74f` state completed; future A3 continuation must register separate session.
