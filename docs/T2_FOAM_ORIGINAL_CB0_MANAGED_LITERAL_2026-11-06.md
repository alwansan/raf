# T2 — SHA-original Foam CB0 source names × original managed IL setter candidate audit

**Session:** `20261106T110527Z-T2-chat-cb0-managed-namelinks-f2e1` — origin `chat`, issue `WATER-001` (OPEN), readiness **NOT_READY**.

## Authenticated inputs and method

- Original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; Foam owner `Raft_Data/sharedassets0.assets` 115,978,112 bytes, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; raw Foam Shader PathID2420 SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Original managed `Assembly-CSharp.dll` exact 3,211,776 bytes, SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`, Git blob `fc9d4ba920a178fdb89c970d9d772a01051dadc6`, matches immutable ZIP2 and current branch. SHA and bytes verified inside Actions.
- Earlier genuine [CB0 compiled load-index CI42204938466](https://github.com/alwansan/raf/actions/runs/42204938466): Pass0 Fragment is larger; six compiled constant-index `OpLoad` paths fall outside Vertex's reflected array length. Pass1 Vertex is larger; two compiled paths fall outside Fragment's length. This does not establish actual host buffer contents.
- Previously the [source→managed *texture* literal work CI42019735778](https://github.com/alwansan/raf/actions/runs/42019735778) and descendants established four non-authored Foam Texture names in compiled setters and original `RenderTexture[]` source. This new experiment covers **CB0 serialized buffer and vector/matrix member names** instead, so is independent of that finished texture scope.
- New `scripts/t2_foam_private_cb0_managed_targets.py` authenticates the full original Shader and B25 name registry, scans both passes, both VS/FS stage-specific CB0 source members (4 stage entries), and hashes original private names **only in `RUNNER_TEMP`**. A name index absent from the original registry remains explicitly unresolved rather than invented. New isolated `android-port/Experiments/T2/FoamCb0ManagedLiterals` uses Mono.Cecil 0.11.5 to statically inspect exact original DLL method `ldstr` instructions, public Unity typed uniform setter call metadata and method proximity, with strict SHA pins.
- [Real CI42208958212](https://github.com/alwansan/raf/actions/runs/42208958212), job `127862550030`, source commit `eb1db19f3cdd38b43f61fdf842899c1ad10d6f9b` **SUCCESS**. 11/11 Python original-name source-free negative tests and Cecil selftest passed; exact UnityPy source identity and original managed SHA passed. Private temporary name hashes, original asset and DLL checkout erased; only numeric safe JSON uploaded. No source code/game bytes copied to public logs.

## Original compiled managed facts

| Safe source-authentic aggregate | Result |
|---|---:|
| Original Foam CB0 stage links examined | 4 |
| Unresolved source member `m_NameIndex` | **0** |
| Distinct source buffer name targets | 1 |
| Distinct source vector member names | 5 |
| Distinct source matrix member names | 0 |
| Distinct buffer names found in original managed `ldstr` | **0/1** |
| Distinct vector names found as original managed `ldstr` | **3/5** |
| Original `ldstr` matches to vector names | 4 occurrences in 4 methods |
| Methods containing both matched vector name and a typed uniform setter | **1** |
| Matched vector-name literal with a following typed setter within 16 IL instructions | **1** |
| Following setter families (can co-occur near same literal) | `Material.SetFloat`: 1; `Material.SetVector`: 1 |
| Matched source name `ldstr` directly followed by `Shader.PropertyToID` within 4 IL instructions | **0** |
| Actual original methods examined | **19,512** |
| Original IL instructions examined | **491,490** |
| Original `ldstr` instructions | **7,246** |
| Recognized typed Unity numeric/uniform setters (all original code) | **489** |

**What this separates:** Four source-authentic CB0 stage entries give one buffer name and five distinct vector member names. Three of those five names occur as original managed IL literals; the one observed same-method/nearby typed setter candidate supplies a concrete location class for investigating the original value producer. The one missing buffer name and two missing vector names are *negative literal observations in this specific original managed assembly*, not proof that Unity cannot populate them from global/built-in engines, native code, IDs, or other assemblies. No unpublished exact names, hashes, private member indices, original method labels, IL or byte sequences were emitted.

**Critical limits:** Same-method co-occurrence and `ldstr` proximity are **not** a first-formal string argument proof. It might be an unrelated setter; another method may use `Shader.PropertyToID` before a typed `System.Int32` overload. The compiler/runtime may fill CB0 via Unity engine bindings rather than a managed wrapper. This analysis cannot prove source-to-translated member offsets, actual uploaded buffer capacity, data values, timing, material receiver identity, shader import, Vulkan or Adreno water pixels. Do not invent CB alias or assume smaller reflected stage arrays are safe.

## Next falsifiable question

Perform an instruction-stack conservative `ldstr`→typed Unity setter **first-argument** check on the **same original SHA-pinned managed assembly** for the one exact source-matched nearby candidate; do not accept proximity without verified IL argument ownership. If no matching actual first formal is found, classify this result as a search hint only. In parallel, determine whether the two source vector members never present as literals can be supplied through engine globals or non-string IDs; that requires separate proof.

**WATER-001 stays OPEN; no Unity original CB0 upload/Adreno acceptance, no game `.shader`, `.meta`, GUID or native game build changed.**
