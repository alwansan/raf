# T5 — installed-version main OBB ZIP first-byte runtime evidence hook

Issue: **INTEGRATION-001** · T5 chat session: `20261106T1645Z-T5-chat-installed-obb-read-e7c4` · permitted branch: `feature/android-native-port` · 2026-11-06T17:00:24.850Z.

## Why the experiment matters

Old owner-tested run [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) was playable and the original signed main OBB's entire SHA-256/CRC32 was authenticated by [CI42230326050](https://github.com/alwansan/raf/actions/runs/42230326050). [CI42248117179](https://github.com/alwansan/raf/actions/runs/42248117179) independently established 5/5 original FMOD bank and 29/29 Haptics WAV Android jar paths. Those source-archive proofs **do not** establish that the same-version `main.<versionCode>.<package>.obb` is present and readable *on the installed POCO F5 Pro*, or that Unity's engine actually opens resources from it.

## Integrated bounded source change

- `android-port/Runtime/Platform/AndroidExpansionArchiveProbe.cs` is a pure .NET, fail-open diagnostic, given **getObbDir, installed package and PackageInfo long versionCode**. It selects ONLY the exact `main.<installed-version>.<package>.obb`; reports a stale-only OBB without selecting it, rejects invalid package components, empty/archive-link/ZIP-failure cases, and does not enumerate or log absolute paths.
- In the matching archive it seeks the central directory, counts nonempty `assets/bin/Data/` Unity entries and the five expected FMOD bank paths, then reads **exactly one uncompressed byte** from one nonempty Unity ZIP entry. The sample does NOT compute SHA, extract a resource, load a scene, allocate a full game asset, or log original resource bytes/names. Potential failures produce a recoverable status and exception **type only**.
- `AndroidTestDiagnostics.StartDiagnostics()` calls the read-only check once and writes `storage / obb.unity_zip_read_sample` with version, archive size/counts, one-byte read status and `installed_obb_sha_verified=false; unity_engine_resource_load_verified=false; gpu_pixels_verified=false`. All JNI/ZIP exceptions are caught and logged as unavailable, without interrupting scene or audio initialization.
- The main real native Unity workflow copies Platform C# using an **explicit filename loop**. Its list was extended to include exactly `AndroidExpansionArchiveProbe.cs` alongside `AndroidTestDiagnostics.cs`; this is necessary to avoid a missing-type Unity Android compile failure.
- Synthetic .NET executable project is `android-port/Tests/ExpansionArchiveProbe/` and a new **isolated**, no-LFS, no-full-Unity workflow is `.github/workflows/raft-t5-installed-obb-read-probe.yml`. The CI additionally asserts the actual native Unity import script contains the helper exactly once.

## Evidence and honest boundaries

1. Initial workflow [42256256534](https://github.com/alwansan/raf/actions/runs/42256256534) was invalid YAML before starting jobs, due a plain YAML `run:` scalar with a colon-space inside a shell-quoted echo; fixed to a YAML block scalar. It was **not** a C# or OBB failure.
2. Intermediate [CI42256468606](https://github.com/alwansan/raf/actions/runs/42256468606) **SUCCESS**, 24/24 synthetic ZIP checks and managed Platform build, but lacked proof that the newly created file was in the Unity import copy list. The omission was discovered by reading the real native workflow and was repaired before final success.
3. Final [CI42257103707](https://github.com/alwansan/raf/actions/runs/42257103707), job `128027083765`, immutable source `c9f55dc103ddc817315e44ddf9ee34449f35ca62`, **COMPLETED SUCCESS**: `T5_UNITY_IMPORT_COPY_PROBE status=PASS exact_file_once=true`; `T5_INSTALLED_OBB_READ_PROBE synthetic_checks=24 status=PASS device_verified=false`; managed platform project **Build succeeded, 0 errors**. Remaining project warnings are unrelated existing nullable/unused field warnings; the newly introduced probe nullable warning was removed.
4. No native ARM64 Unity player, new signed APK, on-device OBB file read, full device SHA, original engine asset load, FFT kernel, water render/pixel or gameplay acceptance was run by this CI. The ZIP first-byte probe is **not** a Unity engine read proof. Installed APK-only deliveries may legitimately have no main OBB, so `matching_obb_missing` must be interpreted in the context of the specific split delivery.

Next: produce a new device test candidate when team P0 readiness permits, then inspect actual `obb.unity_zip_read_sample`, `fmod.bank_root`, the `main.89` installed path/version and actual Unity resource open logs from the **same device run**. Do not use the old signed artifact metadata to infer a new candidate's device mount. WATER-001 and RENDER-002 remain OPEN; **NOT_READY 0/3**.

No private original archive bytes, shaders, secrets, gameplay source, active Unity native request, audio behavior, Settings or deferred touch/layout were changed.
