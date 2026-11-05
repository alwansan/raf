# T5 — actual owner-phone OBB GUID warnings are **patch.89** lookups (5 November 2026)

## Original evidence

The owner confirmed world entry, saving, exit and reopening using native [run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) artifacts (source `e9c358eda01785b65e4eb14f18723da426635628`, versionCode **89**). The source-pinned full game delivery was byte-verified in [run42110297871](https://github.com/alwansan/raf/actions/runs/42110297871), then independently checked with **actual APK aapt identity, cryptographic apksigner and actual matched OBB** in [run42117471172](https://github.com/alwansan/raf/actions/runs/42117471172): both APK/OBB exact SHA256 matched, package `com.alwansan.raft.androidtest`, versionCode 89, APK signature valid, original OBB ZIP contains 39 entries. No device-side install path or Unity internal GUID acceptance was established.

Read directly from **Git blobs of original CL logs**, not just aggregate LogRaft summaries, pinned owner CL commit `520c4cf409aa20a4db54ff80ed87d8807d9cba57`:

- LogRaft session `20261105-220911-559`, segment1 Git blob `d50b9fde330c425e15d444922c214a5b112bb264`: **one** actual Unity `Unable to load GUID for '.../Android/obb/com.alwansan.raft.androidtest/patch.89.com.alwansan.raft.androidtest.obb'` at 22:09:32 local. Segment2 Git blob `9a6d3ba358b89ba387217c87e0b410b401fd150e`: **zero** OBB GUID warnings.
- Session `20261105-230108-327`, segment1 Git blob `cb3a3318b604c1cfbc43583e05580a39bcb66c81`: **two** exact `patch.89...` GUID warnings at 23:01:38 and 23:01:55 local. Segments2–4 blobs `5275f859334fa47bcfc74f0ca5f0530e260102e6`, `a28d2451af66cfc60a682b3bc22626041eccae2b`, `660f9ef6030cd30ae33bbcf5ac7389d85fcd5d4e`: zero additional OBB GUID warnings. Cited blob hashes serve reproducibility; full raw logs are not copied or republished.
- **All 3** observed OBB GUID warning strings specifically name **`patch.89`**, NOT `main.89`. The authenticated delivery's only declared companion expansion file is `main.89.com.alwansan.raft.androidtest.obb`; it includes no `patch.89` companion. Google Play expansion conventions permit an optional patch OBB separate from main; the observed Unity lookup cannot be used as proof that the main OBB is corrupt or has a wrong package/version.

## Engineering integration and controls

New read-only `scripts/t5_classify_obb_guid_logs.py` streams raw LogRaft text without storing, uploading, or printing full device paths. It classifies exact OBB paths into **main GUID warning**, **optional unshipped patch probe**, **declared patch GUID warning**, **foreign package/version** or **other GUID warning**. It validates current package/version against a supplied authenticated logical delivery inventory and refuses malformed/duplicate filename claims. It does **not** suppress, catch or modify Unity warnings; it labels their diagnostic origin.

New `tests/test_t5_classify_obb_guid_logs.py` provides **16** synthetic positive/negative classifications, including wrong parent package, wrong version, actual 1+2 observed warning shapes, a real main OBB warning that must not be reclassified as optional, declared patch and unsafe metadata.

One-shot narrow CI `.github/workflows/raft-t5-obb-guid-log-identity.yml` uses **the six actual original CL raw log segment files** from the pinned CL commit; checks each downloaded file's Git blob SHA, then counts patch versus main categories without uploading any logs or game files. It compares exactly **1+2=3** patch warning messages and **zero main** against original LogRaft summary evidence. [Run42119428667](https://github.com/alwansan/raf/actions/runs/42119428667) must complete successfully before counting this CI as proven. Separately, the actual CL original Git blobs were read and pattern-checked directly during this chat; details above are already supported.

## Interpretation, limits, next action

The original phone log `obb_guid_load_failed` **category conflates an optional patch OBB lookup with an actual main OBB failure**. This narrows the owner's concern: the observed three warnings alone do **not** warrant repackaging/rebuilding APK+main OBB, or replacing GUIDs. It does not prove `patch.89` is physically absent from the phone, that its optional lookup can never matter, or that `main.89` mounted with the right bytes on device. The actual owner game+save+reentry observations remain positive evidence from that installed artifact; the true cause of missing water/FFT/pass and white surfaces remains independent.

Do not 'fix' this by hiding Unity errors or creating an invented empty patch OBB. Next scoped test should inspect on-device `/Android/obb/com.alwansan.raft.androidtest/main.89...obb` hash/location, and seek exact Unity resource GUID/offset failures only if the **main** path appears in new logs. Keep `INTEGRATION-001` open, `NOT_READY 0/3`; audio/Settings, T5 scheduled Resolution, T1–T4 source and deferred touch remain unchanged.

Session: `prompt/coordination/clients/T5/sessions/20261105T2208Z-T5-chat-obb-guid-3d7a.md`.
