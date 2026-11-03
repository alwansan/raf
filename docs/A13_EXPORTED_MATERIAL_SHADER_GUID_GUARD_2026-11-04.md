# A13 — exported Material → Shader GUID structural guard (4 November 2026)

Client: `raft-20261103T225600Z-a13e6b94`, session `a13-20261103T225600Z-76d14a0f`, resumed from completed A13 `raft-20261103T123129Z-6533d5b4`.

## Actual source and CI

The isolated read-only guard `scripts/probe_a13_exported_material_shader_guids.py` was introduced at [5ed6ff67](https://github.com/alwansan/raf/commit/5ed6ff67326dc7424deebb2da2458bf26808512f), synthetic tests at [a2e868b9](https://github.com/alwansan/raf/commit/a2e868b92d77f0169df64047d6d3f7d41bda464e), and no-LFS/no-Unity workflow at [236ad8f6](https://github.com/alwansan/raf/commit/236ad8f68d166afa1bc51c21e8ff886e855c8c62). [CI run 41735646696](https://github.com/alwansan/raf/actions/runs/41735646696), job 126264034218, **COMPLETED SUCCESS**, exact source SHA `236ad8f68d166afa1bc51c21e8ff886e855c8c62`. Log says **Ran 15 tests in 0.019s — OK**.

The guard parses exported Unity YAML `!u!21` Material records, requires one `m_Shader` per record, and resolves only non-builtin GUID references to unique `.shader.meta` GUID targets backed by a real `.shader` file. It fails closed on missing/wrong-type GUIDs, duplicate GUIDs, broken or absent metadata, null/negative pointers, invalid type, malformed/ambiguous fields, symlinks/unsafe root, over-size input, and mismatched optional expected Material count. Built-in transports are **counted separately as unresolved**, not fabricated Shader matches. Output is aggregate numbers and explicit false provenance/visual/build flags. It changes **no game resources, GUIDs or ShaderLab files**.

For a *future authenticated complete* AssetRipper export, run:
```bash
python3 -m scripts.probe_a13_exported_material_shader_guids --project /absolute/path/to/export
```
`--expected-materials N` must only be supplied when exact source/export record cardinality has independently been established. W3's 1556 source Material objects do **not** automatically imply 1556 loose exported `.mat` documents.

## Connection to authenticated source results and honest limits

Previous original A13 [CI 41660807306](https://github.com/alwansan/raf/actions/runs/41660807306): 514 Materials/105 Shaders across two owners, 358 internal source references resolved, 156 external initially unknown. W2/W3 later resolved external source owner tables and expanded to 82 authentic owners: **1556 Materials, 165 Shader objects, 437 internal and 1103 cross-owner source links**, plus **16 engine transports** kept separate. These source counts are NOT an audit of exported `.mat` GUIDs.

**This CI used synthetic fixtures only**. No complete actual AssetRipper/Unity export was supplied, inspected or certified, no source-to-export identity mapping validated, no original ShaderLab/FFT/pass restored, no Unity/APK/OBB/XAPK, phone GPU or new release. W1 currently owns shader program restoration; W2 color/materials; W3 original source graph; A1 FFT; A12R Blur. `WATER-001`, `RENDER-002` and `FFT-FORMAT-009` remain OPEN. Game **NOT_READY**, immutable-candidate full reviews **0/3**.

## Next precise step

When a same-stage authenticated *complete* export is available, run the guard on its actual `Assets` and compare each exported Material Shader GUID against original source owner/fileID/pathID identities and exported Shader `.meta` GUID, preserving built-in handling. Do not call a synthetic pass proof of exported fidelity; do not use zero-match bypasses or substitute generic shaders.
