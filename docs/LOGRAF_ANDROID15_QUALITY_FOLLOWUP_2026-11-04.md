# LogRaft Android 15 quality follow-up — 2026-11-04

**Scope:** `lograf` only. The game branch `feature/android-native-port` is read-only; current reviewed head `6b60c35e845a3bc8e559a7df7e408363032697cb`. Do not reproduce or publish raw owner logs.

## New evidence from the owner's 0.6.82 Poco F5 Pro capture

The 21:08 device session had 128 telemetry samples. **108 samples** labeled `rejected_pss_exceeds_rss` because Android `dumpsys meminfo <pid>` total PSS exceeded Linux `/proc/<pid>/status VmRSS`, sometimes by hundreds of MiB. The 0.6.83 change aligned collection times but still interpreted the two *different accounting domains* as directly comparable. Android meminfo can include vendor graphics/memtrack amounts not in process VmRSS, so excess alone does not establish a fabricated PSS. The value now remains available as an explicitly **Android-reported** PSS under `android_meminfo_reported_above_proc_rss` while `pss_validated_against_rss=false`; it is not a claim of Linux smaps PSS or physical GPU residency. Missing/invalid readings remain null. The separate `android_meminfo_total_pss_kb` retains source provenance and the session reports mismatch counts.

More than **1,250 Unity cursor RGBA32-format errors** appeared alongside missing MonoBehaviour script reference, duplicate EventSystem, `steam_api64` missing native library, and convex mesh polygon-limit errors. Five fixed-vocabulary categories now summarize these game-side observations without collecting private assets, mouse video, Steam data or scene contents. The raw game-UID Logcat is unchanged.

PID probe failures or temporarily inaccessible `/proc/<pid>/cmdline` are not confirmed game exits. Before this fix the sampler could emit `game_exited` and query a process exit history just because `currentPid()` had temporarily returned -1; the remote callback later relabeled the state, but the unnecessary exit-history query already occurred. A dedicated **UNKNOWN (-2)** sentinel preserves previous verified identity and no longer creates a false exit transition. Only a verified empty `pidof` result produces NOT_RUNNING (-1); actual Android exit-history reason is still not assumed without PID/time matches.

When SurfaceFlinger provides fewer than two present timestamps, `presented_fps_estimate` remains null (not zero) and `surface_latency_valid_timestamp_count` records how many timestamps Android returned. It does not create an FPS fallback, infer a Unity hang, or enable GPU profiling.

## Tests / CI criteria

- Existing recorder structural checks now enforce the unknown-vs-exit distinction, full framework PSS provenance, and SurfaceFlinger timestamp count.
- JVM tests cover cursor/script/EventSystem/Steam/convex message classification, negative-success controls, PSS accounting mismatch quality and PID probe tri-state, in addition to the existing 17,178 synthetic FFT event replay.
- Verify exact applicationId `com.alwansan.lograf`, unchanged repository test keystore `signing/lograf-public-test.p12`, automatic Actions versionCode bump, signed APK upload and release; distinguish successful CI from actual Poco F5 Pro runtime evidence.

**Remaining intrinsic limitations:** no external Android logger can observe private Unity FrameTimingManager, internal water/FFT shader object IDs or FMOD bank path resolution if the game emits no accessible Logcat markers. The game branch's original ZIP2 source restoration (FFT/water/materials/FM​​OD/OBB) and latest experimental APK+split OBB are separate work streams. Any new runtime test must report source/version and exact symptom, not imply game remediation from logger changes.

## Verified CI outcome — 4 November 2026

- Source commit: [`65602cf57e154de3b0eeb860d40c1dc0c671e3a3`](https://github.com/alwansan/raf/commit/65602cf57e154de3b0eeb860d40c1dc0c671e3a3).
- [GitHub Actions run `41890403277`](https://github.com/alwansan/raf/actions/runs/41890403277): **COMPLETED SUCCESS**, including original structural checks, actual JVM diagnostic regression with a synthetic 17,178-FFT-error replay, Android release Gradle build in 37 seconds, persistent test-keystore signature verification and release upload.
- Published signed artifact: [`lograf-84/LogRaft-signed.apk`](https://github.com/alwansan/raf/releases/download/lograf-84/LogRaft-signed.apk), 159,692 bytes. Version `0.6.84`, versionCode `1084`, applicationId `com.alwansan.lograf`. SHA-256 sidecar accompanies the APK.
- Certificate SHA-256 is `bdb27cfad1fd9a6ac14bd47317206ce4df462040f45ddb1fdbb66a0974043149` (same pinned public test signing certificate). This is not the APK file's content hash.
- **Device status:** No 0.6.84 phone test exists yet. This is software test/build evidence, not a claim that Raft's shaders, water, OBB or input are fixed. 0.6.82 metrics and logs were the diagnostic input.
