# A6 — isolated LOCAL-005 engineering

Identity `raft-20261103T100042Z-afcedabb`; session `a6-20261103T100042Z-8d2c701e`; only `feature/android-native-port` writable. Registered as HAPTICS-008 at 17af4fd2; subsequent live coordination identified A3, A4 and A5 on HAPTICS-008. A6 voluntarily paused that work, did not edit haptics/source, and pivoted to independent LOCAL-005.

Read current owner and AGENTS, coordination protocol, STATUS/readiness, latest handoff, existing HAPTICS-008 plans, A1 WATER and A2 DISPLAY states. Local save path sources inspected: `LocalSavePaths.cs`, `LocalProfileStore.cs`, `LocalPlayerIdentity.cs`, original save path adapter, smoke suite and source-only workflow. Existing save format `.rgd` remains original; helper `world.sav` is isolated prototype, not proof that game SaveAndLoad uses it.

Plan: reproduce concrete path/sandbox or cross-platform defect with an executable local test before any safe source change. No Unity/native/OBB/APK, existing requests, release or automation changes. Do not change `.meta`/GUID, original assets or `.rgd` serialization.

## Confirmed A6 scoped result — 2026-11-03T10:13:01.911Z

- Local Linux filesystem reproduction: lexically rooted world path redirected through pre-existing `worlds/redirect -> outside` symlink and wrote a synthetic `world.sav` outside; not a device test.
- Published [0fa98e71](https://github.com/alwansan/raf/commit/0fa98e71fbe5c06a1e92cae3d93fff89fae2fec0), changes EXACTLY `android-port/Runtime/Platform/LocalSavePaths.cs` (+20) and `android-port/Tests/Smoke/Program.cs` (+26), no .meta, original game source, RGD, LFS or shader modifications. Check preexisting and post-create descendants for `FileAttributes.ReparsePoint`, not caller-provided root ancestors; deliberately no claim of atomic symlink-race immunity.
- Two new .NET smoke cases: world symlink and profile ancestor symlink, plus preexisting valid/unsafe world name tests. Same-source [platform Actions 41617053603](https://github.com/alwansan/raf/actions/runs/41617053603) COMPLETED SUCCESS; all job steps successful. A later platform run from an independent commit was in progress at review; do not conflate its source.
- This fixes only the standalone platform helper's preexisting-link handling. No claim the private original `SaveAndLoad` calls this helper. Original `.rgd` and offline world resume still need authentic integration evidence. LOCAL-005 project gate NOT CLOSED. No Unity, APK, OBB, XAPK, native request, Release or automation mutation by A6.
- A3/A4/A5 independently investigate HAPTICS-008; A6 paused its overlapping record before touching haptics. New work must read their fresh plans.
- CI/Git ref incident: the initial branch update returned GraphQL UNKNOWN twice and did not apply; confirmed target source hashes unchanged, rebuilt commit from live HEAD and used expected SHA successfully. See A6 incident record.
- A6 session paused after this bounded task, does not run in the background.
