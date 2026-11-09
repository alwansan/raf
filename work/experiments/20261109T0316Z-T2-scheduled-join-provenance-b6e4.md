# T2 original Foam join provenance — scoped experiment

session_id: 20261109T0316Z-T2-scheduled-join-provenance-b6e4
origin: scheduled
baseline_sha: 309f8675814787d8e169b1d2d90b6d1610c8ef10
issue: WATER-001 OPEN
experiment_key: T2-FOAM-PASS1-MIXED-RETURN-ALIAS-GATE-20261109
resource: original ZIP2 SHA 15964ea8 (private, no raw exports)
files_in_scope: work/experiments/20261109T0316Z-T2-scheduled-join-provenance-b6e4.md; clients/T2/sessions/20261109T0316Z-T2-scheduled-join-provenance-b6e4.md
shared_resources: none; no CI dispatch, APK, ShaderLab or T3 source edits.

## Verified starting evidence
- Owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md: world save/reopen succeeded on artifact; water pass/FFT faults remain. APK86 history superseded.
- Latest T2 chat source-original [CI42549568993](https://github.com/alwansan/raf/actions/runs/42549568993): pass1 callee returns `value_mixed_or_joined` across reachable CFG; does not prove actual Texture instance equality. Source scan passes; original names/IL private.
- [CI42547038822](https://github.com/alwansan/raf/actions/runs/42547038822) confirms 4 owner synthetic GLES case exports and 15 regression tests; NOT Raft water pixels.
- Current T3 canonical event 20261106T2007Z-T3-chat-explicit-original-d52e.json still lacks id/event_id; do not modify cross-owner record. T3 was previously notified.

## Hypothesis / next discriminating experiment
`value_mixed_or_joined` can arise from a null branch, distinct field origins, or opaque nested call. A conservative **private** per-return-path provenance trace (return operand + receiver chain) can distinguish these without exposing tokens/names. Require immutable ZIP2 + Assembly-CSharp SHA and fail closed for exception regions, unsupported opcodes, alias merges, virtual dispatch. Emit only fixed categories and test both branches using synthetic Mono.Cecil fixtures. Never treat a static Texture return type as instance equality. If any path is opaque or null, keep crosspass alias UNKNOWN; if unique field token category is proven, compare pass0 target's actual producer token in private scan before ShaderLab integration.

## Status
planning_only; no original trace or source edit performed in this scope. Next T2 session should implement source-owned analyzer with new independent synthetic fixture and run existing SHA-pinned workflow after checking live Actions. Avoid repeated source-free GLES or duplicate mini APK. WATER-001 OPEN.
