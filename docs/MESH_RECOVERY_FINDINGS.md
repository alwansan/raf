# Raft Android port — mesh and asset link recovery diagnostics

**Verified on 2026-10-30**, branch `feature/android-native-port`. This is static-only research. No original game content, Unity Editor project or Android APK is published in this branch.

## Baseline — 40 levels with script identity registry but no shared game assets

[Run 41025306987](https://github.com/alwansan/raf/actions/runs/41025306987) loaded all 40 `levelN` scenes with `globalgamemanagers.assets`, restored all **64,642 / 64,642** `m_Script` GUID references, yet reported:

| Exported Unity YAML issue | Serialized reference count |
|---|---:|
| `deadbeef` placeholders across all scene properties | 393,450 |
| `deadbeef` `m_Mesh` references | 198,114 |
| `deadbeef` `m_Script` references | 0 |

**Important:** counts represent *uses*, not distinct missing mesh assets or source files. A single sentinel stands for numerous unresolved references. [Detailed script recovery](RECONSTRUCTION_STATUS.md).

## Expanded export using ALL available non-LFS Unity data

[Run 41025868800 — SUCCESS](https://github.com/alwansan/raf/actions/runs/41025868800)

A runner with adequate free storage staged **114** real files from regular Git, skipping **17 LFS pointer** files. The Unity export had 40 scenes and all 64,642 original script GUID links remained matched. No LFS data downloaded.

| Metric | Baseline | Expanded regular Git data | Improvement |
|---|---:|---:|---:|
| Total `deadbeef` references | 393,450 | 199,156 | -194,294 (-49.4%) |
| `m_Mesh` `deadbeef` references | 198,114 | 94,152 | -103,962 (-52.5%) |
| `m_Script` references correctly linked | 64,642 | 64,642 | no regression |

Mesh placeholders in the expanded export still use serialized `fileID: 4300000`, an **output-side** file ID, not enough to identify original input bundle. The independent source pointer analysis below provides the original locations.

## Independent source UnityPy mesh pointer analysis across all 40 levels

[Run 41026113254 — SUCCESS](https://github.com/alwansan/raf/actions/runs/41026113254)

`scripts/audit_source_mesh_pointers.py` used UnityPy 1.25.4 to inspect `MeshFilter`, `MeshCollider` and `SkinnedMeshRenderer` components in 40 original scene files and 3 extra ordinary-Git asset files. It parsed their **original** `m_Mesh.m_FileID/m_PathID` pointers and each serialized file's external dependencies.

- **174,314** `MeshFilter` components, **24,895** `MeshCollider`, **249** `SkinnedMeshRenderer` in the inspected sample. These class counts should not be conflated with the number of nonzero valid mesh references.
- **3,947** distinct source mesh pointer targets across the files sampled.
- PPtr target path counts below are uses in source components, **not** distinct Mesh files:

| Original mesh target file (highest-frequency examples) | Original pointer uses | Present in regular Git? |
|---|---:|---|
| `resources.assets` | **85,525** | **No, LFS only (111,533,516 bytes)** |
| `sharedassets30.assets` | 42,137 | Yes (its `.resS` stream is LFS) |
| `sharedassets34.assets` | 19,892 | Yes (its `.resS` stream is LFS) |
| `sharedassets24.assets` | 15,243 | Yes (its `.resS` stream is LFS) |
| `sharedassets35.assets` | 6,486 | Yes (its `.resS` stream is LFS) |
| `sharedassets6.assets` | 6,025 | Yes (its `.resS` stream is LFS) |
| `sharedassets0.assets` | **5,423** | **No, LFS only (115,978,112 bytes)** |
| `sharedassets25.assets` | 5,135 | Yes (its `.resS` stream is LFS) |
| `sharedassets29.assets` | 4,943 | Yes (its `.resS` stream is LFS) |
| `sharedassets36.assets` | 3,209 | Yes (its `.resS` stream is LFS) |

**Interpretation:** `resources.assets` has the strongest direct structural evidence for a high-impact selective LFS import, followed by resolving dependencies/streams for sharedasset groups. It is NOT yet proven that downloading that file fixes 85,525 exported placeholders one-to-one; exporter behavior, missing external data, built-in primitive objects, mesh serialization and unsupported shaders may still intervene.

## Next selected experiment — explicitly approved Git LFS transfer only

[Manual-only, opt-in GitHub Actions workflow](../.github/workflows/raft-opt-in-lfs-mesh-probe.yml)

The workflow has **no push trigger** and its default input is **NO - do not download**. The user must deliberately run it and choose:
- **106.4 MiB**: download only `resources.assets` (111,533,516 bytes), the largest referenced missing source container.
- **217.0 MiB**: download `resources.assets` and `sharedassets0.assets` (227,511,628 bytes combined).

The job will verify file size **and SHA256 against repository's LFS pointer**, stage only the approved objects alongside all regular Git files, and record before/after mesh placeholder counts, without publishing or committing extracted contents.

**Why manual?** Downloading Git LFS objects can consume bandwidth quota, and we cannot read the user's remaining free allowance or billing protection settings from this session. The earlier Git LFS upload of ~6.9 GiB does not prove downloads are free. Check GitHub billing/spending limits before activating.

No need to reupload AssetRipper or ILSpy; their install and checks have already succeeded in ephemeral CI. Unity 2021.3.45f2 Editor import/compile and Android build have **not** succeeded yet.

## Rights / distribution

The repository appears publicly accessible and contains a third-party commercial PC game's data. All CI tests are for private ephemeral local export and aggregate analysis. Avoid publishing extracted game resources, decompiled code or full derivative APK without authorization. No source or asset artifacts were uploaded by these workflows.
