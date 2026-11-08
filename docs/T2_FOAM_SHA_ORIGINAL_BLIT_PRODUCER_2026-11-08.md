# T2 — SHA-original Foam Graphics.Blit typed operand audit (2026-11-08 UTC)

**Worker:** T2 / chat session `20261108T1925Z-T2-chat-original-blit-cecil-v2` · **Issue:** WATER-001 OPEN · **Evidence grade:** SHA-original static managed IL (not Unity/GPU/device).

## Distinct engineering question

Prior synthetic `scripts/t2_foam_blit_operand_gate.py` 10/10 CI [42512807487](https://github.com/alwansan/raf/actions/runs/42512807487) checks only *caller-constructed* normalized CIL fixtures. Earlier authentic `FoamShaderFindResultFlow` proved a unique SHA-original Shader.Find→Material chain and the presence of two explicit pass literals, but **not the real Foam source/destination texture instances**. The new independent scanner `android-port/Experiments/T2/FoamBlitOriginalProducers/` examines **actual Mono.Cecil instructions from the original managed DLL** and requires the exact original Shader.Find→shader field→Material(Shader)→material field lineage before assigning type-only Blit roles. It refuses private names in output and does not follow ambiguous CFG/complex producers.

## Original input and CI verification

- Immutable original `zip2` checkout `15964ea8f246b6e076ce26b60931ee2e1a9a2385` (read-only).
- Original `Raft_Data/Managed/Assembly-CSharp.dll`: **3,211,776 bytes**, exact SHA256 verified independently against `RAFT_FILE_MANIFEST.tsv` before the managed scanner; scanner independently recomputes the expected DLL SHA256 from private runner input. No hash pin weakened.
- Original `Raft_Data/sharedassets0.assets`: **115,978,112 bytes**, reconstructed via pinned ZIP2 and independently SHA256-verified before extracting original Foam Shader `m_Name` to ephemeral private scratch. `UnityPy==1.25.4` and `Mono.Cecil==0.11.5` in pinned project.
- Workflow `.github/workflows/raft-t2-foam-original-blit-producers.yml`, 25-minute bound, `lfs:false`, isolated no-cancel concurrency, no Unity/native build. Source C# and strict Python safe validator `scripts/t2_foam_original_blit_report.py` with **11/11 source-free tests**. No game assets/IL uploaded.
- Initial [CI42515708324](https://github.com/alwansan/raf/actions/runs/42515708324) failed at missing source-only sparse-checkout import, **not Cecil**. [CI42515827760](https://github.com/alwansan/raf/actions/runs/42515827760) independently verified DLL/Shader owner SHA but failed private name extraction because additional Python parser modules were omitted. Both were fixed **only** by expanding source scripts checkout; no original bytes or proof flags were changed.
- **Final [CI42515921184](https://github.com/alwansan/raf/actions/runs/42515921184) COMPLETED SUCCESS** on workflow source `0c3e2973119d5daf378acea1aafc71292e4993d8`; job ID `128838799242`. Gates passed: Python 11/11, Cecil compile+selftest, original ZIP2 SHA validation, private shader name extraction, actual original managed IL scan and exact safe JSON validator, cleanup and artifact upload. Safe artifact ID **13631596355** (ZIP size 688B, one JSON report 1,414B). SHA256 of ZIP transport `44c5ecead65609ec6b243e6fb4afabeff8494fa869189c55add6af37d3629b25`. No private payload published.

## Verified source-actual bounded result

| Original source observation | Count / result |
|---|---:|
| Original managed method bodies scanned | **19,118** |
| Typed Unity Shader.Find calls | **81** |
| Direct Shader.Find with SHA-original Foam name | **1** |
| Original Shader field resolved | **true** |
| Original Material(Shader) constructor sites in that chain | **1** |
| Original Material field uniquely traced from constructor | **true** |
| Static four-parameter Graphics.Blit overload calls over whole Assembly | **66** |
| Explicit pass literal 0 within those original Blit calls | **18** |
| Explicit pass literal 1 within those original Blit calls | **11** |
| Other/dynamic pass expressions among Blit calls | **37** |
| Blit calls with **direct** exact Foam Material field plus both directly typed image producers | **1** |
| Directly typed Foam pass0 candidates | **1** |
| Directly typed Foam pass1 candidates | **0** |

**Pass0:** source type `RenderTexture` (producer `typed_field`), destination type `RenderTexture` (producer `typed_field`). This is a bounded ORIGINAL source-IL type classification of the single direct pass0 path, **not proof of target texture object instance or texture data contents**.

**Pass1:** source `unknown`, destination `unknown`; no direct field+two direct image producers survived the strict original scanner. This is **unresolved**, not evidence original pass1 is missing or broken. Other material alias, nested producer, branch, or call could require an authenticated data-flow model; the current limited scanner does not support promoting it.

Safe-report flags were `original_shader_to_blit_direct_field_types_confirmed=false`, `original_texture_instance_identity_proven=false`, `original_crosspass_destination_to_source_identity_proven=false`, `original_CB0_sampler_binding_verified=false`, `original_ShaderLab_Unity_or_Android_pixels_verified=false`, `private_names_IL_methods_fields_pathids_or_bytecode_exported=false`.

### Important denominators

Numbers **66 / 18 / 11 / 37** describe **all** typed four-parameter `Graphics.Blit` calls in the managed DLL, not 66 Foam calls. Only the **1** pass0 site is currently linked through the exact source-original Foam Material field and directly typed source/target producers. Do not relabel 18 or 11 global pass literals as Foam shader passes. The actual old fieldApi report's synthetic/cumulative categories remain separate.

## Acceptance boundaries and next engineering step

Do not publish or install purported original Foam ShaderLab or change CB0/texture samplers based solely on these types. Next privately inspect **why pass1 is unresolved**, differentiating (a) exact original Material field reaching the call but indirect image producer, (b) local material alias, (c) branch/exception handler, (d) call/field producer requiring evaluation stack proof. Add a bounded original-IL **reason-code** census with fixed safe enumerations and explicit zero/unknown handling; never export original method names, offsets, PathIDs, string hashes, raw CIL or shader/asset bytes.

When unique source/destination **instance** identities, correct pass order, CB0 uniforms/samplers, render states and Unity bindings are independently verified, then real Unity 2021 compile and Android pixels can be tested. Existing shared Mini APK [42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) already includes T2 GLES controls (not original water). Do not duplicate Mini or full Unity XAPK, do not change other workers' votes. **WATER-001 OPEN; full game NOT_READY.**
