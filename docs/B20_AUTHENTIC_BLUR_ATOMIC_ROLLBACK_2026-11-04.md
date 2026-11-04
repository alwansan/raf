# B20 WATER-001 — authenticated original Blur installer atomic rollback

## Scope / reason

The existing native Unity staging workflow (the **B45 original Blur** step within `.github/workflows/raft-unity-editor-android-import.yml`) reconstructs and SHA-checks an original-derived two-pass ShaderLab candidate in private scratch, then installs it into a transient exported Unity project with the original asset GUID preserved. The prior installer used `Path.write_bytes(original)` for rollback after a candidate had been promoted: writing directly to the target can truncate the active exported shader if the rollback itself encounters an I/O failure.

This change addresses only transactional safety of the existing recovery path. It does NOT alter original candidate SHA/bytes, ShaderLab content, original .meta/GUID, game assets, Steam/world, audio, Settings or deferred touch.

## Code and provenance

- [B20 fix 9387b481](https://github.com/alwansan/raf/commit/9387b48176fc89aa99b0ebbd9aa2ad4666564515) replaces the former in-place rollback with same-directory fsynced temporary write and atomic `os.replace`. The previously verified external backup is retained on every post-promotion failure.
- During failure, B20 now checks the original shader and .meta after rollback; a failed rollback raises an explicit generic error rather than presenting a false restored-success result. Temporary rollback files are cleaned.
- [B20 tests 49f83ff](https://github.com/alwansan/raf/commit/49f83ff4203eb4b6f0680d6542c1943363080ada) add four synthetic success/failure-injection scenarios without private game data.
- [Isolated workflow 0059820](https://github.com/alwansan/raf/commit/0059820de984e4a0a31aec60cb7b11de913984e3) uses 4-minute standard Ubuntu runner, no Unity, LFS, original program, APK or device.

## Verification / limitations

- [B20 source-only CI 41927169542](https://github.com/alwansan/raf/actions/runs/41927169542): **SUCCESS** for B20 four injected-I/O tests and existing B45 synthetic installer regression at source `0059820de984e4a0a31aec60cb7b11de913984e3`.
- [B45 existing CI 41927095232](https://github.com/alwansan/raf/actions/runs/41927095232): **SUCCESS** on `9387b48176fc89aa99b0ebbd9aa2ad4666564515`.
- [Runner compatibility 41927169375](https://github.com/alwansan/raf/actions/runs/41927169375): **SUCCESS** on B20 workflow SHA.
- Rejected: non-atomic in-place restoration is sufficiently failure-safe. Repro test synthetically corrupts the promoted candidate then rejects an injected rollback rename, verifying that the pristine external backup survives and the failure is reported.
- **No real original Blur ShaderLab candidate installed in Unity in this test, no runtime pixels, no Adreno execution, no device or texture/FFT improvement demonstrated**. This is `SOURCE_FIXED` integration-safety hardening only; WATER-001, RENDER-002 and LOCAL-005 remain OPEN; NOT_READY, three full independent reviews 0/3.

## Next useful work

Use existing B45 original two-pass candidate and pinned ZIP2 source, B24 Foam, B18 FFT descriptors, and B30 runtime identity constraints to implement/validate actual original Spectrum/Foam/FFT ShaderLab and compute bindings through the transient Unity import, then compare pixels and real phone logs. No further source-only census is a substitute for GPU/device evidence.
