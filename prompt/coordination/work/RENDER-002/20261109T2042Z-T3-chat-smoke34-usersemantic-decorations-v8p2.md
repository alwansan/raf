# T3 chat — SHA-original smoke34 explicit SPIR-V UserSemantic decoration availability

session_id: 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2
origin: chat
base_sha: 7410282dc45bb9d9b7e0afabf6303d697a19ccf5
resumed_from_sessions: 20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8; 20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7
issue_id: RENDER-002
status: completed
updated_at: 2026-11-09T20:51:00Z
experiment_key: t3-sha15964-smoke34-two-keyword-private-fragment-dxbc-to-original-and-roundtrip-spv-explicit-UserSemanticGOOGLE-availability-v1
resource_key: sha15964-smoke34-original-private-fragment-spv-UserSemantic-2paired-T3
intended_files:
  - scripts/t3_smoke34_spirv_usersemantic_annotations.py (NEW; no changes to scheduled gate)
  - scripts/t3_original_smoke34_usersemantic_probe.py (NEW; no changes to original previous smoke source modules)
  - tests/test_t3_smoke34_spirv_usersemantic_annotations.py (NEW)
  - tests/test_t3_original_smoke34_usersemantic_probe.py (NEW)
  - .github/workflows/raft-t3-original-smoke34-usersemantic.yml (NEW isolated)
  - docs/T3_SMOKE34_USERSEMANTIC_PROVENANCE_2026-11-09_AR.md (NEW)
  - prompt/coordination/clients/T3/sessions/20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2.md (NEW)
  - prompt/coordination/experiments/T3/20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2.json (NEW)
  - prompt/coordination/B_TEAM/events/T3/20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2.json (NEW)

At scope claim latest prior authenticated CI42692895633 success 22/28 PS DXBC UsedMask/declared lanes; SPIR-V original and roundtrip both 28 declared, zero generic compiler name preservation. Earlier source CI42691211652 7 VS/FS authentic DXBC semantic-index links. New latest scheduled session 20261109T2035Z introduced **source-free** scripts/t3_smoke34_location_provenance_gate.py requiring explicit per-lane mapping; this scope does NOT touch scheduled gate and does NOT attempt unproven mapping. Most recent Actions listed no T3 source jobs running, distinct T1 FFT/T2 Foam/T4 input/T5 mini. No main/force writes or other worker modifications.

Question genuinely new: vkd3d original SPIR-V and HLSL→glslang roundtrip may or may not contain true SPIR-V OpDecorateStringGOOGLE / HlslSemanticGOOGLE annotations attached to input variables. A robust bounded **binary opcode** scanner inspects this actual metadata, correlates only explicit decoration to authenticated DXBC ISGN semantic+index and safe reflected Location, and emits **counts only**. If annotation is absent, report NONE/INCONCLUSIVE and do not invent mapping based on OpName or numeric Location. Also report register-number==Location **structural overlap only**, with an explicit NO_PROVENANCE flag. Literal names/bytecode stay ephemeral private. Distinct CI workflow with SHA original 6 scenes+4 owners 2 exact private PS keyword variants; no Unity or native APK; no READY claim. Finish with session+work+experiment+event on actual verified CI result and release resource.
## Final genuine source result: completed / resource released
[CI42696526193](https://github.com/alwansan/raf/actions/runs/42696526193) SUCCESS at code head 0ab78d56f9d8bc50fb5e6adf5601a7b2e7a5df63. Synthetic tests 12 binary-opcode +8 genuine-bridge +9 scheduled failclosed gate +21 inherited DXBC +7 original shader inventory = **57 PASS**. Six SHA scenes/four SHA owners, two exact compiled source PS variants (original + HLSL roundtrip SPV) reverified privately.

**Result:** Both original and roundtrip genuine SPIR-V have 7 user input variables/28 declared lanes across exact two pairs. **0 HlslSemanticGOOGLE decorations, 0 SPV_GOOGLE_hlsl_functionality1 extensions** in either program set, so there is **no direct explicit semantic annotation** available. DXBC input register numeric number equals original SPIR-V input Location in **7/7** genuine user records, versus **5/7** after HLSL roundtrip; for all numeric matches scalar family and declared width also coincide. This is a **structural candidate only** and not authenticated Semantic→Location provenance, dataflow, per-lane value equivalence or graphics fix. No private code or names published.

Safe counts-only artifact [13710355183](https://github.com/alwansan/raf/actions/runs/42696526193/artifacts/13710355183) expires 2026-11-16T20:49:42Z. Earlier CI42696430679 failed only due repeated synthetic test temp directory; fixed fixture in commit 0ab78d. Other workers' XAPK (T5, CI42696228231) independent; do not cancel or alter. Scope now completed; original source resource released. RENDER-002 OPEN/NOT_READY 0/3.
