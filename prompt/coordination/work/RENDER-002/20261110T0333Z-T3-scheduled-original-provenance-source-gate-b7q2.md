# T3 — source provenance gate (2026-11-10 03:33 UTC)

session_id: 20261110T0333Z-T3-scheduled-original-provenance-source-gate-b7q2
origin: scheduled
baseline_head: 0ae946c2f2a30f4a351dc8c9b0917b9ebad77d5e
issue: RENDER-002 OPEN / NOT_READY 0/3
scope: this work note and a separate T3 session note only; no shared shader, Unity, APK, or other agents' files.
experiment_key: T3-SMOKE34-ORIGINAL-DXBC-SPIRV-DEFUSE-20261110
shared_resource: none acquired; original ZIP2 private workflow NOT launched.

## Evidence and decision
Owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md confirms world/save/reentry on 42058825739; white raft/hand, square smoke and lighting are not device-fixed. In prior original source workflow 42692895633, 22 PS read components and 28 SPIR-V declared components are different domains. T3 synthetic validator CI 42728727179 SUCCESS (14 tests) proves only structural injection; current validator intentionally returns STRUCTURAL_INJECTION_ONLY. Live Actions first page checked at 03:33 UTC: 42747722414, 42745684716, 42745684704 all completed success; no queued work shown in that page. New CL/test owner sessions exist through 20261109, but no new verified smoke pixel correction in the examined evidence. Current T3 last scheduled session 20261110T0230Z-T3-scheduled-original-map-handoff-n4q7.

## Narrow original-source experiment contract
1. Authenticate ZIP2 provider commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385 and original shader instance by source hash before processing; keep all binary/source payload private.
2. For each of the two authentic smoke34 PS keyword variants, enumerate actual DXBC input register read masks (not declaration masks), per-instruction swizzle and dataflow use; separately enumerate SPIR-V input loads, access chains, component extraction, decorations and output influence.
3. Obtain a provenance link from compiler intermediate representation or instrumented conversion itself; no equality of numeric register and location is accepted as provenance. Reject ambiguous many-to-one links, optimization-erased links, or unresolved permutations as INCONCLUSIVE.
4. Publish only counts, SHA256 digests of private inputs, verdict and redacted mismatch categories. Do not publish semantic identifiers, raw shader bytes or proprietary shader text.
5. Compare original particle material shader, texture alpha, renderer mode, render queue, ZTest, ZWrite, ColorMask, Blend RGB/Alpha and keywords to actual exported ShaderLab. If any source is unavailable, mark that dimension UNKNOWN rather than inventing a correction.
6. Only after a genuine source/export mismatch is identified, propose a scoped fix and device smoke pixel acceptance. Never infer white raft or smoke resolution from synthetic CI.

## Why no duplicate CI this cycle
No original-source instruction-provenance extractor was present in the inspected T3 gate; synthetic tests already succeeded, so repeating them or another Unity build would add no evidence. Next executor must first inspect current HEAD, latest T3 chat, and private workflow scope, then implement source-derived tracing before spending a private-source runner.
