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
