# A6 — isolated LOCAL-005 engineering

Identity `raft-20261103T100042Z-afcedabb`; session `a6-20261103T100042Z-8d2c701e`; only `feature/android-native-port` writable. Registered as HAPTICS-008 at 17af4fd2; subsequent live coordination identified A3, A4 and A5 on HAPTICS-008. A6 voluntarily paused that work, did not edit haptics/source, and pivoted to independent LOCAL-005.

Read current owner and AGENTS, coordination protocol, STATUS/readiness, latest handoff, existing HAPTICS-008 plans, A1 WATER and A2 DISPLAY states. Local save path sources inspected: `LocalSavePaths.cs`, `LocalProfileStore.cs`, `LocalPlayerIdentity.cs`, original save path adapter, smoke suite and source-only workflow. Existing save format `.rgd` remains original; helper `world.sav` is isolated prototype, not proof that game SaveAndLoad uses it.

Plan: reproduce concrete path/sandbox or cross-platform defect with an executable local test before any safe source change. No Unity/native/OBB/APK, existing requests, release or automation changes. Do not change `.meta`/GUID, original assets or `.rgd` serialization.
