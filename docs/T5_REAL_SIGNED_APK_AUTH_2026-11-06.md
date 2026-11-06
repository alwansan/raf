# T5 — full byte authentication of the original Android signed APK

**Session** `20261106T1330Z-T5-chat-signed-apk-auth-f7b2`; `origin=chat`, `issue_id=INTEGRATION-001`, branch `feature/android-native-port` only. This verifies **a completed older owner-tested signed artifact**, not a rebuild of current source or Android graphics acceptance.

## Exact immutable source

- [Original owner-tested build #42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), `source_commit=e9c358eda01785b65e4eb14f18723da426635628`; original owner confirmed world enter/save/exit/reentry on that APK+OBB.
- GitHub Actions delivery artifact `13441227298`, `raft-android-test-delivery` ZIP bytes `5,948,243,524`; signed checkpoint artifact `13441766832`, `raft-android-signed-output-checkpoint` ZIP bytes `2,974,110,506`. Pinned provider metadata SHA descriptors were authenticated by REST before reading; the full outer archive transport SHA was **not** rehashed.
- The **actual original delivery ZIP's 2,166-byte `delivery.json`** was read via strict 206 ranges and provided expected APK length **672,853,870 bytes** and **full source-declared SHA-256**, held only in private runner memory. The `checkpoint` ZIP's APK member was independently verified **ZIP_STORED** via local header; therefore the 672,853,870 actual APK bytes could be streamed from the archive's authenticated inner offset without downloading the entire 2.97 GB checkpoint or 5.95 GB delivery envelope. Full original APK bytes were temporarily stored in runner-private disk and deleted after verification.

## Verified real-world facts

[GitHub Actions #42228262902](https://github.com/alwansan/raf/actions/runs/42228262902), job `127927198011`, exact source commit `7e5d69ce00e5c22183915205f164b67101694d8c`, **COMPLETED SUCCESS**, with 12/12 synthetic negative/positive unit tests and Android SDK build-tools `37.0.0` installed.

| Independent verification | Original source-verified result |
|---|---|
| Actual signed APK read and hashed | **All 672,853,870 bytes** |
| Actual signed APK SHA-256 vs exact original `delivery.json` declared SHA-256 | **MATCH** (verified full 64-character digest in runner; safe prefix `d200b212ca8c`) |
| `aapt dump badging` on actual signed APK binary manifest | **PASS** |
| Binary `AndroidManifest.xml` package (not delivery guess) | `com.alwansan.raft.androidtest` |
| Binary manifest actual `versionCode` | **89**, matches delivery claim |
| `apksigner verify --verbose --print-certs` native Android CLI exit status | **0 — cryptographic verification passed** |
| APK signing scheme v1 / v2 | **true / true** |
| APK signing scheme v3 / v4 | **false / false**, not needed to claim v1/v2 validity |
| Number of signers reported by `apksigner` | **1** |
| Reportable certificate SHA-256 metadata | **UNKNOWN / NOT PARSED**, no fingerprint invented; tool's signer metadata format did not match the safe digest parser |
| Full signed main OBB SHA256, Unity GUID, phone mount | **NOT VERIFIED** |
| Current branch new Android build / water FFT, shaders, GPU pixels | **NOT VERIFIED** |

The report distinguishes **full original signed APK file SHA match**, **binary Android manifest identity** and **actual apksigner cryptographic verification**. None is silently inferred from ZIP central file size alone. The APK certificate's SHA prefix is intentionally empty, so the result does **not** assert the fingerprint or compare trust against an independent owner-pinned signer. The local delivery manifest is not itself externally cryptographically signed.

## Controls and non-success runs

- New isolated `scripts/t5_verify_real_signed_apk.py`, `tests/test_t5_verify_real_signed_apk.py`, `.github/workflows/raft-t5-real-signed-apk-attestation.yml` under T5 scope; only GitHub Actions token injected in runner, no URL/credential/raw APK/IL/game data published, no Unity build or T1–T4 files touched.
- [CI42226874653](https://github.com/alwansan/raf/actions/runs/42226874653) **failed** before any full download due to a duplicate synthetic test lambda parameter. [CI42226998096](https://github.com/alwansan/raf/actions/runs/42226998096) **failed** before download because test fixture precedence did not duplicate the whole aapt badging string. Both test bugs fixed.
- [CI42227170402](https://github.com/alwansan/raf/actions/runs/42227170402) **failed the T5 reporting gate after** real complete APK SHA, binary `aapt`, and `apksigner verify` CLI all passed, because the reporter incorrectly assumed it must parse exactly one SHA-256 certificate fingerprint. The fix distinguishes verified crypto command success from **optional unparseable certificate display metadata**, supports multiple signers and never invents a single signer from missing output.
- [CI42228036640](https://github.com/alwansan/raf/actions/runs/42228036640) and [CI42228145311](https://github.com/alwansan/raf/actions/runs/42228145311) failed synthetic fixtures **before download** during reporter adjustment; fixed test assertions. Final [CI42228262902](https://github.com/alwansan/raf/actions/runs/42228262902) passed all 12 synthetic tests and real native APK SHA/aapt/apksigner gates. No false APK corruption diagnosis from intermediate test failures.
- The signed APK bytes were streamed only through exact expected GitHub 206 `Content-Range` requests (no HTTP 200 full-download fallback). Hard byte cap 700 MiB, per-range 4 MiB and at least 1 GiB preflight free disk; Android tools discovered from installed runner SDK without installing new build tools. Private temporary APK deleted after success or failure.

## Next verification and game acceptance

**Next resource-dependent action**: authenticate the existing **2,301,256,312-byte** original main OBB member by a complete bounded SHA-256 stream against actual original `delivery.json` (prefer hashing with no disk copy, 2.3 GB transfer cap and explicit resource coordination); cross-check Unity internal OBB GUID/access and actual audio/FMOD resources separately. If an independently supplied pinned signing certificate fingerprint is available, extract and compare real signer certificate metadata without guessing its identity. Recheck SHA and package version on the exact installed APK before making any phone-source conclusion.

**Still OPEN:** water shaders, FFT, colors/effects/fire/dynamic lighting, full Android phone readiness, current branch APK/OBB delivery, and current build Unity device rendering. Source/test success is not game readiness; team gate remains **NOT_READY 0/3**.
