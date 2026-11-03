# W2 original external Material pointer classification — 3 November 2026

> **Coordination context (recorded):** while this probe was executed, peer W3
> (`raft-20261103T153100Z-b4d2c9e7`, ~15:45Z) independently published the same
> A13 follow-up with parsed-form names: [W3 report](W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.md)
> and [aggregate JSON](W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.json).
> The two runs agree numerically at every point of intersection (144 custom +
> 12 engine transports, 11 distinct target objects; W3: Skin_Amplify 50,
> Nature/SpeedTree8 41, Standard 29, …). W2's work stands deliberately as an
> **independent verification** that also extends the result to the unused
> parts W3 left fail-closed: the material **texture-environment** channel,
> cross-owner **target-existence validation**, and the documented
> **one-vs-zero-based convention control**. No W3 file was modified.

Client W2 `raft-20261103T152008Z-92502b76`. This is the declared next step from
A13's [original material links report](A13_ORIGINAL_MATERIAL_SHADER_LINKS_2026-11-03.md):
classify the **156 external Material m_Shader pointers** using each owner's
serialized-file external dependency table (`m_Externals`). CPU-only; two
SHA-pinned original owners; no Unity, no GPU, no LFS beyond the already
established two-owner set.

## Inputs (independently re-authenticated before parsing)

| Owner | Bytes | SHA256 |
|---|---:|---|
| `resources.assets` | 111,533,516 | `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c` |
| `sharedassets0.assets` | 115,978,112 | `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` |

Existence-validation owners (tracked regular files, hashed at run time — counts
only are published): `globalgamemanagers.assets`,
`Resources/unity default resources`, `Resources/unity_builtin_extra`.

## Pointer convention established by direct evidence

`external_id = m_FileID - 1` (one-based into `m_Externals`). Evidence:

1. Automatic **cross-owner existence validation**: under one-based reading every
   referenced `m_PathID` exists as an actual `Shader`/`Texture2D` object in the
   physical owner file; under a zero-based reading **zero** of the 156 pointers
   landed on a Shader in the physically loaded builtin owners, and the two
   conventions disagree on the resolved owner name for **310** of the 315
   external pointers (0-based interpretation is refuted, not merely unproven).
2. UnityPy's own `PPtr.deref` implements `m_FileID - 1` — the engine
   convention matches an existing trusted implementation.

## Aggregate results (local authenticated run)

### Material → Shader (m_FileID != 0): 156/156 resolve to named owners

| Owner | fileID | Target owner | Pointers | Distinct target objects | Target exists |
|---|---|---|---:|---:|---|
| resources.assets | 3 | `sharedassets0.assets` (original custom shaders) | 142 | 9 | yes |
| resources.assets | 2 | `Library/unity default resources` (engine builtin) | 7 | 1 | yes |
| sharedassets0.assets | 3 | `Library/unity default resources` (engine builtin) | 5 | 1 | yes |
| sharedassets0.assets | 1 | `globalgamemanagers.assets` | 2 | 2 | yes |

Cross-owner target existence validation: **all 315 external target path IDs
(156 shader + 159 texture) exist as actual objects in the named physical
owner files; 0 missing** (validated against locally hashed copies of the three
tracked files above). A13's earlier counts are independently reproduced:
514 Materials (163+351), internal shader pointers 358/358 (14+344).

### Material texture environments (m_TexEnvs): no broken external texture links

| Owner | Target owner | Pointers |
|---|---|---:|
| resources.assets | internal (fileID 0) | 700 |
| resources.assets | `sharedassets0.assets` texture objects | 159 |
| sharedassets0.assets | internal (fileID 0) | 2123 |

External texture existence validation: **159/159 exist in
`sharedassets0.assets`; 0 missing.** No texture pointer was out of range.

## Engineering significance for color/pale-surface symptoms (bounded)

- Proven: the original two-owner data has **zero broken Material → Shader and
  zero broken Material → Texture references**, internal or external. The
  historic per-client hypothesis "unresolved external pointers cause pale
  surfaces" is **rejected by direct evidence**, not deferred.
- Proven (corroborating W3, whose names apply): 142 materials in
  `resources.assets` reference 9 distinct original custom Shader objects in
  `sharedassets0.assets`, and 2 more reference `globalgamemanagers.assets`
  shaders — giving W1 a material↔shader linkage base for his reconstructed
  programs without re-analysis.
- Proven (new, beyond W3's scope): **all 159 external Material→Texture
  references resolve inside `sharedassets0.assets`** and every external target
  pathID across both channels exists in its physical owner file
  (315/315, 0 missing).
- W1 targeting note: his first targeted Unity Android Vulkan single-shader
  assetbundle run [41663393724](https://github.com/alwansan/raf/actions/runs/41663393724)
  COMPLETED SUCCESS (receipt only; not device acceptance and not a full APK).
- Not proven / out of scope: whether the referenced shader *programs* are
  correct on device (W1's reconstruction lane), sRGB/color-space and quality
  settings, render states, FFT kernels, or any on-phone acceptance. This
  classification removes one candidate cause; it does not restore rendering.

## Reproduction

`scripts/probe_w2_external_material_shader_refs.py` (aggregate-only JSON with
schema-locked keys; refuses non-aggregate output fields), 19 synthetic
fail-closed tests in `tests/test_w2_external_material_shader_refs.py`
(including negative controls: wrong-size/missing pinned owner, out-of-range
and negative fileIDs, duplicate-external detection at the parse level, and
non-aggregate-key rejection), and
`.github/workflows/raft-w2-external-material-refs.yml` (unique W2 concurrency
group, `cancel-in-progress: false`, two-owner LFS hydration with full SHA
verification, aggregate-only artifact).

## Boundaries

- Aggregate-only publication: no object names, path IDs, shader/source bytes or
  textures are published; dependency table names are packaging metadata.
- Original payloads were read-only; no `.meta`/GUID/original source modification.
- The zero-based convention is recorded strictly as a negative control.
- No Unity/APK/OBB/XAPK/Release, native request, scheduled task, CL write or
  protected-branch mutation. WATER-001 / RENDER-002 / FFT-FORMAT-009 remain
  OPEN; game NOT_READY; immutable-candidate reviews 0/3.
