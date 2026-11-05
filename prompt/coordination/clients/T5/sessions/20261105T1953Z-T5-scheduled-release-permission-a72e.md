# T5 — release authorization and artifact recovery decision (2026-11-05 19:53 UTC)

Origin: scheduled. Source branch: feature/android-native-port. Baseline SHA: 8a0237aea53c76252bd710d7e939d862296a3d0c. Experiment: t5-release-403-42058825739-token-permissions-and-expiry-readonly-v1.

## New independently verified facts

- Live immutable native run 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628): reconstruct SUCCESS, publish-early-test FAILURE, delivery-result FAILURE. Job 127441439836 downloaded delivery, then at 2026-11-05 18:21:48 UTC `gh release create` received `HTTP 403 Resource not accessible by integration` from POST /repos/alwansan/raf/releases. This is a release-creation permission failure, not a Unity compiler error.
- Live feature branch workflow blob 24683d3102d589aebaf7451d8d7515266ce26628 already explicitly grants `permissions: contents: write` for publish-early-test (lines 979–983). Thus adding that same permission line is not a novel fix and must not be claimed as such.
- Read-only GitHub Release API GET /releases/tags/android-early-test-42058825739-1 returned 404 at this checkpoint; no verified published release for this run.
- Read-only Actions artifact API still reports delivery artifact 13441227298, 5,948,243,524 bytes, digest sha256:29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6, expires 2026-11-06 18:19:05 UTC. Signed checkpoint artifact 13441766832, 2,974,110,506 bytes, digest sha256:0e99e82c44af0fa21f613515ca0cb8eee2c04aa7911e9a001aabd1abdcde16bd, expires 2026-11-07 18:18:17 UTC. Both `expired=false` on read.
- Repository Actions workflow permission settings endpoint was not exposed by the available read-only GitHub connector (endpoint rejected as unsupported); consequently actual token permission, ruleset and installation policy remain UNKNOWN. Do not infer a specific root cause from 403.

## Minimal authorized recovery, no Unity rerun

1. Owner/authorized maintainer checks repository Settings → Actions → General → Workflow permissions, organization policy and any ruleset/app restrictions. Existing YAML job contents:write is necessary but not evidence of effective token rights.
2. Before 2026-11-06 18:19:05 UTC, download the exact delivery artifact from run 42058825739 via authenticated `gh run download 42058825739 --repo alwansan/raf --name raft-android-test-delivery --dir <private-empty-dir>`. Keep it private and check extracted delivery.json, SHA256SUMS and each declared file byte size/hash. The API archive digest is a ZIP digest, not each game payload SHA.
3. Publish from the saved verified files only with an authorized token, immutable source e9c358eda01785b65e4eb14f18723da426635628 and tag android-early-test-42058825739-1; never use an unverified file or claim success before remote asset list, sizes and digests are checked. Prefer an owner-authorized release-only workflow or maintainer CLI, not rerunning 2.5-hour Unity.
4. If no authorized release creation is possible, retain the downloaded archive privately before expiry. The signed checkpoint provides a second recovery window but is not a full published delivery.

## Negative evidence and boundaries

No release created, no token changed, no artifacts downloaded to this session, no native build dispatched or cancelled, no game code/asset/.meta/GUID/serializer/audio/Settings/touch changes. This is read-only live authorization/retention forensics and a deterministic recovery handoff, not a proven permissions fix or Android phone test. Water/FFT/graphics and local-world save remain NOT_READY 0/3.

Next: confirm whether owner-authorized artifact preservation/publication occurred; if not, prioritize retaining delivery bytes before expiry, then use actual effective-token policy to select a release-only repair.
