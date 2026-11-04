# LogRaft diagnostic correctness bundle — 2026-11-04

**Write scope:** only `lograf`; game branch `feature/android-native-port` was inspected read-only at `6b60c35e845a3bc8e559a7df7e408363032697cb`. No private user logs were committed.

## Device evidence: Poco F5 Pro / Android 15

User-provided 0.6.82 session `20261104-210832-360` contained 3,287,278 game-UID lines, 121,496 `Graphics.Blit` invalid-pass roots, 17,178 `Invalid kernelIndex` roots, and 2 `Unable to load GUID` messages for a `patch.86...obb` path. Raw lines show matching-timestamp `UltimateWater.Internal.Dx11FFT.ComputeFFT` stack frames after the kernel roots. The prior one-line classifier therefore called them `other_invalid_compute_kernel`. The earlier 17:35 session also contains an `FMODUnity.RuntimeManager.Initialize` frame for a `NullReferenceException` root that had not been classified as FMOD.

Local writer for the long session reported 10,514 written / 10,514 accepted batches and zero **observed local writer failures**, not proof against Android's own Logcat buffer rollover or Shizuku loss. SurfaceFlinger provided 9 valid presented-FPS samples of 128; unavailable FPS does not establish a Unity freeze.

## Changes in this bundle

1. **FFT stack correlation.** Correlate the exact Logcat timestamp/UID/PID/TID/priority prefix over at most 24 lines / 1.5 seconds; count one water FFT error per matched root, and uncorrelated roots in the generic compute category. Retain original raw lines byte-for-byte. A 17,178-event synthetic flood test verifies exact classification, and a different-thread control prevents false attribution.
2. **FMOD causality.** Correlate generic Unity `NullReferenceException` only to same-event `FMODUnity.RuntimeManager.Initialize` stacks. Unrelated null references are not misreported as FMOD. Direct initialization failures and missing-event patterns remain covered.
3. **OBB/GUID.** Count `obb_guid_load_failed`, `obb_file_missing`, `obb_access_denied`, and `other_asset_guid_load_failed` separately; successful OBB path mentions are not errors. This observes emitted Logcat text only; it does not read the expansion package.
4. **PSS sample alignment.** Compare a cached PSS candidate against a bracketed RSS reference collected before and after that same `dumpsys meminfo` command. Export `pss_reference_rss_kb`, `pss_collected_unix_ms`, `pss_sample_age_ms`, and explicit `validated_recent` / `validated_cached` / rejection quality. Still reject unexplained source mismatch; no fake memory values.
5. **Honest throughput and stop-time totals.** Distinguish interval `game_log_lines_per_second` from cumulative `game_log_lines_session_average_per_second`. Add `final_error_category_breakdown` and `final_game_log_lines` to session summary using last stop-time remote evidence, instead of interpreting the final three-second sample as complete.

## Game development cross-check, not a game modification

Authentic original `zip2` assets are being verified and staged for FFT and FMOD bank restoration. Latest original water-shader census has Spectrum 7 passes / Foam 2; user's 0.6.82 logs still show runtime 1-pass water materials and missing compute kernels. That mismatch cannot be repaired by a logger. A published experimental game build `android-early-test-41812889049-1` contains signed APK and split OBB/XAPK; build success is not phone success. `docs/APK_BUILD_READINESS.md` still indicates NOT_READY and water/render/FFT gates open. Package-based UID filtering remains `com.alwansan.raft.androidtest`.

## Testing and limitations

CI runs `python3 scripts/test_lograf_v06.py`, `bash scripts/test_lograf_diagnostics.sh` (JVM regression), and Gradle signing verification. Device test is still required for Shizuku/Binder interruption, long sessions, actual memory quality, FPS data availability and full APK installation. Raw logs and segmented storage are retained; no auto uploads, private game data access, developer secrets, guessed FPS, or game branch changes are introduced. Device functionality must not be asserted from CI alone.

## CI and release evidence (confirmed)

- Code commit: `136e52d8ac0f0a2c71b03e0ee522f0f58f9e9e06`.
- GitHub Actions: [41887820451](https://github.com/alwansan/raf/actions/runs/41887820451), **COMPLETED SUCCESS**. Structural recorder checks, actual JVM diagnostic regression (including 17,178 synthetic FFT events), Gradle release build, signature/certificate matching, artifact upload, and Release publication all succeeded.
- Release: [lograf-83](https://github.com/alwansan/raf/releases/tag/lograf-83). Signed asset: `LogRaft-signed.apk` (157,508 bytes), plus SHA-256 sidecar. Exact package identity remains `com.alwansan.lograf`; build sets versionCode `1083` and versionName `0.6.83`.
- Pinned public test certificate SHA-256: `bdb27cfad1fd9a6ac14bd47317206ce4df462040f45ddb1fdbb66a0974043149`. This is **the signing certificate fingerprint**, not the APK-file hash.
- Separate local read-only raw-log correlation check: 17,192 root `Invalid kernelIndex` lines across the complete 0.6.82 raw segments, **all 17,192** had a same-event water FFT stack frame in the next 24 lines. The previous metric sample reported 17,178 because it preceded Stop; the new final category summary is designed to include tail observations.
- **Not yet device tested**: no claim that LogRaft 0.6.83 fixes the game's shader, OBB or FMOD faults, or that SurfaceFlinger FPS is always available.
