# T2 — source-original Foam Shader and Material references in `sharedassets0.assets`

Session `20261106T1520Z-T2-chat-foam-owner-shader-material-links-5e84`, origin `chat`. Issue **WATER-001 OPEN / NOT_READY**.

## Source and validity

- Source: immutable original `alwansan/raf:zip2` SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, restored through `scripts.w1_stage_zip2_owners.stage` without LFS.
- Exact owner: `Raft_Data/sharedassets0.assets`, **115,978,112** bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`.
- Original Foam `Shader` object PathID **2420**, raw SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Original managed `Assembly-CSharp.dll` **3,211,776** bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.
- All original assets checked by SHA inside a temporary GitHub runner, using pinned UnityPy 1.25.4. Original binaries and private Shader names were neither executed nor published.

## Motivation: the previous compiled managed path is not Foam identity proof

Previous authentic T2 [CI42229056366](https://github.com/alwansan/raf/actions/runs/42229056366) proved the *actual first string formal* of a `Shader.Find(string)` call supplying a managed `Material` which later receives one original Foam CB0 parameter name through `Material.SetVector` **differs** from the original serialized Foam Shader `m_Name`. Exact property-name overlap is not Material→Foam shader identity. This new experiment asks a different bounded question: within the exact original asset owner, does that requested name correspond to *another* Shader object, or do serialized Material objects directly reference the known original Foam Shader object by local pointer?

## Implementation and negative controls

- Registered distinct work under `prompt/coordination/work/WATER-001/T2-20261106T1520Z-T2-chat-foam-owner-shader-material-links-5e84.json` before editing any files; only T2-owned scripts/tests/Cecil source and isolated original-source workflow changed.
- `scripts/t2_foam_private_cb0_managed_targets.py` now reads only this 115MB original owner after independent `PINS`/SHA authentication. It enumerates UnityPy object readers classified as Shader or Material and privately hashes non-Foam Shader `m_ParsedForm.m_Name`. The exact original Shader.Find first formal from the source-authenticated managed Cecil trace is compared against these **temporary-only** hashes; neither names nor hashes appear in public code output, JSON safe result, logs or artifacts.
- For local Material references, the pointer must have **both** `m_FileID=0` and `m_PathID=2420`. A reference with nonzero fileID but identical PathID does **not** count. No method/symbol-name heuristics, no Shader fallback aliases, and no guessed Meta/GUID references.
- Bounds: at most 250,000 total objects, 8,192 Shader objects and 32,768 Material objects; malformed Unity typetrees count as `unparsed`, **never** as a negative result. A zero can only be interpreted for the enumerated owner, not for other game files.
- Synthetic Python tests cover private digest nonplaintext, duplicate/wrong original Foam object, wrong material fileID, malformed/null pointer, actual embedded NUL reject, and explicit original owner pin dependencies. All previous source CB0 name/PPtr checks and Cecil Shader.Find actual-first-formal false-positive rejection remain enabled.
- Initial isolated [CI42242151031](https://github.com/alwansan/raf/actions/runs/42242151031) and [CI42242210912](https://github.com/alwansan/raf/actions/runs/42242210912) failed only a **synthetic NUL fixture**, not original Shader source. After fixing it, isolated [CI42242293870](https://github.com/alwansan/raf/actions/runs/42242293870), [CI42242616195](https://github.com/alwansan/raf/actions/runs/42242616195), [CI42242833419](https://github.com/alwansan/raf/actions/runs/42242833419), [CI42243064980](https://github.com/alwansan/raf/actions/runs/42243064980) were blocked at original asset-owner catalog before asserting Shader/Material values. Safe stage diagnostic and fail-closed unreadable-object handling were added; the root code cause was absent imports of the original `OWNER`, `PINS` and `fingerprint` provider constants. Fixed using explicit pinned imports. No false original result was emitted during these failed runs.

## Final genuine source evidence

[GitHub Actions **42243327311**](https://github.com/alwansan/raf/actions/runs/42243327311), job `127978991083`, source commit `29b23e72522addc748560db7ca5b8f948d8aa7e1`: **SUCCESS**. **16/16 source-free Python tests**, typed Cecil source-free controls, genuine Foam owner object and original managed DLL SHA authentication, and genuine original object census completed. Earlier corrected [CI42243288433](https://github.com/alwansan/raf/actions/runs/42243288433) also SUCCESS with identical original owner result. There were 19,512 original managed method definitions and 491,490 IL instructions independently examined in the pinned `Assembly-CSharp.dll`.

| Exact question, only within pinned `sharedassets0.assets` | Verified |
|---|---:|
| Original Shader objects enumerated | **58** |
| Original Material objects enumerated | **351** |
| Shader names the pinned UnityPy reader could not parse | **0** |
| Material `m_Shader` pointer records reader could not parse | **0** |
| Original Material objects with local `m_FileID=0,m_PathID=2420` Foam Shader pointer | **0** |
| Material references to an external Shader (nonzero `m_FileID`) | **7** |
| Other Shader objects in this owner whose serialized name exactly matches the genuine Shader.Find request | **0** |
| Proof that all original game Shader or Material assets live in this one owner | **NO** |
| Proof of Unity runtime reference resolution, original 160B CB0 upload or Adreno water pixels | **NO** |

### Interpretation and next safe action

The original managed Shader.Find name requested by the one source-CB0-property-overlap Material path **matches neither the actual Foam Shader name nor any of the other original Shader names in this one owner**. The 351 original Materials stored in the same owner provide **no direct local Foam Shader PathID2420 link**. Seven Material Shader PPtrs are external to this owner, but their external targets have **not** been resolved; they are not evidence for or against Foam. None of these negative counts proves the original Foam Shader is absent from other scenes/prefabs/asset bundles or cannot be loaded dynamically.

For real Foam recovery, inspect **other SHA-pinned original asset owners** containing Shader/Material references and resolve external PPtr file IDs through their verified serialized external file tables. Prefer exact immutable Foam Shader PathID/GUID references over a shared property-name string. Do not rewrite game ShaderLab, Meta/GUID, or alias a Shader.Find name to Foam based on this evidence. Original two-pass pass0 Fragment / pass1 Vertex CB0 stage-access capacity mismatch still needs the *actual* host upload identity and size validated, then a real Unity/Adreno water device test.

**WATER-001 OPEN / NOT_READY.** No Unity native build, APK/OBB, original game shader/scene/prefab, audio, Settings, world/save or touch files modified by T2.
