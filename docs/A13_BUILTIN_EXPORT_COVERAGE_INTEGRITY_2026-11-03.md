# A13 — fail-closed built-in ShaderLab export coverage integrity (3 Nov 2026)

Client: `raft-20261103T123129Z-6533d5b4` (A13). Issue: RENDER-002. Scope: read-only coverage diagnostics; not shader recovery or build.

## Source/run evidence

- Native early-test [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951), job 125878883840, source c7254f7, **FAILED before Unity** at `scripts.restore_builtin_shaders`: zero exported vendor identity matches. Before that, export report showed **140 ShaderLab files, each 1 pass, 0 compute**; TMP 11, PostFX 14+2 compute, Volumetric 3 were restored. This is historic pre-fix run, not a verification of current export or complete built-in inventory.
- Earlier [107-file subset coverage](../prompt/coordination/work/RENDER-002/raft-20261103T103610Z-4e91b2cd-coverage.json) found 24 empty + 83 non-vendor + 0 vendor matches; sample provenance was **not authenticated as the full failing export**.
- Existing A9 [identity source fix](A9_BUILTIN_SHADER_IDENTITY_GUARD_2026-11-03.md), A3 [path safety](A3_BUILTIN_SHADER_PATH_SAFETY_2026-11-03.md), A6 [commented include](A6_BUILTIN_SHADER_INCLUDE_COMMENTS_2026-11-03.md) are distinct and already validated; this does not modify their restorer.

## Actual scoped repair and verification

[Source `6bfde3425438`](https://github.com/alwansan/raf/commit/6bfde3425438d92aa5fc1313e489df5c502c1018) changes `scripts/probe_builtin_export_coverage.py` only as a **read-only auditor** and adds A13-owned tests/workflow. Its earlier regex scanned comment text as if it were ShaderLab declarations. The probe now calls the same comment-aware declaration reader and SHA-pinned official archive validator used by the authoritative restorer. This prevents synthetic `// Shader ...` or `/* Shader ... */` from being counted as a valid vendor match; malformed UTF-8 and unsafe symlink aliases fail instead of becoming negative matches.

The historic digest over file content SHA values alone can stay unchanged if an exported shader file moves without a content change. A new path-bound SHA-256 includes length-prefixed relative path, raw file size and file content SHA. The historic digest remains for backwards comparison. Duplicate declarations are aggregate counts, not leaked identities. `full_export_scope_verified=false` and `original_game_identity_authenticated=false` remain explicit; no source or names are disclosed or replaced.

- Independent [A13 CPU-only CI 41637048446](https://github.com/alwansan/raf/actions/runs/41637048446), job 125920757165: **COMPLETED SUCCESS** on exact source `6bfde3425438d92aa5fc1313e489df5c502c1018`, **9/9 tests**. Cases: legitimate vendor, line-comment false match, block-comment false parse, unchanged content/path-move digest divergence, duplicate aggregate/no identity leak, malformed UTF-8, symlink, empty tree, wrong archive fingerprint.
- [CI artifact 13231330739](https://github.com/alwansan/raf/actions/runs/41637048446/artifacts/13231330739) stores synthetic-only unittest output, 502-byte archive. Workflow concurrency group is independent and `cancel-in-progress: false`, timeout 6 minutes, `lfs: false`.
- Local same-case preflight was 9/9 with a tiny **synthetic replacement of the identity helper**. Unlike the final CI, local tests did not load the real repository helper, so rely on the exact-source CI for integration claims.

## Negative result, boundaries and next evidence

No authentic failing export or owner 107-subset provenance was transferred into this experiment; therefore **the zero vendor matches on the complete reconstructed game were neither reproduced nor repaired**. It remains unknown whether the original exporter omitted built-in ShaderLab objects, output stubs without official identity, or the actual full root differs from the subset. Never force a built-in replacement or skip the strict failure just to make the native pipeline appear successful. A future permitted diagnostic run must collect the actual complete export inventory at the failure step with an authenticated source/job SHA, count/path-bound digest, and export completion proof; compare with material/GUID references and known official identities before proposing any restoration change. That run is not authorized or executed by A13.

No original loose assets, proprietary ShaderLab/DXBC/SPIR-V sources, .meta/GUIDs, LFS content, Unity Editor/import, APK/OBB/XAPK/Release, native request files, CL or scheduled tasks modified. **RENDER-002/WATER-001/FFT-FORMAT-009 stay OPEN, game NOT_READY, full independent readiness audits 0/3.**
