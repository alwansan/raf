# CLog — Cinemana Pro dedicated Android diagnostic companion

Branch: `clog`, derived from `lograf` at 6d268476dc5aa64f379ae7ad7deb09097872a1b1. This branch is separate from both the `lograf` logger and CP game project.

## Target confirmed from the actual CP branch
- Read-only source: `alwansan/CP`, `feature/stable-core-ui-performance`, head 39c23fbf3a43181a6a372ba6bece32444e9b8687.
- Android package: **`com.cinemana.pro`**, APK reconstructed from Smali/DEX.
- Process: main app; `com.cinemana.pro:filedownloader` for `com.liulishuo.filedownloader.services.FileDownloadService$SeparateProcessService`.
- Primary UI: HomeActivity, DownloadsActivity, VideoPlayerActivity, SettingsActivity; splash and profile/details fragments.
- MKV pipeline: `DownloadRepair129`, `RecoveryCapsule`, `MkvReconciler`, `Queue110`, `MkvExporter`, `MkvPriority325`, `Lease115`, `MkvManifestStore` / Room database, FFmpeg single-worker mux, subtitle checks and durable queue receipts.
- Risks: E42/E49 stalled `.mkv.cnm115-UUID.part`, repeated queue enqueues without corresponding export start, state-write failures, `MkvCancel262.clearCurrent` liveness, startup ART VerifyError, background ANRs, high CPU/threads, dropped frames, player return-to-details navigation, new-episode notifications.
- Existing app telemetry in `/storage/emulated/0/Cinemana/work/log` includes `load_diagnostics.main.jsonl`, `load_diagnostics.filedownloader.jsonl`, `ui_performance.jsonl`, `downloads.log`, `.mkv_export.log`, `download_repair_actions.log`, `download_repair_unresolved.log`, `player_diagnostics.log`, `mkv_player_resolver.log`, `mkv_subtitle_catalog.log`, `diagnostics.log`, `ui95.log`, per-episode .mkv.log files. Files can be private and contain signed URLs.

## Goals of CLog
- Use Shizuku to capture the *target UID* across `main`, `system`, `events` and `crash` Logcat buffers; separately filter system messages referencing `com.cinemana.pro` or its actual process PIDs.
- Sample CPU, RSS, threads, PSS, I/O, memory pressure, GPU/CPU frequencies, battery, and thermal data without claiming unavailable counters are zero.
- Monitor both main and `:filedownloader` process, not just the UI PID.
- Count critical known markers and capture ANR, VerifyError, Room, FileDownloader, MKV, FFmpeg, player/codec, notification and graphics indicators in a compact separate metrics stream. Preserve full raw logcat.
- Optionally let the user choose the *existing work/log folder* using Android Storage Access Framework, to copy logs on an independent background thread. Never alter Cinemana files or clear stuck downloads.
- Write each session into the user's selected output folder, segment indefinitely without deleting earlier segments, then share a ZIP on explicit user action.

## Privacy and limitations
- CLog does **not** require ROOT; it requires an active Shizuku service. Shizuku and Android 15/vendor restrictions can block some counters/log buffers.
- Do not automatically upload logs or export them to a public service. They may contain URLs, account details, video titles, file paths or authentication material. Review before sharing.
- User-provided access to a work/log folder is *read only*. This is not permission to delete/change MP4, subtitle, MKV `.part`, JSON, Room or app settings.
- A third-party logger **cannot see internal Java method calls, database transactions, FPS or network content not emitted to logs**. For deep diagnosis, CP's own instrumentation and its persisted log files remain necessary.
- Android process termination, including `:filedownloader`, is **not** automatically a confirmed crash. Treat exit-history evidence as unavailable until verified on device.
- CPU/GPU thermal samples and external presented FPS estimates are indicators, not proof of the cause of UI freezes.

## CP documents read to design this variant
- `docs/stable-core/WORK_SESSION_HANDOFF.md` (historical checkpoint with PATCH330 link)
- `docs/stable-core/PATCH330_WORKER_CLEANUP_RESILIENCE.md`
- `docs/stable-core/PATCH329_RECOVERED_QUEUE_RESILIENCE.md`
- `docs/stable-core/PATCH328_MKV_WORKER_WATCHDOG.md`
- `docs/stable-core/PATCH308_THREAD_CPU_DIAGNOSTICS.md`, `PATCH309_CPU_PLAYER_ATTRIBUTION.md`
- `Cinemana_PATCH252_Project/DIAGNOSTIC_BUILD_AR.md` (player, H.264 10-bit and surface diagnostics)
- `Cinemana_PATCH252_Project/app/AndroidManifest.xml` (verified actual app ID/services)

Build and signing use GitHub Actions on **only** `clog`, independent from LogRaft's workflow. The logger is installed as `com.alwansan.clog`, so LogRaft and CLog can coexist without conflicting app data.
