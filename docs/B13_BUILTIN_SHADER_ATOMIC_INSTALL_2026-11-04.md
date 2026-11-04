# B13 — RENDER-002 atomic built-in shader source staging (2026-11-04)

Agent B13; session `20261104T2247Z-B13-builtin-atomic`; only writable branch `feature/android-native-port`. Scope: the **existing** production built-in shader restorer, not shaders/FFT/materials themselves.

## Reproduced risk and source fix

The production `scripts/restore_builtin_shaders.py` previously replaced an existing authored/exported `.shader` with `Path.write_bytes(content)`. That truncates the original before finishing the new write, so an I/O exception can leave a partially written program until a separate in-place rollback succeeds. It also trusted a source snapshot made before creating backup/dependency files, without re-reading source bytes at the publication boundary. A concurrent worker or exporter change could be clobbered.

[Source correction 20c94103](https://github.com/alwansan/raf/commit/20c94103edc9d10352560d473656f7004208268b):

- Save and read back original ShaderLab and `.meta` backup bytes before changing source. Incomplete backup aborts and deletes the disposable incomplete backup; original source remains untouched.
- For each replacement, compare current original source and metadata to the exact preflight byte snapshot. Reject changed source instead of overwriting it. This is a bounded prepublication race check, not an OS lock against every concurrent mutation.
- Write new source to an exclusive, same-directory temporary file; flush, fsync and preserve mode; atomically `os.replace` rather than truncate in place. Remove temporary files on error.
- Track only **successfully published** replacements. When a later source fails, restore prior source bytes through the same atomic path; refuse to overwrite a source modified again after publication and retain external backup for manual recovery. Existing dependency cleanup remains.
- No original `.meta`/GUID modifications, no invented shader programs, and no changes to the existing exact-identity engine-ownership gate, material assignment, audio, Settings, world/.rgd, deferred input or build request.

## Verification

[Test commit 253ea8e](https://github.com/alwansan/raf/commit/253ea8e536829b3c57a698cb68e09490d034d0a3) adds four injected-failure tests alongside ten existing source-free tests:
1. Forced atomic rename failure cannot truncate the original shader; original/meta backup intact, no temporary or added license left.
2. External source mutation after backup but before publication is detected and **not overwritten**.
3. Failure publishing the second shader rolls back the first shader to exact original bytes, preserving backups.
4. A silently corrupted saved backup is rejected before any original source changes.

[Isolated B13 Actions 41928703661](https://github.com/alwansan/raf/actions/runs/41928703661) **COMPLETED SUCCESS** on workflow source `0865169bbc2bfb38d3b4eb297e893ecbf9f6f74f`: actual job `source-atomicity`, **14/14 tests PASS**; compilation check PASS. [Workflow](../.github/workflows/raft-b13-builtin-atomic.yml) uses a bounded 8-minute Ubuntu-24.04 source-only run, no LFS/download of Raft originals, no Unity, no APK, independent concurrency and `cancel-in-progress:false`.

## Limits / nonclaims

The last observed actual phone game remains [Raft Android APK86](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1), built from older immutable source; CL main HEAD `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29` has no new phone evidence for these commits. The earlier W1 native [41741108965](https://github.com/alwansan/raf/actions/runs/41741108965) failed before Unity at 0/142 loose built-in shader matches; the subsequent distinct source-authenticated engine-ownership check is **not** bypassed by this work. Original water ShaderLab/FFT compiled identity, exported Material source→GUID lineage, visual colors, new world save and live Adreno pixels remain unverified.

This is production **source-staging transaction hardening**, not real water restoration, new shader program or phone graphics fix. `RENDER-002`, `WATER-001`, `LOCAL-005` stay OPEN and overall game `NOT_READY` with 0/3 full independent reviews. Next useful work: reproduce authenticated same-instance exporter identity and original program binding for water/ShaderLab/FFT, or prove original world create-save-reopen with new binary in a coordinated trial. Do not request an equivalent full build just for this fix.
