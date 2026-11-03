# A11 RENDER-002: same-stage built-in ShaderLab identity audit v3 — 2026-11-03

## Source / proof

- Original A11 identity `raft-20261103T123040Z-02fe66b3`; resumed session `a11-resume-20261103T2255Z-c6f3a290`. All changes on `feature/android-native-port`.
- [code/test commit 04a4eefea](https://github.com/alwansan/raf/commit/04a4eefea18a8bff9059e8217d801b9ef87576de).
- [CPU-only CI 41735395961](https://github.com/alwansan/raf/actions/runs/41735395961), job 126263178117: **completed success 23/23** synthetic unit tests in 0.319s. Artifact 13277394069 retains aggregate test log only.

## Change

The A11 read-only `scripts/probe_a11_shader_export_scope.py` now accepts `--audit-stage-builtin-archive <localSHA-pinned-archive>` together with required `--project`, `--expected-shaders`, `--expected-computes`. On this single supplied export scope it verifies shader+compute counts, sources and .meta GUID integrity, invokes the existing official Unity 2021.3.45f2 SHA-256 pinned archive loader, applies the same comment-aware ShaderLab identity decoder as the real restorer, rejects duplicate built-in identities and invalid inputs, and compares pre/post complete inventory digests to catch mutation during inspection. It prints numeric counts and digests only; no proprietary paths, shader identities or shader source are logged. It does not restore or modify shaders.

Six new synthetic cases test exact built-in match, mandatory counts/mismatch, wrong archive, concurrent shader modification, duplicate built-in identity, and CLI limited output. Existing 17 synthetic regressions remain green.

## Explicit limits

**Original complete AssetRipper export not inspected in this CI.** The historical native run 41624581951 stopped before Unity at zero vendor identity matches, and its 140 shader files are not proven same-stage comparable to the 107-file local sample. Synthetic test success proves only the helper's behavior. `original_export_provenance_verified=false`, `original_gpu_shader_execution_verified=false`, `ready_for_build=false` remain explicit. WATER-001, RENDER-002 and FFT-FORMAT-009 remain OPEN; overall NOT_READY and 0/3 readiness reviews. No original data, Unity, native deliverable, LFS pull or ZIP2 download was initiated.

## Next engineering gate

Capture authoritative original complete AssetRipper export in the same reconstruction stage immediately *before* any replacement or restoration, with pinned ZIP2 original input reconstruction (size/SHA verification), original export counts, actual Unity built-in archive path, and tool/version/provenance. Run the new read-only audit before original-source mutation. Investigate any zero real matches without inventing aliases or weakening source gates.
