# T2 chat — SHA-original Foam return-value flow (stack+locals across CFG joins)

session_id: 20261109T0212Z-T2-chat-return-value-flow-n7x3
origin: chat
branch: feature/android-native-port
base_sha: 23f8610e5cda70b4f41cced0d8e1babfb8d50524
resumed_from:
  - clients/T2/sessions/20261109T0155Z-T2-chat-original-cfg-topology-a8f5.md
  - clients/T2/sessions/20261109T0141Z-T2-chat-cl-fourcase-ci-r6p2.md
issue_id: WATER-001 OPEN
experiment_key: T2-FOAM-SHA15964-CFG-RETURN-VALUE-ABSTRACT-20261109
work: work/experiments/20261109T0212Z-T2-chat-return-value-flow-n7x3.md
origin_verified_prior: CI42548419872 original ZIP2/DLL authentic, pass1 cfg_mixed_syntactic_return_predecessors; this was only syntax and NOT return-stack provenance. Earlier owner mini GLES T2 4/4 synthetic PASS, separate from Raft original water.

## Scoped change

- Registered intended file scope before source edit at commit f97c9462194dd22c5c09e0f5342cff0a79a0c830.
- Added `ReachableReturnValueFlow` to **T2-owned** original Cecil scanner `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs`, source commit `4c8af56a580264df92a98375a7fd30ae87a10a21`.
- The new forward CIL abstract interpreter reads stack and local-value **categories** along reachable control flow (direct branch, condition, switch and valid fallthrough); joins disjoint categories as `mixed`, rejects exception handlers, unresolved targets/underflow/mismatched stack heights, unsupported opcodes and budget overrun. Real field tokens and object identity are **not** retained in emitted records; source type cannot become object reference proof. Calls remain `nested_call_untraced`; `callvirt` virtual-dispatch checks retained.
- Independent synthetic Cecil fixtures cover same-category return via local across two branches, genuinely different return categories, stack phi into shared return, malformed targets, exception handlers and nested-call unknown provenance.
- Original-safe JSON shape unchanged; only fixed public stdout categories, no raw original CIL/private names/assets.
- NO changes to other workers' drivers/pack/game assets/source or native build requests; no APK produced, T2 Mini NO_BUILD unchanged.
- Existing T3 event missing an explicit record ID remains pre-existing separate canonical summary blocker; T3 already informed, no cross-owner edits.

## CI waiting checkpoint

- [Run 42549568993](https://github.com/alwansan/raf/actions/runs/42549568993), T2 original Foam source private SHA-authenticated workflow at commit `4c8af56a580264df92a98375a7fd30ae87a10a21`.
- Job `128941879761`: Python source-free gate, Mono.Cecil compile/selftest, immutable ZIP2 and original managed/shader owner staging **SUCCESS** at checkpoint; source-original scan/purge/upload still in progress. Reopen run and retrieve redacted `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW` category; if failed, triage first stage and fix T2 source only; never bypass SHA/privacy gates.
- No other in-progress/queued Actions at scope registration; other T workers' subsequent runs do not overlap this path.

next_step: Examine actual original-value category. If mixed/unknown, identify smallest unsupported CIL flow or return-producer class without leaking original IL; if category-only field/null, do NOT infer exact instance alias. Then examine crosspass pass0 destination ↔ pass1 source instance lineage, CB0/sampler/ShaderLab and real Unity/Adreno water pixels; WATER-001 remains OPEN.

## Authenticated final result and handoff

- [CI42549568993](https://github.com/alwansan/raf/actions/runs/42549568993) **SUCCESS** at source commit `4c8af56a580264df92a98375a7fd30ae87a10a21`, job `128941879761`. 17/17 Python PASS, Mono.Cecil synthetic PASS, original exact ZIP2/DLL/Shader-owner SHA pass, original scan and private cleanup pass.
- New original safe output: `T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_or_joined` (prior syntax-only `cfg_mixed_syntactic_return_predecessors` unchanged). Pass0 source remains `RenderTexture typed_field`, pass1 source declared `Texture typed_call_result`; **no source pass0 ↔ pass1 object instance equality proven**.
- Scope `work/experiments/20261109T0212Z-T2-chat-return-value-flow-n7x3.md` completed **only** the new original-source return-value category audit. Report `docs/T2_FOAM_ORIGINAL_RETURN_VALUE_FLOW_2026-11-09.md` committed at `c06464a2027d519eaf5a684c1d771b6ef0ef65aa`.
- Continue by testing original pass1 receiver and per-path texture origin including field-token lineage/constructors in **private SHA-pinned scratch**, never publishing actual names or private IL. Unknown/virtual/exception path must fail closed. Next validate same RenderTexture *instance* across pass0 destination and pass1 source and binding to Foam material/CB0/samplers, then real Unity/Adreno water pixels.
- **Boundaries:** old owner Mini T2-01..04 synthetic phone GLES4/4 PASS distinct from original water. No APK/XAPK requested, no audio/Settings/input changes, no shared Mini or T3 ledger edits. T2 NO_BUILD; WATER-001 OPEN and game NOT_READY.

## Ledger refresh status — inherited issue, no override

Own validated event `prompt/coordination/B_TEAM/events/T2/20261109T0212Z-T2-chat-original-foam-return-values.json` was saved in commit `58462edef9b19dca51420fe2559e10d27b1c4b7b`. Auto-triggered canonical summary [CI42549865743](https://github.com/alwansan/raf/actions/runs/42549865743) **FAILED** in `scripts/refresh_b_team.py::read_records` because the existing **T3** event `prompt/coordination/B_TEAM/events/T3/20261106T2007Z-T3-chat-explicit-original-d52e.json` has neither `id` nor `event_id`. This same inherited data problem was already reported to T3 in `prompt/coordination/T_TEAM/T2_TO_T3_20261109T0147Z-summary-identity-blocker.md`. T2 neither edited that cross-owner event nor bypassed/suppressed ledger validation. Re-run deterministic summary after owning T3 repairs event identity. This failed summary is **not** the successful source-only original CIL run, which remains CI42549568993 SUCCESS.
