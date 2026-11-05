# T5 chat — actual APK86 Release small manifest bytes audit

- session_id: `20261105T1738Z-T5-chat-release-manifest-6e91`
- origin: `chat`
- status: `completed`
- base_sha: `380f59958bda4b47895c8239bf5327f48c2ff7fa`
- resumed_from_sessions: `20261105T1713Z-T5-chat-release-metadata-83ac`, scheduled `20261105T1646Z-T5-scheduled-c71e`
- issue: INTEGRATION-001
- work: `prompt/coordination/work/INTEGRATION-001/T5-20261105T1738Z-T5-chat-release-manifest-6e91-manifest-byte-bind.json`
- experiment_key: `t5-gh-release-apk86-real-small-metadata-bytes-hash-deliveryjson-SHA256SUMS-vs-public-assets-and-7-transport-parts-v1`
- resource_key: `t5-release-small-metadata-only-GitHubActions-no-Unity`

## Baseline and distinct scope

[Native CI42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) on fixed e9c358eda01785b65e4eb14f18723da426635628 remains `in_progress` in **actual Unity Editor 2021.3.45f2 Android import/compile** step62. Request/license/original Mesh/40 original scenes and documented water trial acknowledgement succeeded; genuine Unity completion, signed APK, OBB, XAPK, Release, phone water and local world RGD remain unverified. No native retry/cancel, no T1–T4 source edit.

The preceding T5 [CI42072829025](https://github.com/alwansan/raf/actions/runs/42072829025) proved 28/28 **public API-only** Raft APK86 Release metadata consistency against native CI41812889049, tag android-early-test-41812889049-1. To improve actual artifact provenance without multi-GB downloads, this cycle validates the **bytes** of precisely two small files: Release `delivery.json` (2,166 B) and `SHA256SUMS` (727 B). Their expected API SHA256 digests are public and checked separately. All 7 game transport part hashes/sizes are reconciled as **declarations only**, not cryptographically rehashed game bytes.

## Implementation/test scope

Read/download the two tiny real metadata files with `gh release download` in **isolated CPU-only Actions**. Validate their actual SHA256 against exact Release asset API metadata, their declared transport part SHA256 and lengths against live public metadata, three logical whole APK/OBB/XAPK declared digests/lengths against publisher body claims, and SHA256SUMS entries exactly matching the manifest. Reject extra/missing/duplicated part, wrong logical source, bad hash, mismatch/altered manifest, unsafe name, and APK/OBB identity drift. Source-only synthetic adversarial fixtures plus real download CI. No ZIP2, original bytes, Unity binary, APK signature, OBB mount or Android install tested.

## Next

Create own script, tests and narrow workflow; run CI and record exact result in experiment/event; close own work. Continue original native run monitoring separately. Overall NOT_READY 0/3.


## Verified end-of-chat cycle — 2026-11-05 17:44 UTC

- **Original actual published game source:** native CI41812889049 immutable d181ee7152580f49ee0b41dfd05fa2bfdacfafe5 and GitHub Release android-early-test-41812889049-1. Real production old APK86 not a newer experimental Unity binary.
- New independent `scripts/t5_verify_release_manifest_bytes.py` and `tests/test_t5_verify_release_manifest_bytes.py`; small GitHub workflow `.github/workflows/raft-t5-release-manifest-bytes.yml` from commit 54adc9b235a56b815095f5de622664bc1fb03144.
- Actual [CI42077040831](https://github.com/alwansan/raf/actions/runs/42077040831), job127419899287, **COMPLETED SUCCESS**: `Ran 28 tests in 0.007s; OK`. This used the exact published `delivery.json` (2166B; SHA256 3a672dd06f1b582eb56a670c6b54ddf6296c3f4b62c031af32ee8c3c768c97b9) and `SHA256SUMS` (727B; SHA256 18eb4be15a90b2b861284eb3179168f8614f60d99412429125f361f882a53daf), downloaded with gh release download under 12KB each. Actual SHA256 of these two files matched live GitHub Release API asset metadata exactly; all 7 transport-part declarations bind across downloaded `delivery.json`, `SHA256SUMS`, live API asset records, and frozen old release source claims.
- **Verified scope only:** 2 tiny metadata files' real bytes and 3 logical file / 7 transport part metadata declarations. No actual 7 large payload part bytes were downloaded or rehashed, no APK v2/v3 signature, full XAPK reassembly, OBB mount, Android install, playable offline world or RGD persistence tested. Real release metadata matches does not mean game is playable.
- Work completed: prompt/coordination/work/INTEGRATION-001/T5-20261105T1738Z-T5-chat-release-manifest-6e91-manifest-byte-bind.json. Experiment completed: prompt/coordination/experiments/T5/T5-20261105T1738Z-T5-chat-release-manifest-6e91-manifest-authenticity.json. Event: prompt/coordination/B_TEAM/events/T5/20261105T1744Z-release-manifest-bytes.json.
- Original newer native CI42058825739 immutable e9c358eda01785b65e4eb14f18723da426635628 remains `in_progress` at actual Unity 2021.3.45f2 Android import/compile step62; four water/graphics diagnostics only, no APK/OBB/XAPK release. Past original water gate was successful *as experimental acknowledged deficits only*, not GPU authenticity. No duplicate heavy build, cancellation or T1–T4 source edits. NOT_READY 0/3.

## Next exact resumption
Requery immutable GitHub native run 42058825739 before any new build request. If Unity Editor/IL2CPP fails, inspect its first actual failing job/log (not downstream artifact-gate effects). If package/Release publishes, verify exact source and actual APK/OBB/XAPK bytes/signatures and test offline-world save/full process exit/same-world reopen and water/FX on device. Any new release gets a new pinned source manifest test, never blindly reusing the old APK86 fixture.
