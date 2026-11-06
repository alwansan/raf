# T5 scheduled — native reconstruction checkpoint

- session_id: 20261106T2150Z-T5-scheduled-native-reconstruct-8b4f
- origin: scheduled
- resumed_from_sessions: 20261106T2139Z-T5-chat-xapk-crosspass-consistency-71fa; 20261106T1950Z-T5-scheduled-zip-prefix-6f2a
- base_sha: 75cf40a1f112a45f7f47a695d9ed70a9633f1699
- work_commit: 3f988e7dfb5680f7862279dc94242a5f0bdc5a3d
- issue: DELIVERY-013 / INTEGRATION-001
- state: waiting_ci

## Verified live evidence

Owner device feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered, saved and reopened world on signed artifacts from run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628. Do not extrapolate to current SHA. CL summaries show water passes and FFT errors and sparse FPS estimates, not GPU timings. T4 owns physical mouse, T5 owns three right-side buttons/Resolution, with no modifications here.

At check on 2026-11-06 21:50 UTC, [native run 42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) source a1737bd736e276d53df808442cfae3b1eea0d488 **in_progress**, reconstruct job 128163021015 at Unity Editor 2021.3.45f2 Android import/compile. Request gate and license preflight SUCCESS. No duplicate native dispatch. This immutable run predates the latest cross-pass XAPK packaging commit.

[T5 packaging CI42298819268](https://github.com/alwansan/raf/actions/runs/42298819268) **SUCCESS** on 0345ee05da47cbdb7dc679b80e20c3ade2a79f81; 17/17 synthetic delivery tests and 4/4 publish tests documented in resumed chat session. [ZIP conflict CI42283255333](https://github.com/alwansan/raf/actions/runs/42283255333) SUCCESS. Neither proves signed original package installed on phone. T4 owns unrelated backup-root source regression; no overlap.

## Decision and boundaries

No new Unity build because 5/5 trial consensus absent (T4 yes; T1/T2/T3/T5 no in trial-20261106-r1) and equivalent native job active. No source, Unity, APK, OBB, .meta, GUID, .rgd, touch, audio or Settings changed. No new phone/LogRaft measurements. Work scope isolated to this session/work checkpoint, avoiding teammates' production files. The useful result is exact live CI stage attribution and source-SHA separation preventing duplicate native execution or false package/device acceptance.

## Next

Poll run 42296450023; if failed inspect exact Unity compiler/import logs and isolate a separate failing assertion; if passed inspect artifact names and immutable SHA/signature/versionCode/OBB/delivery.json, and only then compare device LogRaft epochs. Move work from waiting_ci to completed after evidence. Full readiness NOT_READY 0/3.
