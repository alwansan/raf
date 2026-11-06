# T1 — original FFT butterfly-1 Y last-writer CFG path evidence

- session_id: 20261106T122023Z-T1-chat-y-guard-paths-d71e
- origin: chat
- status: completed
- issue_id: WATER-001 (OPEN / NOT_READY)
- base_sha: 4bfe352226792fcf5e8356fe621a4376a6d343f3
- resumed_from_sessions: 20261106T113707Z-T1-chat-bitcarrier-producer-c8f1; 20261106T113001Z-T1-chat-lane-alias-f73c; 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2
- work_path: prompt/coordination/work/WATER-001/T1-20261106T122023Z-T1-chat-y-guard-paths-d71e.json
- experiment_path: prompt/coordination/experiments/T1/20261106T122023Z-T1-chat-y-guard-paths-d71e.json
- canonical_event: prompt/coordination/B_TEAM/events/T1/20261106T122023Z-T1-chat-y-guard-paths-d71e.json
- scope_commit: ca3046a9d9b87cad8ed830c8dca6195bddfd8064
- tool_commit: 0548a7e3ca93b56af28def87a94bf375a3dffb37
- fixture_commit: 06810b3de1ad37c13bc32ffc9a2e75c058f418d2
- pointer escape hardening: 1970eb99d1f7826cfcefb12cad548655b9d24f92
- pointer escape test: 5824cba6b5dd8f3a9b97940a10198fcc0d4aafb8
- fixed empty-category rendering: d00f2de69e9d3d143e6191fc81badf82e5186d18
- verified exact-source workflow SHA: c04278edeb3429738259ca7ef28300bfae00d91b

## Hypothesis and distinct action

The original Butterfly1 coordinate Y had two may-reaching scalar writer categories under previous merged reaching-store sets: signed-32-bit bits interpreted as float and float constant. The new bounded CFG path-state model tracks the *last* writer on potential structural paths from Function entry to the original private OpLoad. Separately it records whether both writer kinds may appear on a single CFG path, encountered predicate-producing opcodes (never literal values/IDs), unsupported aliases, pointer escapes and backward CFG edges. Only T1 isolated Vulkan workflow was changed; no shader/game assets, heavy Unity, Android builds, T2–T5 files or working audio/Settings/touch were changed.

## Reproducible testing / result

- First [CI run 42217597416](https://github.com/alwansan/raf/actions/runs/42217597416) failed in source-free tests before original extraction; 14/15 synthetic tests passed, one expected a category with empty predicate list but code omitted the empty key. Fixed output to represent unguarded writer keys explicitly.
- Corrected original [CI run 42217830589](https://github.com/alwansan/raf/actions/runs/42217830589) job 127892163524: **SUCCESS**, all 15/15 new adversarial tests PASS, SHA-verified ZIP2 original recovery/FFT private SPIR-V diagnostic/Vulkan roundtrip/cleanup PASS.
- Original source input SHA-pinned `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original bytes/bytecode, vector constant values, IDs and raw capture never published.
- At original slot0 Butterfly1 Y: `static_writer_categories={"whole_vector":3,"sint32_bits_to_float32":1,"float32_constant":1}`. However bounded path witness `final_writer_categories_possible=["float32_constant"]`; one abstract state at load. `may_visit_bitcarrier_and_float_constant_on_same_cfg_path=false`. The only encountered predicate producer family on the returned path is `OpINotEqual`. No backward edge, uninitialized final path, unknown final write, or pointer escape observed by this bounded model.
- **Interpretation:** in the enumerated structurally possible paths in the exact source fixture, the immediate last write to the physical vector lane read by Butterfly1 Y is the float constant; the earlier bitcast writer is an overly broad candidate from merged block dataflow. This does not establish the executed GPU branch, actual integer coordinate value, signed-bit carrier semantics for other sites, HLSL lowering correctness or Vulkan↔Unity numeric parity.
- The result is a *static control-flow path discriminator*, NOT device acceptance, actual playable water, a verified authored Unity FindKernel identity or a correct shader replacement. WATER-001 remains OPEN / NOT_READY.

## Safe handoff

Proceed with distinct source-private analysis of `OpINotEqual` branch predicate operand types/producer chain and branch successor destinations, then a paired SHA-pinned same-input Vulkan versus Unity coordinate/pixel trace to confirm whether Y addressing actually diverges. In parallel original Butterfly1 X still has prior severe numerical/coordinate discrepancy (252/256 in earlier trace); prioritize a source-backed fix to that path before speculative Y rewrite. Keep results under a new T1 session and do not rerun equivalent same-Vulkan experiment without a changed question.
