# T5 — original owner-tested main OBB byte integrity (SHA-256 + archive CRC32)

**Session:** `20261106T1358Z-T5-chat-obb-fullsha-7e39`; origin `chat`; issue `INTEGRATION-001`; only writable branch `feature/android-native-port`.

## Fixed original input and test boundary

- Original owner-tested [GitHub Actions source run 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source `e9c358eda01785b65e4eb14f18723da426635628`. This is not a newly rebuilt Android deliverable from current branch.
- Immutable original GitHub delivery artifact `13441227298` and signed output checkpoint `13441766832`. Both artifact IDs, names, full ZIP byte lengths, provider digest and source run are authenticated from GitHub metadata before reading any original bytes.
- The original `delivery.json` inside the delivery ZIP declares `main.89.com.alwansan.raft.androidtest.obb` **2,301,256,312 bytes**, **3 delivery transport parts**, and the exact full SHA-256 for the logical OBB. The signer checkpoint outer ZIP contains the full main OBB as one `ZIP_STORED` member, whose CRC32 comes from the outer central directory. This checkpoint member was previously shown to have a genuine nested 39-entry ZIP structure and all matching local headers ([CI42224062207](https://github.com/alwansan/raf/actions/runs/42224062207)).
- Independent verified original signed APK [CI42228262902](https://github.com/alwansan/raf/actions/runs/42228262902) proved entire APK 672,853,870-byte SHA-256 against the same original delivery manifest, real binary manifest package/versionCode 89, and `apksigner` v1/v2 integrity. That APK result does **not** automatically authenticate the OBB.

## Exact method

- New T5-owned source `scripts/t5_verify_real_signed_obb.py`, `tests/test_t5_verify_real_signed_obb.py`, isolated `.github/workflows/raft-t5-real-signed-obb-attestation.yml`.
- Source pins immutable owner artifacts and checks the source `delivery.json` contract, full 64-hex original OBB SHA claim and exact logical size; verifies outer ZIP local header is STORED, matches index, and reads a bounded offset into that precise member only.
- Processes each actual byte in chunks of no more than 4 MiB through strict HTTP **206 Content-Range**, computes incremental `hashlib.sha256()` and `zlib.crc32()`, comparing whole-message SHA to original delivery claim and CRC to independently indexed checkpoint. **No game assets written to disk, committed, uploaded or returned.** The raw SAS URL/token, original asset bytes and original private resource names are absent from results and logs.
- Hard cap **2,400,000,000** OBB-range data bytes plus at most 8 MiB of two envelopes' metadata. HTTP 200/unbounded download, changed immutable artifact source/size/digest, short chunk, CRC conflict or SHA conflict is **BLOCKED**, never an automatic success. A ZIP archive structural CRC is not a cryptographic signature; the full SHA reference originates in the same old source delivery artifact, not an independently publisher-signed manifest.

## Actual test state

- [GitHub Actions CI42230326050](https://github.com/alwansan/raf/actions/runs/42230326050), job `127934255743`, exact source `867b332be6782777fc06810bb696ff20fc6e19ca`.
- **9/9 synthetic unit-test cases** passed (correct positive hash/CRC; altered same-size bytes; wrong SHA; bad CRC; truncated range; size/cap and bad format).
- **Live real source OBB read: COMPLETED SUCCESS.** [CI42230326050](https://github.com/alwansan/raf/actions/runs/42230326050), job `127934255743`, exact source `867b332be6782777fc06810bb696ff20fc6e19ca`: **9/9 source-free Python tests** and entire authentic original **2,301,256,312-byte** signed main OBB read. SHA-256 full 64-character digest equals actual original delivery manifest claim (**safe printed digest prefix `660b6c0909ae`**). Independently computed CRC32 across all bytes equals its STORED ZIP checkpoint central-directory CRC32. **549 HTTP 206 data requests**, plus original delivery range metadata **3,275 bytes** and signed checkpoint range metadata **255 bytes**. No raw original OBB was saved/uploaded; status includes `unity_original_obb_guid_verified=false` and `actual_android_obb_mount_verified=false`.

## Limits and next decision

Even a positive complete OBB SHA would **not** prove an Android mounted OBB from `/Android/obb`, embedded Unity `data.unity3d` GUID, FMOD event playback, shader/water/FFT/color parity, or readiness of a new 2026-11-06 build. The owner confirmed world/save/reentry on the **old signed package**, not current active T1–T4 changes. Game readiness remains `NOT_READY 0/3`.

**Next:** inspect the prior owner device warning `OBB GUID` against the original package path and the Unity player-consumed OBB internal data; source and on-device access still require separate tests. Compare installed-file hashes to the now SHA-authenticated original APK and OBB if device proof is available, then assess shader/water performance after T1–T3 integration. Do not treat an authenticated old delivery as a current-branch release.
