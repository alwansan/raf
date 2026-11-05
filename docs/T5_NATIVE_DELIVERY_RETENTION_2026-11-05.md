# T5 — immutable native delivery ZIP retention experiment (5 November 2026)

## Scope and necessity

Owner's Poco F5 Pro world entry, save, exit and reopening were confirmed with the artifact of native GitHub Actions run [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), original source `e9c358eda01785b65e4eb14f18723da426635628`. Original `reconstruct`/Unity/IL2CPP/signature/package steps succeeded, but `publish-early-test` failed HTTP 403 when attempting to create a GitHub Release. This failed publication step must not be misreported as a failed Unity compile, or bypassed by an unauthorized token.

Artifact `13441227298` (`raft-android-test-delivery`) expires 2026-11-06 18:19:05 UTC and its **GitHub archive ZIP** is reported as exactly 5,948,243,524 bytes with SHA256 `29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6`. The second signed-checkpoint artifact `13441766832` is distinct (2,974,110,506 bytes, expiry 2026-11-07 18:18:17 UTC). The archive ZIP digest does not by itself prove the inner APK/OBB/XAPK hashes.

## Engineering solution

`scripts/t5_verify_retained_delivery_archive.py` provides a bounded, read-only verifier. It pins and hashes the original ZIP container, checks that it is a flat, unique, safe ZIP inventory, reads only small `delivery.json` and `SHA256SUMS` into memory, enforces package identity and native versionCode=89, and streams **each actual payload ZIP member** to recompute every transport-part SHA256 and the concatenated full logical APK, OBB, XAPK digests/lengths against `delivery.json`. ZIP member CRC is also checked on end-of-stream. It rejects unexpected payload members, parts out of order, wrong quantities and mismatched checksums. It never unpacks a game file, dumps proprietary bytes or invokes the game.

`tests/test_t5_verify_retained_delivery_archive.py` builds synthetic tiny transport ZIP fixtures with 18 positive and adversarial tests (archive hash/size, identity, same-size payload drift, logical and part hash drift, missing, reordered or extra parts, dangerous ZIP members, duplicated entries and malformed metadata).

The one-shot standalone CI `.github/workflows/raft-t5-retain-native-delivery.yml` pins original run/commit, artifact ID, byte size/digest, and run number; runs those controls before any large download, checks actual free disk, acquires the authenticated **same original ZIP** from the GitHub Actions API, streams all actual parts using the validator and—only after success—attempts `upload-artifact@v4` with a new, distinct 3-day retention window. It uses read-only `actions:read` and `contents:read`, never Release write permissions, no Unity, no new APK build, no native request changes, concurrency group per original artifact and `cancel-in-progress:false`.

Manual re-execution on the exact source would be redundant unless the first run failed for a diagnosed and repaired reason. It does not run on unrelated pushes, because the push job is gated by the one-shot message tag; workflow_dispatch remains possible for a specifically approved later attempt.

## Recovery use

If the new artifact exists and is verified, download `t5-retained-native-delivery-42058825739`, extract its **one ZIP file**, then extract that original GitHub delivery ZIP. The resulting `delivery.json`, `SHA256SUMS`, `reassemble.py`, APK and OBB/XAPK transport parts are exactly the owner-authorized immutable native delivery, subject to the CI's reported checks. Reassemble selected OBB or XAPK from its parts with the project's SHA-checked helper; do not install a `.part001` or confuse outer nested ZIP with an XAPK.

**Limits:** even a green job does not prove APK signing format, installation, OBB GUID mapping, water FFT, Adreno rendering, phone performance or owner gameplay beyond the already reported artifact scenario. A new Actions artifact is not a public GitHub Release; failed `gh release create` permission must be fixed separately by authorized maintainers. If ZIP fetch or upload hits quota/storage/ruleset errors, report exact failure and do not claim preservation. Source fidelity and NOT_READY 0/3 remain.

- Original run: https://github.com/alwansan/raf/actions/runs/42058825739
- New retention experiment: https://github.com/alwansan/raf/actions/runs/42110297871
- Chat checkpoint: prompt/coordination/clients/T5/sessions/20261105T2110Z-T5-chat-retain-delivery-a6f8.md

## Verified run result — 2026-11-05 21:13 UTC

**SUCCESS:** [Actions run 42110297871](https://github.com/alwansan/raf/actions/runs/42110297871), job127535758223, immutable experiment source `df6144411a130cc1ac23f1df4ae7f653d61e9704`.

- Source-free precheck: **18/18 tests passed in 0.030s**; Python compilation passed.
- Original GitHub API run and artifact metadata verified: native run 42058825739, source `e9c358eda01785b65e4eb14f18723da426635628`, versionCode **89**, original artifact 13441227298, size 5,948,243,524B, digest `sha256:29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6`, not expired at acquisition.
- **Real 5.95GB source archive downloaded, full archive digest and size verified**. All **7 actual transport-part byte SHA256** and all **3 logical APK/OBB/XAPK concatenated byte SHA256/lengths** matched the manifest. The total actual logical payload bytes read were **5,948,221,616B**. All ZIP streams were read through EOF, checking their CRCs. The result reported false for APK signature, Unity GUID and device mount verification; it did not falsely upgrade these claims.
- **Retention succeeded:** a new independent Actions artifact `13454900880`, name `t5-retained-native-delivery-42058825739`, outer ZIP bytes **5,948,243,834**, outer ZIP digest `sha256:41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef`, expires **2026-11-08 21:12:40 UTC** (2026-11-09 00:12:40 Asia/Baghdad).
- New artifact's outer ZIP digest is expected to differ from original Actions archive ZIP digest: it stores the **exact original 5,948,243,524-byte archive as a single file**, adding an outer artifact transport ZIP envelope. For recovery download and unpack outer ZIP, verify inner ZIP has original pinned SHA, unpack inner ZIP, then reassemble desired APK+OBB/XAPK lossless transport.
- Separate GitHub Release creation HTTP403 is not repaired; no Release was created by this read-only Actions workflow. New artifact does not claim publication or installation; owner phone observation still belongs to the old native candidate and prior reported scenario.

This closes **this narrow retention/byte-integrity experiment only**, not the shared INTEGRATION-001, WATER-001 or rendering blockers. NOT_READY 0/3. No full native Unity build, signing action, modified package/game files, LFS transfer or T1–T4 work was touched.
