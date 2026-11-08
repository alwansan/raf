# T1 — Android GPU Compute mini lab (WATER-001)

**Worker:** T1 · **Scope:** actual Android OpenGL ES 3.1 synthetic Compute/SSBO capability and readback; *not* original Raft/Unity shader recovery.

## Current status: SOURCE_READY — no verified T1 APK yet

- The built-in GPU Java source is `apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1ComputeProbe.java`.
- `MainActivity` installs it **only with** `-Pworker=T1`; all shader text is compiled into the APK, and user-imported testpacks cannot supply/execute shaders, scripts, dex or native code.
- Android package when built: `com.alwansan.raft.lab.t1`, versionCode `1`, debug signature (per-run debug signing).
- **APK download / SHA256 / CI / immutable build source:** pending actual verified T1 build; do not test or invent a URL.
- Main T1 paired FFT source-only workflow [42493143730](https://github.com/alwansan/raf/actions/runs/42493143730) is SUCCESS, but is **not** the mini APK build and does not constitute Android GPU evidence.
- Logs remain append-only inside app-private storage during the run; export via MediaStore to `/storage/emulated/0/Download/Games/cl/test/t1-builtin-t1-gles31-<session>/`. No root, all-files access, or Shizuku required.

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

Do not launch an identical build during T4's running mini-lab; use isolated mini build request protocol after that run concludes.
