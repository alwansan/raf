# T2 — SHA-original four-owner Material→Shader PPtr external file graph

**Session:** `20261106T1544Z-T2-chat-four-original-owners-pptr-6a71` • **origin:** chat • **issue:** WATER-001 **OPEN / NOT_READY**

## Proven input and prior blocker

The directly traceable original managed `Shader.Find → UnityEngine.Shader field → new Material(Shader) → Material.SetVector` chain was proven on source-original SHA-pinned `Assembly-CSharp.dll`, but its actual `Shader.Find` first string argument **does not match** original Foam Shader serialized `m_Name` ([CI42229056366](https://github.com/alwansan/raf/actions/runs/42229056366)). A shared constant-buffer member name is therefore **not Foam Shader identity proof**.

The preceding one-owner authentic [CI42243327311](https://github.com/alwansan/raf/actions/runs/42243327311) enumerated **58 Shader** and **351 Material** objects in `Raft_Data/sharedassets0.assets`, showing zero local `Material.m_Shader` references to original Foam Shader `fileID=0,pathID=2420`, while identifying **seven external Shader PPtrs** without resolving their external table. The current experiment expands and resolves the owner graph only where SHA-pinned source files and type-identifiable `Shader` objects are known.

## Source authenticity

Immutable ZIP2 source commit: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. New independent T2 CI uses `scripts/w1_stage_zip2_owners.py` to reconstruct **only four pre-pinned original assets** with exact original manifest, byte counts and SHA256:

| Original owner | Original bytes | Source SHA256 |
|---|---:|---|
| `Raft_Data/resources.assets` | 111,533,516 | `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c` |
| `Raft_Data/sharedassets0.assets` | 115,978,112 | `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` |
| `Raft_Data/Resources/unity default resources` | 4,832,808 | `026e6d1d96dc2e28c72ece25f2419469d649a95e25b6929bc5cfc95bca529f8e` |
| `Raft_Data/Resources/unity_builtin_extra` | 936,628 | `0eb8f0a4ea47b075a6b637abc02d0c7930d96cb9f6c5d723819eb8042cfb3886` |
| **Total** | **233,281,064** | **Each owner independently SHA-verified** |

Original Foam Shader is source-pinned in `sharedassets0.assets` at PathID **2420**, raw object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.

## New reusable original-source-only tool and fail-closed verification

T2 registered an independent work scope before modifying any source and added:
- `scripts/t2_foam_original_external_pptr_graph.py`: read-only UnityPy **1.25.4** enumeration of source-authenticated Shader object PathIDs, Material `m_Shader` PPtrs, and each source file's serialized `externals` table. The `m_FileID` is **zero for same owner**, or **one-indexed into the external file table**. Never attribute a matching `m_PathID` in the wrong source file to Foam.
- `tests/test_t2_foam_original_external_pptr_graph.py`: **8 synthetic adversarial controls** for filename normalization, one-based external indexing, foreign local PathID collisions, wrong object types, unknown/unpinned externals, malformed/null pointers, unknown preservation, original Foam object presence and output privacy. No original game bytes run in synthetic tests.
- `.github/workflows/raft-t2-foam-original-external-pptr.yml`: separate independent source-only workflow, `ubuntu-24.04`, bounded CI timeout and source volume, original ZIP2 sparse checkout and SHA pins, no LFS, no native Unity build. The original staged 233 MB bytes are removed before publishing only a safe aggregate JSON artifact.

Only four **public provider tags** and finite aggregate numbers are output. Source-private external paths, names and GUIDs stay in private runner memory. **Important:** matching an external basename and target PathID under independently verified SHA files is a *candidate* reference, not proof of Unity's actual runtime GUID dereference/asset loading. The tool explicitly emits `external_file_basename_is_actual_Shader_GUID_identity_verified=false`.

## Actual original experiment

**Definitive original [GitHub Actions 42247200163](https://github.com/alwansan/raf/actions/runs/42247200163)**, job `127992415067`, source commit `805901f738d54b54a01992e3624d24c06c8cdc97`: **SUCCESS**. Eight sourcefree tests passed; source ZIP2 commit, four owner exact byte sizes and SHA256 passed; source-only graph and safe JSON assertions passed. Original binaries never executed.

| Verified within these four pinned owners | Source-authentic count |
|---|---:|
| Original `Material` objects read | **516** |
| Original `Shader` objects read | **165** |
| Unreadable Material Shader pointers | **0** |
| Material Shader PPtrs pointing to external files | **156** |
| External PPtrs whose filename+PathID identifies a typed Shader in one of the four SHA-pinned providers | **154 candidates** |
| External PPtrs whose provider cannot be matched in these four pinned owners | **2** |
| Malformed external `fileID` indexes | **0** |
| Any Material local same-file pointer to original Foam Shader | **0** |
| Any external basename+PathID candidate for original Foam Shader | **0** |
| Unity runtime PPtr→GUID and actual Foam binding verified | **NO** |
| Actual complete Foam CB0 upload to GPU / Android Adreno water | **NO** |

| Original owner tag | Shader | Material | PPtr to known typed Shader in pinned owners | Unresolved external PPtr |
|---|---:|---:|---:|---:|
| `resources` | 47 | 163 | 149 | 0 |
| `sharedassets0` | 58 | 351 | 5 | 2 |
| `unity_default_resources` | 6 | 2 | 0 | 0 |
| `unity_builtin_extra` | 54 | 0 | 0 | 0 |

The seven external references previously observed in `sharedassets0.assets` now separate into **five filename/typed-target candidates** within the known pinned providers and **two targets still unresolvable by these four providers**. None of the 516 Materials has an authenticated direct local Foam pointer or even an external basename/PathID Foam candidate in these four files.

### Scope of negative result and next distinct experiment

This does **not** prove the real Raft Foam Shader has no Materials or never runs. Other `sharedassets*`, scenes, prefabs, asset bundles, dynamically assigned materials or scripts may reference Foam. In addition, source `externals` table names are not verified live runtime GUID values. No disallowed extrapolation from absence in four owners to all original game objects.

**Next concrete step:** from the two unresolved `sharedassets0.assets` external pointers, match their **file-table referenced source file identities** to the immutable ZIP2 `RAFT_FILE_MANIFEST.tsv` in private scratch, choose uniquely source-verified candidates for staging, and then compare actual external target Shader object PathID and original Foam references. Do not guess filenames from a common Shader property name or rewrite game Shader/.meta/GUID. Original pass0 Fragment / pass1 Vertex CB0 reflected extent/byte-upload requirements and real Android pixels are independently OPEN.

No shared Unity/native game source, ShaderLab, original asset, material, scene, prefab, GUID/.meta, audio, Settings, touch, save/world, APK, OBB or other T-agent files changed by this experiment.
