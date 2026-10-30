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

## Verified latest: THREE LFS resource objects eliminate all exported deadbeef scene refs

[Run 41027328691: resources.assets only](https://github.com/alwansan/raf/actions/runs/41027328691) downloaded exactly 111,533,516 LFS bytes (SHA256 verified). 40 scenes and 64,642 script links passed, and placeholders fell to **37,111 total**, **8,631 m_Mesh**.

[Run 41028211970: + sharedassets0.assets](https://github.com/alwansan/raf/actions/runs/41028211970) downloaded 111,533,516 + 115,978,112 bytes, SHA256 verified, all scripts preserved; placeholders **6,697 total**, **3,233 m_Mesh**. These residual references all occurred in a single exported scene, `Landmark_Utopia`. This singled out a likely missing Utopia `sharedassets36.assets` input; independent source m_Mesh pointers previously found **3,209** uses of this asset file.

[Run 41028697081: + sharedassets36.assets](https://github.com/alwansan/raf/actions/runs/41028697081) added a third 110,149,324-byte LFS object (SHA256 verified), total three original resource containers **337,660,952 bytes (~322 MiB)**:
- **40/40** level scenes exported.
- **64,642/64,642** scene C# script GUID references still matched.
- **0 deadbeef** placeholders across exported scene references (previously 393,450).
- **0 deadbeef m_Mesh** links (previously 198,114).
- Export now includes **8,389 `.asset` files**, **888 `.prefab`**, **1,536 `.mat`**, **679 `.anim`**, **179 `.controller`**, **140 `.shader`** and 40 `.unity` scenes.
- This test did **not** download the larger `.resS` payloads or actually import/compile the project with Unity Editor. No material/mesh visual fidelity or working gameplay claim can be made until those tests pass.

The developer-run tests kept all proprietary extracted game resources on disposable runner storage; only numeric results were logged. The local 6-part archive was also discovered in this session; its embedded `Raft-SteamRIP.com.rar` archive was examined without running original binaries. Local `resources.assets`, `sharedassets0.assets`, and `sharedassets36.assets` were selectively extracted and their SHA256 digests matched repository LFS pointers. This may allow future local validation without additional LFS downloads when the same attached files are available.

**Next real gate**: combine full asset export with safe ILSpy C# overlays into one candidate project; inspect Unity package dependencies, and test Unity **2021.3.45f2** Editor import/compilation with legitimate activation. Large `.resS` streams may still contain essential vertex/textures, so zero scene GUID placeholders does NOT mean game is visually complete.

## 2026-10-30: no-network local RAR resource stream verification

A user-supplied compressed archive was already mounted in the private container. We verified that Linux `libarchive.so.13` can **read and selectively extract RAR5 content** without installing an external unrar executable.

Using the local RAR, we extracted exactly `Raft/Raft_Data/sharedassets25.assets.resS` into a disposable working directory, without uploading, executing or publishing game content. The result was **217,498,752 bytes**, with SHA256 `cee00266ec286c506b1e2b2689fb8cec16213efe1463638058786b830d4ffc84`, **identical to the stored Git LFS pointer**. The reusable parser/verifier is tracked in [`scripts/extract_raft_lfs_from_rar.py`](../scripts/extract_raft_lfs_from_rar.py); it reads the expected SHA256 and size directly from the local Git LFS pointer, restricts extraction to a specified `Raft/Raft_Data` path, and refuses mismatched content or overwriting existing output. It only needs an available source archive and Linux libarchive. 

This proves one large external mesh/texture stream can be recovered from the already uploaded archive **without further Git LFS bandwidth use**. It does **not** show all streams are present/correct or that the meshes are visibly valid in Unity. Continue with selective `.resS` content integrity and Unity Editor import tests rather than automatically downloading all remaining ~6.47 GiB LFS objects.

## 2026-10-30: safe local Mesh stream range coverage (no Git LFS download)

A follow-up [cheap coverage run 41097275762](https://github.com/alwansan/raf/actions/runs/41097275762) succeeded with 3/3 range/path synthetic tests. The updated `scripts/audit_mesh_stream_dependencies.py` can classify each sampled Mesh `m_StreamData.path`/`offset`/`size` against the currently available source files as `available-range`, `lfs-pointer`, `missing-file`, `out-of-bounds`, `invalid-range`, or `unsupported-path`. It never opens actual data ranges or downloads streams and refuses unsafe absolute/parent path reference matching.

On a checkout **without Git LFS** and sampling at most 80 Mesh objects per serialized file, the script counted **278** references to Mesh stream payloads: **32 locally available valid ranges**, **246 references whose source stream file is a Git LFS pointer**. LFS pointer counts are uses, not distinct missing assets, and do not imply data loss. The three resource containers that are ordinarily fetched in the full Unity CI have deliberately **not** been fetched for this cheap check; do not compare its `278` to the earlier `1877` full-header read count as though all files had been loaded.

Source streams, original Unity geometry and collisions remain distinct from serialized GUID reference linkage. Before expanding costly LFS retrieval, use the range audit to prioritize physically absent or truncated `.resS` content and separately check Unity collider import warnings.

## Exact non-finite source ranges — Work continuation

[Range audit 41124553138](https://github.com/alwansan/raf/actions/runs/41124553138) passed on commit `5b59f402`: 159 distinct non-finite-error names extracted, no header parse errors or rejected advertised ranges. The private ledger preserves original path IDs, offset/size, original LFS SHA256 and ambiguity; public output contains aggregate counts only.

| Stream prefix | Matched non-finite names | Unique referenced Mesh bytes |
|---|---:|---:|
| sharedassets24 | 15 | 890800 |
| sharedassets25 | 13 | 629888 |
| sharedassets29 | 22 | 2210584 |
| sharedassets30 | 19 | 1159296 |
| sharedassets34 | 24 | 1302336 |
| sharedassets35 | 34 | 2994520 |
| sharedassets6 | 3 | 106176 |

These are per-provider name counts, not proven fixes. Range bytes merge overlaps and are not downloadable LFS object sizes. The source-only [one-stream experiment 41124735861](https://github.com/alwansan/raf/actions/runs/41124735861) is queued at this checkpoint, selecting only sharedassets29.assets.resS (295782704 bytes) and validating SHA256/size before checking original decoded positions and triangle indices. It does not test AssetRipper or Unity cooking. Read its result before spending another transfer; do not infer success from scheduling.
