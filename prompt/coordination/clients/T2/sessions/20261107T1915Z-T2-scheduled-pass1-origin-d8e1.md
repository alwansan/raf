# T2 — Pass 1 unknown producer: evidence boundary review

- session_id: 20261107T1915Z-T2-scheduled-pass1-origin-d8e1
- origin: scheduled
- base_sha: f00b91129325c1683e029637ffdf55e94fc95308
- resumed_from_sessions: 20261107T1822Z-T2-scheduled-aggregate-matrix-a9f2; 20261107T2227Z-T2-chat-blit-texture-role-6c52
- issue_id: WATER-001; status: completed (review scope only; WATER-001 remains OPEN)
- scope: prompt/coordination/work/WATER-001/20261107T1915Z-T2-scheduled-pass1-origin-d8e1.json and this session; no overlapping C# parser, Python validator, game ShaderLab, T3 or native workflow writes.

## Owner-device priority and authenticity

Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner's artifact from run 42058825739 reached, saved, exited and re-entered world; publication failed, not world entry. Logs report 23,884 water pass errors / 3,850 FFT kernel errors (220911-559) and 39,132 / 6,026 (230108-327). These counts belong to their device sessions, not GPU timing. No new device observation in this cycle.

## Reconciliation and result

Checked live branch HEAD f00b91129325c1683e029637ffdf55e94fc95308, active Actions query (0 in_progress), T2 sessions, source C# Mono.Cecil report, Python report validator and aggregate checker. Existing original authenticated run [42308583977](https://github.com/alwansan/raf/actions/runs/42308583977) succeeded on 4e5f4d24 with 65/65 report tests and original source SHA reauthentication. Its same-site correlation is stronger than earlier global-only role counts: **pass0 source=RenderTexture, destination=RenderTexture; pass1 source=unknown, destination=unknown**. These are static IL producer categories, not actual runtime allocation or texture content. Existing aggregate matrix test commit 3fe16a90 and source guard are already present; avoid repeating.

The C# reporter defines separate pass0/pass1 source/destination categories and the Python validator enforces per-pass partition and global conservation; the independent aggregate checker also partitions the two literal pass sites. A new generic aggregate test cannot resolve pass1's computed producer; that requires inspecting the exact original method's bounded IL expression / producer chain. The only evidence-backed next experiment is **bounded pass1 source/destination provenance classification** (local/field/call/branch/cast/stack-shape) in private SHA-pinned CI, emitting only coarse categories and unknown when not provable. Do not guess RenderTexture identity, CB0 alias, sampler binding, or publish raw IL. Coordinate with chat T2 before touching Program.cs.

## Execution limits

No game shader, CI dispatch, release, original asset export or shared file changed. Local git clone blocked by DNS (github.com unresolved); GitHub connector read worked. This review did not run repository tests or prove ShaderLab, Unity, or Android pixels. No new code fix justified by this result; preserve T3 fire/smoke scope and T4 physical mouse/T5 Resolution ownership.

## Next step

In a separate scoped implementation, add fail-closed pass1 computed-producer IL classification with synthetic branch/stack negatives; run the existing pinned Mono.Cecil workflow once on changed source, inspect sanitized aggregate and prove any new role before integration. Coordinate with T1/T3 and avoid duplicating running native builds.
