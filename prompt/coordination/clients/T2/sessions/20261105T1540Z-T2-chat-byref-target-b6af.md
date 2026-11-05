# T2 chat — original Foam ref RenderTexture[] callee signature/body provenance

- session_id: `20261105T1540Z-T2-chat-byref-target-b6af`, origin: `chat`, owner `T2`, issue `WATER-001`, status `active`.
- baseline: work was reserved first at `f0b84e96258c0aac23482034324324bf2497805b`; no original source assets or game edits.
- resumed_from_sessions: `20261105T1509Z-T2-chat-original-byref-sink-a83c` (original SHA CI42053062181 proved one typed byref call), `20261105T1520Z-T2-scheduled-e7c1` (separate ledger validation).
- experiment_key: `T2|ZIP2-15964ea8|AssemblyCSharp-0a6f0527|Foam-exact-array-byref-call-target|definition-and-signature-v1`.
- target: distinguish actual source original byref recipient as standard external library API versus same SHA-managed Assembly-CSharp.dll method; if a body is available, report bounded opcode aggregates without claiming execution or writes to ref argument.
- planned files: own `FoamFieldAddressConsumer.cs`, new `FoamByrefTargetBody.cs`, own `Program.cs`, own `raft-t2-foam-managed-literals.yml`, work/experiment/event/session files.
- coordination: no overlapping T2 managed workflow at reservation; active T1 FFT CI42057399746 not touched. T5 prior native package run42052375742 finished FAILURE, not silently assumed built. No ShaderLab, .meta, scenes, sound/Settings or postponed touch work.
- next: implement exact MethodReference capture with conservative original signature match and synthetic internal/external controls; genuine SHA-original CI. Keep WATER-001 OPEN, NOT_READY0/3.

## Source implementation and CI checkpoint

- Source commit [8080364261e1590e8c6db1eb025d756c08506980](https://github.com/alwansan/raf/commit/8080364261e1590e8c6db1eb025d756c08506980), HEAD-lease fast-forward after T1/T4 concurrent pushes; no force. Own files: `FoamFieldAddressConsumer.cs` precise target callback, new `FoamByrefTargetBody.cs`, own `Program.cs`, own `raft-t2-foam-managed-literals.yml`.
- Synthetic controls: real matching byref callee body containing a literal `ldarg; ldnull; stind.ref` and same-name differently typed callee rejected; original method names/IL and private small-domain indices withheld.
- Original SHA-pinned CI [42058352098](https://github.com/alwansan/raf/actions/runs/42058352098) **queued at checkpoint**. It discriminates known framework `System.Array.Resize` signature, matching SHA-original internal definition, and missing/external body; actual ref mutation/runtime execution remains unproven unless strictly verified.
- T1 FFT, T4 RGD and T5 native scopes not edited or cancelled. Previous T5 native package CI42052375742 finished FAILURE, not a finished APK delivery. WATER-001 OPEN, NOT_READY 0/3.

## Verified original typed byref recipient definition and compiled body — SUCCESS

- Exact SHA-authentic original [CI42058352098](https://github.com/alwansan/raf/actions/runs/42058352098) **COMPLETED SUCCESS**, source commit [80803642](https://github.com/alwansan/raf/commit/8080364261e1590e8c6db1eb025d756c08506980), managed original `Assembly-CSharp.dll` SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e` (3,211,776 bytes). Tests of exact synthetic internal byref target, same-name wrong typed signature and source-free safety controls all passed.
- Real recipient MethodReference resolves to **exactly one actual original method definition with compiled body** in this SHA-authenticated managed DLL. It is not merely an unresolved or framework API reference: `OriginalTargetDefinitionCategory=same_sha_managed_definition`, `framework_resize_signature=false`.
- Original recipient body aggregates: **1 `newarr UnityEngine.RenderTexture`**, **1 `stind.ref`**, **1 `stelem.ref`**, **2 branch opcodes**, **0 strict consecutive `ldarg ref; ldnull; stind.ref`**. These are **method-wide opcode counts**, not proof that the `newarr` result is the value assigned to the exact byref parameter, nor proof that any branch executes. This is now a concrete candidate for source-authentic indirect array allocation, with unresolved dataflow and runtime.
- CI safe output `T2_FOAM_BYREF_TARGET_SAFE` read directly from actual runner job `127352811551`; safe artifact `13429204614`, SHA256 `dfe1a24dd1b77c56886f8f393443b0e2c1c00e6116ba22a4885ce5ab4365888a`, 2285 bytes. Original private method/field names, IL and small integer values withheld.
- status: `completed` for source recipient method resolution and opcode census. **Next:** strict intraprocedural branch-aware def-use from actual `newarr RenderTexture` into actual `stind.ref` destination `ref RenderTexture[]`, and detect `stelem.ref` array origin; remain fail closed. No native/Unity/device or shader-asset acceptance. WATER-001 OPEN / NOT_READY 0/3.

## Second experiment within the same chat cycle: ref-array allocation def-use

- Reserved separate work `prompt/coordination/work/WATER-001/T2-20261105T1540Z-T2-chat-byref-target-b6af-array-ref-store-dataflow.json` before edits, commit `9bdcdf7929ec129a1fa5874b513581afedefd441`. Original byref target definition/body previous scope closed successfully.
- Implemented source-free `FoamByrefAllocationFlow.cs`, integrated with T2 `Program.cs` and original SHA-pinned workflow on [commit 81589064](https://github.com/alwansan/raf/commit/81589064359a025cbe268ba74b3c8502f5678517). Uses branch-target-delimited basic blocks, exact typed `ref RenderTexture[]` source/formal tags, actual `newarr`, `stind.ref` and `stelem.ref` stack provenance. Fail-closed when unknown opcode or a value crosses a branch. Source-free tests: positive ref-store, wrong array element type, and cross-branch proof must be rejected.
- [Original CI42059508444](https://github.com/alwansan/raf/actions/runs/42059508444) `in_progress` at checkpoint. Do not assert original newarr-to-byref flow until it passes and safe aggregate is inspected. T1 FFT and T5 native CI active independently; neither changed or cancelled by T2.
