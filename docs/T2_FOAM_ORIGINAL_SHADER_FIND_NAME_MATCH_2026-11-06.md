# T2 — Original Foam Shader.Find requested name versus original serialized Foam Shader name

**Session:** `20261106T1340Z-T2-chat-shader-stfld-source-a84d` (`origin=chat`); issue **WATER-001 OPEN / NOT_READY**.

## Proven original chain preceding this comparison

All source material is authenticated privately in CI: immutable original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, original Foam owner `Raft_Data/sharedassets0.assets` 115,978,112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, and original `Assembly-CSharp.dll` 3,211,776 bytes SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`.

Previous T2 genuine [CI42225913516](https://github.com/alwansan/raf/actions/runs/42225913516) showed that the Shader field supplying the constructor for the actual Material receiver is a nonpublic Unity `[SerializeField]` and has one original compiled `stfld` writer. The independent [CI42228032544](https://github.com/alwansan/raf/actions/runs/42228032544) **SUCCESS** established the **exact value popped into that `stfld`** is the result of `UnityEngine.Shader.Find(string)`, with 3 prior same-basic-block IL instructions and C# synthetic false-positive guards. Earlier source-original CB0 name `Material.SetVector(string,Vector4)` proof covers **one** of five serialized CB0 vector member names, not the whole buffer or runtime water.

## Exact source shader name check

Registered independent scope `prompt/coordination/work/WATER-001/T2-20261106T1340Z-T2-chat-shader-stfld-source-a84d-find-name-match.json` **before code changes**, and extended only T2 code: `scripts/t2_foam_private_cb0_managed_targets.py`, `tests/test_t2_foam_private_cb0_managed_targets.py`, `android-port/Experiments/T2/FoamCb0ManagedLiterals/MaterialStoreValueTrace.cs`, `Program.cs` and the isolated `.github/workflows/raft-t2-foam-cb0-managed-literals.yml`. No original game source or Unity-generated files changed.

- Derive a SHA256 digest of the **authentic original serialized Foam Shader object's** `m_Name` from the same SHA-pinned source tree. Keep this digest strictly in **RUNNER_TEMP**, never stdout or artifacts; do not publish the raw name. Verify expected original shader stage and name model as previously pinned.
- Statically inspect the original `Shader.Find` `MethodReference` exactly **feeding the original `stfld`**. The bounded Cecil IL stack model retains the actual first `System.String` formal through literal/typed string local, rejecting unrelated nearby `Shader.Find` calls and mismatched local type. Private literal string remains in process memory and is never emitted.
- In the same private runner, SHA256 the *actual Shader.Find first argument* and compare with the original serialized Foam `m_Name` digest. Only counts `same`, `different` or `unknown` leave private scratch; no original names, digests, method/field identifiers, ShaderLab source, bytecode or original DLL were published. Synthetic positive/negative Cecil tests and **12** sourcefree Python original source name tests include a private digest no-plaintext check.
- Do not equate even a matching requested **name** with successful runtime Shader.Find resolution or Shader asset identity. A mismatch is strong evidence **against a direct exact-name request for this original Foam Shader**, but could still involve aliases, fallback shaders, or a distinct shader sharing a property name; the runtime association remains an independent unresolved question.

## Genuine source-backed result

**Definitive [CI42229056366](https://github.com/alwansan/raf/actions/runs/42229056366)**, job `127929919326`, source commit `50c7616ff5099f82d23279f7a0ec8c5ba5e598ba`: **SUCCESS**. All **12** sourcefree Python tests and extended Cecil direct-first-string / false-positive controls passed. Original owner/managed SHA authentic, 4 original CB0 stage links, 19,512 managed method definitions, 491,490 IL instructions, 7,246 `ldstr` instructions examined. [Intermediate CI42228964040](https://github.com/alwansan/raf/actions/runs/42228964040) also succeeded with the same original comparison result.

| Source-authentic check | Exact outcome |
|---|---:|
| Compiled `Shader.Find(string)` returns into the exact original Shader field `stfld` | 1 |
| Actual first string formal captured (not an unrelated literal) | 1 |
| First string equals original Foam Shader serialized `m_Name` | **0** |
| First string differs from original Foam `m_Name` | **1** |
| Unresolved first-string provenance | **0** |
| Runtime Shader.Find asset identity equals original Foam Shader | **NOT PROVEN** |
| Original 160B CB0 upload and Android Adreno water pixels | **NOT PROVEN** |

**Critical interpretation:** The source-original Shader.Find *requested name* is **different from** the source-original Foam Shader's serialized `m_Name`. The previous shared-property-name `Material.SetVector` caller is a **compiled property-name overlap**, **not** proof that this Material loads or updates the original Foam Shader. Future T2/T5 work must **not** promote this caller into a Foam-specific upload or READY assertion. Preserve its useful original code/dataflow evidence as a *distinct runtime material path*. This finding does not prove the two shader assets cannot alias at runtime or that the requested shader asset exists in the build; it disproves only this direct exact-name equality.

## Next falsifiable source question

In SHA-pinned original Unity asset data (starting with the same `sharedassets0.assets` owner, expanding to other authenticated asset owners only when needed), privately compare the actual requested Shader.Find name against other original serialized Shader objects. Report only count and source category without publishing private shader names or bytes. Alternatively trace actual Foam Material asset references and Shader PathID/GUID in original scenes/prefabs; that is a stronger path to correct original **Foam-specific** buffer upload than following unrelated shared property names.

**WATER-001 OPEN**. No Unity ShaderLab, `.meta`, GUID, game assets, scenes, saved worlds, Settings, sound, controls, APK, OBB or device GPU test altered by T2 in this experiment.
