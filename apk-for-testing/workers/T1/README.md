<!-- OWNER_SHARED_MINI_LAB_20261108 -->
> **المختبر الموحد هو المرجع الحالي:** لا تطلب من المالك تثبيت APK هذا العامل بشكل منفصل. التجربة الجديدة داخل [تطبيق T1–T5 الواحد](../../TEST_CENTER.md)، [الحزمة الواحدة](../../unified/pack/team-testpack.json)، [سياسة التعاون](../../UNIFIED_LAB_POLICY_AR.md)، [صف جاهزية بناء Mini المشترك](../../SHARED_BUILD_READINESS.md). احتفظ بروابط APK القديمة وأدلّتها أدناه للأرشفة فقط. يمكن أن يحتاج العامل تغيير Java/renderer تحت unified، ولا يبدأ بناء مستقل؛ T5 ينسّق واحداً عند حاجة عامل واحد مثبتة.

# T1 — Android GPU Compute mini lab (WATER-001)

**Worker:** T1 · **Scope:** actual Android OpenGL ES 3.1 synthetic Compute/SSBO capability and readback; *not* original Raft/Unity shader recovery.

## Current status: READY_TO_TEST — one real APK built and uploaded (Android device results pending)

**Latest verified APK: T1 v0.1.1-t1-export-path (8 Nov 2026)**

- **Download:** [GitHub Actions Artifact #13624141881](https://github.com/alwansan/raf/actions/runs/42497767712/artifacts/13624141881), ZIP with `app-debug.apk` and `mini-lab-sha256.txt`.
- **Build:** [run 42497767712](https://github.com/alwansan/raf/actions/runs/42497767712) — **SUCCESS**; `assembleDebug -Pworker=T1`, nonempty APK, SHA256 and uploaded archive verified.
- **Source SHA:** `37182f0e9d38c0c38f3e78e7e5c21463eeaac8d9`.
- **Package / version:** `com.alwansan.raft.lab.t1`, `versionCode=2`, `versionName=0.1.1-t1-export-path`.
- **APK SHA256:** `d177634c7ee7d71117005000fa904db03e825a43ba63dbe921ddf43cc077d0b7`.
- **Artifact ZIP:** 35,583 bytes; expires `2026-11-15T16:03:00Z` (7 days).
- **Log export (latest owner requirement):** `/storage/emulated/0/Download/Games/cl/raft log/test/t1-builtin-t1-gles31-<session>/`. Events include actual `app_version` and `app_version_code`.
- **Expected on Adreno730:** T1-01..04 should all PASS if genuine ES3.1 compute/SSBO are functional. Any FAIL/UNEXPECTED plus logs/screenshots is diagnostic; a PASS cannot prove Unity FindKernel or water restoration.

**Previous build retained for provenance (superseded, do not install for new tests):** v0.1.0, source `2980d378e37a678feedc3584530bde71212fbd9f`, [run 42497238594](https://github.com/alwansan/raf/actions/runs/42497238594), [artifact 13624351093](https://github.com/alwansan/raf/actions/runs/42497238594/artifacts/13624351093), APK SHA256 `d87dc468ab39ea2ac67fe09fe1e02b34052c84f09ab3ad9bd8d22d24d18449a6`. Old APK exported to `Download/Games/cl/test`; superseded solely to meet latest explicit owner log path/version request.

- The built-in GPU Java source is `apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1ComputeProbe.java`.
- `MainActivity` installs it **only with** `-Pworker=T1`; all shader text is compiled into the APK, and user-imported testpacks cannot supply/execute shaders, scripts, dex or native code.
- Package when built: `com.alwansan.raft.lab.t1`, versionCode `2`, ephemeral debug signature; uninstall the earlier T1 lab before an incompatible debug-key upgrade, but **never uninstall Raft**.
- Main T1 paired FFT source-only workflow [42493143730](https://github.com/alwansan/raf/actions/runs/42493143730) is SUCCESS, but is **not** the mini APK build and does not constitute Android GPU evidence.
- Logs remain append-only inside app-private storage during the run; export via MediaStore to `/storage/emulated/0/Download/Games/cl/raft log/test/t1-builtin-t1-gles31-<session>/`. No root, all-files access, or Shizuku required.

## Four immutable CASEs (not configurable through imported files)

| Case | Goal | Expected / pass criterion |
| --- | --- | --- |
| `T1-01` | Actual ES context and compute limits | OpenGL ES >=3.1; max workgroup count X>=4, max local size X>=4, invocations >=4, no GL error; record vendor/renderer/GLSL version |
| `T1-02` | One compute dispatch + SSBO readback | 16 uints exactly `v[i] == i*3+7`; GL error zero, successful SSBO unmap |
| `T1-03` | Two compute dispatches + memory barrier | 16 uints exactly `v[i] == 2*(i+10)+1`, after `GL_SHADER_STORAGE_BARRIER_BIT`; no GL error |
| `T1-04` | Negative control / GPU compiler | Deliberately invalid built-in GLSL function fails compilation; a compiler accepting it is FAIL |

**Owner procedure after a verified APK is linked here:** install T1 mini lab beside Raft without touching any Raft save; open each `T1-01` ... `T1-04` and tap **Run selected T1 GPU CASE**; inspect observed status; mark PASS/FAIL/UNEXPECTED and note anomalies; use **Export logs**. Send exported `events-*.jsonl`, screenshot of failing case plus device GPU/GL strings. Negative and positive results are required; do not classify all cases PASS merely because the app opens.

## Evidence boundary and next diagnosis

The Nov 8 phone session `LogRaft-20261108-164850-270` reports **11,165** `water_fft_invalid_compute_kernel` and **74,359** `ultimate_water_invalid_pass` for that session only. These counters do not establish missing compute *hardware* vs missing imported Unity kernel or program. A PASS from this lab only shows baseline GLES 3.1 compute on the device; it **cannot** prove `ComputeShader.FindKernel`, `Dispatch`, source/asset recovery, Unity Vulkan, original FFT numeric parity, or Raft water rendering. Follow-up should add an authenticated original Unity compute test only after source mapping and permitted private asset handling, then integrate actual fix into Raft and verify the full game.

CI build uses scoped `.github/workflows/raft-t1-gles31-mini-lab.yml` triggered by a one-time `workers/T1/build-request.json`, because concurrent team commits prevented pinning the immediate parent of the *shared* workflow request. No T4/T2/T5 request or full game pipeline was overwritten. Historical failed T1 shared request gate runs [42496880833](https://github.com/alwansan/raf/actions/runs/42496880833) and [42497135091](https://github.com/alwansan/raf/actions/runs/42497135091) made no T1 APK and are preserved as failed attempts.
