# T5 chat checkpoint
session_id: 20261105T1508Z-T5-chat-native-retry-c2b7
origin: chat
status: waiting_ci
base_sha: c491f76077edcf7984cb5de95101edc1aafb000d
resumed_from_sessions: 20261105T1453Z-T5-scheduled-6e82, 20261105T1431Z-T5-chat-native-cancel-d41e
issue_id: INTEGRATION-001
work: prompt/coordination/work/INTEGRATION-001/T5-20261105T1508Z-T5-chat-native-retry-c2b7-single-native-candidate-retry.json
resource_key: raft-native-engine-feature/android-native-port
intent: One authorized diagnostic build candidate from the current branch using the existing GitHub workflow. Previous run 42042902522 was cancelled before Editor build; source failure unproven. Preserve other clients' jobs and preserve strict checks.
preflight: branch nonterminal actions 0, source c491f76077edcf7984cb5de95101edc1aafb000d.
next_step: Check fresh Actions, dispatch one distinct request only if no overlap, save exact run status. No device success claim.


## Verified execution checkpoint — 2026-11-05 15:13 UTC

- **Native request commit:** [b0c4b4c05011d915cd845259f06b5f80ee368092](https://github.com/alwansan/raf/commit/b0c4b4c05011d915cd845259f06b5f80ee368092) with actual `[raft-native-build] [raft-device-test]` markers in commit message. Existing request file `.github/raft-native-build-request.json` updated once after preflight HEAD `5ed806ea1b8170988ea0f49140511021a8f239d3`. Original `documented_water_limitations` five entries preserved exactly. Owner-approved workflow and all strict gates untouched.
- **Actual immutable GitHub run:** [42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) from that exact SHA. **status in_progress** at checkpoint. `native-request-gate` **SUCCESS**, `unity-license-preflight` **SUCCESS**, `reconstruct` **IN_PROGRESS** (checkout stage in last verified snapshot). This proves workflow request and license prerequisites, not Editor import/IL2CPP or delivery.
- Previous immutable run [42042902522](https://github.com/alwansan/raf/actions/runs/42042902522) was CANCELLED without a source failure before Unity, and still has 0 signed game artifacts. This new build uses distinct updated source; no other queued/in_progress/pending branch Actions were present immediately before dispatch. No T1/T2/T3/T4 jobs cancelled or source files overwritten.
- Work `prompt/coordination/work/INTEGRATION-001/T5-20261105T1508Z-T5-chat-native-retry-c2b7-single-native-candidate-retry.json` is `waiting_ci`; experiment `prompt/coordination/experiments/T5/T5-20261105T1508Z-T5-chat-native-retry-c2b7-one-native-current-head.json` also `waiting_ci`; event `prompt/coordination/B_TEAM/events/T5/20261105T1513Z-one-native-current-source-request.json` recorded.
- **No native signed APK, OBB, XAPK, Release asset, phone visuals/offline play/save/reopen, Unity/Adreno GPU or readiness claim.** T4 original seed Save guard still a negative (wrong root for actual Save); T3 exact D3D11 stage pairs do not by themselves prove ShaderLab/Android. Project remains NOT_READY 0/3.

**Next:** check [run42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) first upon resumption, not branch HEAD alone. If terminal failure, inspect exact first failing job/step and job log category; if running, preserve work as waiting_ci. If all green, independently verify published exact APK+OBB+XAPK and SHA before any device claims. Do not dispatch duplicate expensive native runs. Preserve working audio and Settings and deferred touch/layout.


## Latest independent read-only progress checkpoint — 2026-11-05 15:15 UTC
- Native [run42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) still `in_progress`, `conclusion=null`. Confirmed `native-request-gate=success` and `unity-license-preflight=success`; current active `reconstruct` step `Restore every original graphics payload before exporting textures and shaders`, no job failure yet. This is **not** full Unity import or signed-package output.
- The immutable run's source SHA remains `b0c4b4c05011d915cd845259f06b5f80ee368092`; fresh shared branch HEAD at checkpoint `7e9d2461250924fb0bd40c1e661cf70b8bad89d7` is newer and **does not change the running candidate**. Source SHA matters for candidate acceptance.
- Shared `prompt/STATUS.md` updated on commit `7e9d2461250924fb0bd40c1e661cf70b8bad89d7` with run and limitations. No new artifact/release and no phone proof; task stays `waiting_ci`. Stop here rather than dispatching a second full import while this one runs.
