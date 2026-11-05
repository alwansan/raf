# T4 session — exact original Data.rgd genuine CLR + SaveAndLoad.Load<T>

origin: chat
session_id: 20261105T1405Z-T4-chat-original-rgd-runtime-k6n8
resumed_from_sessions:
- 20261105T1217Z-T4-android-save-postcheck (last original T4 chat state)
- 20261105T1246Z-T4-chat-load-file-gate-m8q2 (subsequent original Load.argumentFileSnapshot stage)
- 20261105T1338Z-T4-scheduled-v6n9 (most recent scheduled device evidence contract)
base_sha: 5eed7b6715a25177e733d17f383bb8735368bdbf
writable_branch: feature/android-native-port
issue: LOCAL-005

## Start / coordination
- User said "Stay in Chat and Continue"; retained original T4 identity and normal chat. Read latest T_TEAM RESTORE / CHAT_AND_SCHEDULE and role/source instructions, latest T4 sessions from both chat and scheduled, T4 state/MEMORY as helper only, issue/contract, A10 and B37 original Data.rgd metadata evidence and T5 integration history.
- At entry HEAD 5eed7b6715a25177e733d17f383bb8735368bdbf; no current Actions jobs in page checked; CL main 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29 (last device data), newest Raft game release still APK86 `android-early-test-41812889049-1` not the newer source. Other T clients working on renderer/FFT/foam and platform forensics. No job cancellation or shared native request edit.
- Distinct from scheduled T4 13:38 contract or chat 12:46 Load.argumentFileSnapshot: new hypothesis that the **shipped original RGD itself can actually be deserialized into the original game CLR type, and through the exact original compiled generic loader**, not just NRBF parsed.

## Plan registered BEFORE code
- `prompt/coordination/work/LOCAL-005/T4-20261105T1405Z-chat-original-rgd-runtime-k6n8.json`
- `prompt/coordination/work/LOCAL-005/T4-20261105T1417Z-chat-original-loadt-k6n8.json`
- Experiment key `t4-original-rgd-2941-byte-sha-pinned-real-binaryformatter-plus-original-SaveAndLoad.LoadT-dotnet8-151-sibling-v1`.
- Source ZIP2 exact immutable commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385, original `Raft/Raft_Data/StreamingAssets/Data.rgd` size **2941 B** SHA256 `b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba`; original `Raft/Raft_Data/Managed/Assembly-CSharp.dll` size **3211776 B** SHA256 `0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e`; **151** reference siblings pinned at feature commit 02e9fba7fb42b83579595885391be636ee3b56e8. No LFS, Unity, original game source or private serial payload pushed.

## Executed engineering and evidence
- Built `android-port/Experiments/T4/OriginalRgdRuntimeLoad/OriginalRgdRuntimeLoad.csproj`/.NET8 `Program.cs` to check original immutable SHA/size and companion count, load actual original DLL using restricted local reference resolver and **execute BinaryFormatter.Deserialize on one exact 2941B shipped seed**. Capture only source verification, successful original root type identity, bounded failure categories, no original data/type/member names or stack trace. Source-free validator `scripts/t4_validate_original_rgd_runtime_load.py` and **18/18** unit controls including false Android/game claims and wrong SHA rejection.
- [CI42042814576](https://github.com/alwansan/raf/actions/runs/42042814576) **SUCCESS**: original SHA checks and exact 151 siblings; actual BinaryFormatter object created; root CLR type truly comes from exact original Assembly-CSharp.dll; category NONE, modified seed rejected before deserializer.
- Extended the same opt-in runner to locate unique exact static compiled original `SaveAndLoad.Load<T>(string)` generic method in the loaded DLL, bind T to the authentically reconstructed original root CLR type, and **invoke this actual original game method** with the exact original file. Separate fail-closed `scripts/t4_validate_original_rgd_loadt.py` + **18/18** tests assert method really invoked and original same CLR type returned, with no false native/phone/save claim.
- [CI42043768798](https://github.com/alwansan/raf/actions/runs/42043768798) **SUCCESS 18+18 controls**, first direct genuine original seed deserialized then `original_SaveAndLoad_LoadT_invoked=true`, `original_LoadT_method_signature_verified=true`, `original_LoadT_returned_matching_seed_type=true`, `original_LoadT_result_category=NONE`. Wrong seed SHA refused.
- Original failed [CI42042350875](https://github.com/alwansan/raf/actions/runs/42042350875) and [CI42042563929](https://github.com/alwansan/raf/actions/runs/42042563929) were CI harness `ulimit -f` artificially triggering `SIGXFSZ exit153` from core dumps before C# reports; not proof original seed was invalid. Changed to disabled dump generation, private log and timeout without restrictive file cap, while preserving exact SHA gate. Successful runs followed.
- Full report `docs/T4_ORIGINAL_RGD_RUNTIME_LOAD_2026-11-05.md`; work records marked completed; experiment `prompt/coordination/experiments/T4/20261105T1405Z-shipped-original-rgd-real-clr-and-loadt.json`; event `prompt/coordination/B_TEAM/events/T4/20261105T1426Z-original-RGD-real-LoadT-success.json`; issue LOCAL-005 updated; T5 handoff discussion `prompt/coordination/discussions/LOCAL-005/20261105T1425Z-T4-original-Data-rgd-real-LoadT-to-T5.md`.

## Interpretation / next work
- Prior A10/B37 original metadata version/serialized root member mismatch remains factual, but it **did not block** real CLR object reconstruction or genuine compiled original SaveAndLoad.Load<T> for this one shipped seed under tested .NET8/Ubuntu runtime. Do not claim all legacy/user saves compatible.
- **Not done:** original user-generated world .rgd SaveGame/SaveWorld/SaveUser, local host playable world, real process quit and reopen, Unity 2021 ARM64 IL2CPP, Android filesystem or phone. None were simulated, built, installed or represented as successful. `LOCAL-005 OPEN` and overall `NOT_READY 0/3`.
- Next distinct test that would close relevant gate: T5 coordinates a single immutable signed native candidate including B50 Steam guards, B07 firstMoveNext, T4 originalCompletionAssigned and Android-only Save/Load filename snapshots + Load.caughtException. On phone create playable offline raft → save actual world → fully quit → relaunch → reopen same user-generated .rgd into playable state. Correlate original events without logging private paths. Working audio/Settings preserved, touch/layout deferred. Other team runs and shared native request untouched.
