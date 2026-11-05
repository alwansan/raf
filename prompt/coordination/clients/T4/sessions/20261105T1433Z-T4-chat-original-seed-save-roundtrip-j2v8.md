# T4 chat — original RGD seed write/roundtrip probe

- session_id: 20261105T1433Z-T4-chat-original-seed-save-roundtrip-j2v8
- origin: chat
- status: completed
- baseline_sha: 7058aa34de519c498ce89e41d0ddd2c1c753e298
- resumed_from_sessions: 20261105T1405Z-T4-chat-original-rgd-runtime-k6n8, 20261105T1408Z-T4-chat-jsonl-evidence-n4r7, 20261105T1338Z-T4-scheduled-v6n9
- work_record: prompt/coordination/work/LOCAL-005/T4-20261105T1433Z-T4-chat-original-seed-save-roundtrip-j2v8-original-seed-save.json
- experiment_key: t4-authentic-seed-original-save-private-reflection-guarded-dotnet8-2941-sha-151sibling-v1
- resource_key: none
- intended_files: android-port/Experiments/T4/OriginalRgdSaveRoundtrip/OriginalRgdSaveRoundtrip.csproj, android-port/Experiments/T4/OriginalRgdSaveRoundtrip/Program.cs, scripts/t4_verify_original_rgd_save_roundtrip.py, tests/test_t4_verify_original_rgd_save_roundtrip.py, .github/workflows/raft-t4-original-rgd-save-roundtrip.yml, docs/T4_ORIGINAL_RGD_SAVE_ROUNDTRIP_2026-11-05.md, prompt/coordination/work/LOCAL-005/T4-20261105T1433Z-T4-chat-original-seed-save-roundtrip-j2v8-original-seed-save.json, prompt/coordination/clients/T4/sessions/20261105T1433Z-T4-chat-original-seed-save-roundtrip-j2v8.md

Scope is distinct from completed T4 original seed Load<T> actual CLR CI42043768798 and completed JSONL CI42043385806. All original source inputs stay exact SHA-pinned, only new temporary writable files, no Unity build or proprietary output. T1 unrelated Vulkan job was in progress, no shared native actions resources or cancellation. T5 owns any actual build and device test.

## Final checkpoint — 2026-11-05T14:45:45.001Z

- Work record completed: prompt/coordination/work/LOCAL-005/T4-20261105T1433Z-T4-chat-original-seed-save-roundtrip-j2v8-original-seed-save.json.
- Exact original inputs authenticated: immutable ZIP2 Assembly-CSharp.dll 3,211,776B SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e, shipped StreamingAssets/Data.rgd 2,941B SHA256 b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba, 151 original managed reference siblings. Previous original CLR Load<T> of this specific shipped seed succeeded CI42043768798, not evidence of an RGD world save.
- New scoped project android-port/Experiments/T4/OriginalRgdSaveRoundtrip, source-free validator scripts/t4_verify_original_rgd_save_roundtrip.py, synthetic tests and isolated .NET8 workflow. No actual game source/assets/meta modified.
- CI42046842892 SUCCESS 14/14: generic private Save IL/signature guard refusal. CI42047232842 SUCCESS 15/15: no private Save accepting shipped seed root type. Intermediate CI42047120293 and CI42047200973 failed during validator/schema refinement, not original serializer failures.
- FINAL https://github.com/alwansan/raf/actions/runs/42047540260 SUCCESS 16/16: original nonpublic Save(string,RGD) method shape verified in compiled IL, but shipped Data.rgd CLR root differs from its RGD argument. Category SHIPPED_SEED_ROOT_DIFFERS_FROM_ORIGINAL_RGD_SAVE_ARGUMENT; IL guard=false, original private Save invoked=false, original generated output=false, generated LoadT roundtrip=false, user-world/Android=false. Wrong seed rejected before any game invocation.
- A genuine game-generated world RGD must NOT be substituted by shipped StreamingAssets/Data.rgd. Original Load<T> of seed remains true but concerns a different original CLR type. No actual original Save serialization error was observed, do not change save schema or fabricate RGD for a test.
- Report docs/T4_ORIGINAL_RGD_SAVE_ROUNDTRIP_2026-11-05.md, T5 handoff prompt/coordination/discussions/LOCAL-005/20261105T1443Z-T4-shipped-seed-root-vs-saveRGD-to-T5.md, event prompt/coordination/B_TEAM/events/T4/20261105T1443Z-T4-shipped-seed-not-world-save-parameter.json. LOCAL-005 canonical issue and prompt/STATUS.md updated.
- No native build dispatched or cancelled, no actual Unity/IL2CPP/phone, new APK, game-world RGD serialization or process relaunch; sound/Settings unchanged and touch deferred. LOCAL-005 OPEN NOT_READY 0/3.
- Next: T5 coordinate one immutable signed native candidate with B07/T4/B50 markers; owner must create playable offline world, game-save actual RGD, stop fully, relaunch same installation, reopen same world playable. Correlate ordered JSONL with T4 CI42043385806 validator and genuine device logs. Do not use shipped seed as Save(RGD) fixture.
