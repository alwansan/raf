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

## Follow-up: pass1 source versus destination disambiguated (2026-11-08 19:44 UTC)

Added an independent actual-IL **Material-argument-only** gate (source commit [61e9c8e](https://github.com/alwansan/raf/commit/61e9c8ebaeaa2054f62ca77603d3f173a3c723d5)) so the tool no longer discards a real Foam Material → Blit link merely because source/destination images are indirect. Validator now enforces exact material argument, local alias, classified image and unresolved-image count partitions; 14/14 source-free tests pass (test commit [b7eb7b6](https://github.com/alwansan/raf/commit/b7eb7b6854f432a9a222b7c6df847a0eec29c7e6)).

- **[CI42516309771](https://github.com/alwansan/raf/actions/runs/42516309771) SUCCESS** on source `b7eb7b6854f432a9a222b7c6df847a0eec29c7e6`, original SHA stages passed. Its safe-only artifact `13631821162` confirms `original_pass0_exact_Material_field_argument_calls=1`, `original_pass1_exact_Material_field_argument_calls=1`, **zero** local Material alias calls for either literal pass, `original_pass0_linked_Material_image_producers_unresolved=0` and `original_pass1_linked_Material_image_producers_unresolved=1`. This is stronger original IL evidence that BOTH passes consume the **exact original Foam Material FIELD**, even though pass1 images cannot be fully typed by this conservative analyzer.
- Added a fixed-string **first unresolved image operand** diagnostic without exporting any original callsite name, opcode, offset, IL, string or private hash; source [dc04f43](https://github.com/alwansan/raf/commit/dc04f43c7239d0b5b025052cf3540f96297dde2e). **[CI42516516391](https://github.com/alwansan/raf/actions/runs/42516516391) COMPLETED SUCCESS** (14/14 Python and C# selftest, SHA-original DLL and Shader owner, purge before artifact); job `128840612219`, safe artifact `13631856408`. Redacted log output:
  - `T2_FOAM_PASS0_FIRST_IMAGE_OPERAND none`
  - `T2_FOAM_PASS1_FIRST_IMAGE_OPERAND source_not_direct`
- This means pass1's **destination expression was accepted by the narrow typed-value parser** (either directly typed RenderTexture or null; the tool does not currently expose which), but its **source expression was not directly classifiable**. It does **not** mean source is null, invalid, or missing. A call result/complex field receiver/alias/branch may be valid in original code but deliberately unresolved. No source/target **object identity** or crosspass data-flow equivalence has been proven.
- Earlier [CI42516250915](https://github.com/alwansan/raf/actions/runs/42516250915) / [CI42516283628](https://github.com/alwansan/raf/actions/runs/42516283628) failed at intermediate schema/test changes, not authentic GPU/water rendering. Final source [CI42516516391] supersedes them with GREEN gates on the latest analyzer.
- **Next bounded technical experiment:** inspect the type and CIL stack effects of the source expression producer for original pass1 in private scratch, tracing its actual producer chain across typed method calls/local/field aliases, then independently verify whether pass0 destination and pass1 source refer to the same runtime RenderTexture instance. Keep unknown as unknown until proven; only then verify CB0/sampler/render state and Unity/phone graphics. No duplicate shared Mini or XAPK build.
