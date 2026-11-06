# T5 — authenticated GitHub Actions ZIP envelope range inspection (original Android build)

- **Session** `20261106T1301Z-T5-chat-artifact-range-probe-f9c2`; origin `chat`; issue `INTEGRATION-001`. Writable branch `feature/android-native-port` only.
- **Real source**: [owner-tested original native build run 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), source SHA `e9c358eda01785b65e4eb14f18723da426635628`; confirmed by pinned artifact source metadata. Owner's actual successful world/save/exit/re-entry remains linked **only** to that prior build, not the current branch.
- **Real source-only HTTP-range CI**: [42222494746](https://github.com/alwansan/raf/actions/runs/42222494746), job `127907699077`, source `edce82b5e9f93ef73fed6dcd4cb85876b960aa0e`, **COMPLETED SUCCESS**. **11/11** Python source-free tests and actual authenticated GitHub artifact metadata + real ZIP central directory, plus bounded small `delivery.json` member. No giant ZIP downloaded, original game bytes or private redirect URLs emitted.
- **Artifact provenance**: original delivery id `13441227298`, ZIP bytes `5,948,243,524`, GitHub metadata digest `sha256:29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6`; signed checkpoint id `13441766832`, ZIP bytes `2,974,110,506`, metadata digest `sha256:0e99e82c44af0fa21f613515ca0cb8eee2c04aa7911e9a001aabd1abdcde16bd`. Both checked `expired=false`; these SHA digests remain provider **claims about full envelope**, not locally full-stream verified hashes.
- **Actual bounded read**: delivery archive **12 central members**, **7 HTTP 206 requests / 3,275 bytes**; signed checkpoint **2 central members**, **3 HTTP 206 requests / 193 bytes**. Total **3,468 byte-range data bytes**, vs ~8.92 GB total full envelopes. Ranged response Content-Range checked against expected archive byte size, no fallback to unbounded 200/full download.

## New concrete source data from actual envelope bytes

The original `delivery.json` was actually read and parsed (not guessed from artifact name) and declares package `com.alwansan.raft.androidtest`, **versionCode `89`** (not the separate synthetic fixture version `86`), schema `1`, and three logical outputs:

| Logical output | Declared inner file bytes | Number of declared transfer parts |
|---|---:|---:|
| APK | 672,853,870 | 1 |
| main OBB | 2,301,256,312 | 3 |
| XAPK | 2,974,111,434 | 3 |

Outer delivery ZIP central inventory was **1 APK, 3 OBB transport parts, 3 XAPK transport parts, 1 delivery.json, 4 other metadata members**. The checkpoint ZIP central inventory was **1 APK, 1 complete main OBB, 0 XAPK, 0 delivery.json**. The checkpoint central directory advertises inner uncompressed **APK 672,853,870 bytes** and **OBB 2,301,256,312 bytes**, numerically agreeing with actual delivery.json logical output sizes. This establishes **real file presence and metadata size coherence**, not individual ZIP-member SHA/authenticity.

## Reproducible bounded tool and acceptance boundary

- `scripts/t5_probe_github_artifact_zip_range.py`, `tests/test_t5_probe_github_artifact_zip_range.py`, `.github/workflows/raft-t5-real-delivery-zip-range.yml` are isolated T5-owned source-only artifacts. The script validates immutable artifact metadata identity/digest/run link, uses the Actions API redirect to trusted Azure blob host, then issues only strict HTTP 206 Content-Range requests with maximum **4 MiB per entire archive** and 512-KiB chunk caps. It rejects dangerous ZIP paths/symlinks/encryption and duplicates, rejects oversized metadata, bounds members and delivery.json extraction, sanitizes all reported fields. ZIP inspection is read-only; a failed range is **blocked**, never a complete fallback.
- This does **not** compute the signed APK/OBB byte-content SHA256, authenticate the `delivery.json` document cryptographically, verify APK signature/certificate, inspect actual nested APK/OBB Unity resource ZIP payloads, test real XAPK assembly, validate original OBB GUID or phone mount, or rebuild a newer Raft. In particular, an inner file size from the outer central index is **not** proof its compressed stream is intact.
- **Next**: determine if the checkpoint's outer APK and OBB are `ZIP_STORED`; if yes, use further bounded HTTP byte ranges into the actual nested APK/OBB ZIP **central directories** (without reading the 3GB content), count Android ARM64 libraries and original Unity resource entries. Explicitly keep limits on unavailable inner digest/signature and device acceptance. Only then plan an authorized full signed APK/OBB stream and signer/versionCode check.
- T1/T2/T3/T4 files, shared Unity build workflows, original game assets and phone remain unchanged. Original WATER-001/FFT, RENDER-002 shader/color/effects and complete phone acceptance **OPEN; NOT_READY 0/3**.
