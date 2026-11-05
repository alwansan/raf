# T4 → T5: completed native build reconstruction, Release publication HTTP403
- session_id: 20261105T181919Z-T4-chat-overflow-ci-9dzc8
- author: T4 (read-only complementary diagnostic)
- issue: INTEGRATION-001
- resource_key: T5-native-publish42058825739-readonly
- source run: https://github.com/alwansan/raf/actions/runs/42058825739
- source immutable SHA: e9c358eda01785b65e4eb14f18723da426635628
- observed_at: 2026-11-05T18:25:00Z

Read-only verified from GitHub Jobs API and decoded publish job 127441439836:
1. native-request-gate SUCCESS, unity-license-preflight SUCCESS, reconstruct SUCCESS.
2. publish-early-test failed in `Publish complete APK OBB XAPK packages and lossless transport parts`; delivery-result propagated failure as intended.
3. Download-artifact succeeded and verified transfer SHA digest for compressed `raft-android-test-delivery`; exact fatal line at 18:21:48 UTC: `HTTP 403: Resource not accessible by integration (https://api.github.com/repos/alwansan/raf/releases)` on `gh release create`. Therefore release was not successfully published by this run; this step does not implicate Unity compile or establish Android install success.
4. GitHub artifact metadata:
   - delivery `raft-android-test-delivery`, artifact ID **13441227298**, compressed 5,948,243,524 B, expires **2026-11-06 18:19:05 UTC**.
   - `raft-android-signed-output-checkpoint`, ID **13441766832**, compressed 2,974,110,506 B, expires **2026-11-07 18:18:17 UTC**.
   - metadata URLs accessible in Actions run artifacts; expiry may require owner to promptly retrieve/re-publish.

Suggested owner-authorized recovery: independently identify why Release creation token returned 403 despite reported `Contents: write`, verify repository/workflow and GitHub App token permissions and any repository-level policy, then publish from still-valid existing delivery/checkpoint artifacts using an identity authorized for Releases, after byte-size/SHA and package consistency validation. Do not log or embed tokens, change branch/release guards, turn off authenticity gates, or rerun Unity merely to retry Release authorization. If owner cannot publish before expiry, preserve the known signed checkpoint under approved private storage. T4 made no workflow/release changes for this T5 scope. No new Raft Release, phone test, or complete-world acceptance claimed.
