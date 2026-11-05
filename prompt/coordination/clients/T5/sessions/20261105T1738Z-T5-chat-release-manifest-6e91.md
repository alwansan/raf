# T5 chat — actual APK86 Release small manifest bytes audit

- session_id: `20261105T1738Z-T5-chat-release-manifest-6e91`
- origin: `chat`
- status: `active`
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
