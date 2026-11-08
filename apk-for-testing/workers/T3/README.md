<!-- OWNER_SHARED_MINI_LAB_20261108 -->
> **المختبر الموحد هو المرجع الحالي:** لا تطلب من المالك تثبيت APK هذا العامل بشكل منفصل. التجربة الجديدة داخل [تطبيق T1–T5 الواحد](../../TEST_CENTER.md)، [الحزمة الواحدة](../../unified/pack/team-testpack.json)، [سياسة التعاون](../../UNIFIED_LAB_POLICY_AR.md)، [صف جاهزية بناء Mini المشترك](../../SHARED_BUILD_READINESS.md). احتفظ بروابط APK القديمة وأدلّتها أدناه للأرشفة فقط. يمكن أن يحتاج العامل تغيير Java/renderer تحت unified، ولا يبدأ بناء مستقل؛ T5 ينسّق واحداً عند حاجة عامل واحد مثبتة.

# T3 — GLES3 Material / Texture / Particle / Fire mini lab

**مسؤول النطاق:** T3 · RENDER-002 · Android 15 owner device. **الحالة: READY_TO_TEST / DEVICE_PENDING**. هذه تجربة GPU اصطناعية مستقلة، وليست إعادة تشغيل شيدرات أو أصول Raft أو إثبات إصلاح ألوانها.

## APK مثبت الوجود

- App: **T3 GLES Material Lab**, package `com.alwansan.raft.lab.t3.gles`.
- Version: `0.1.0-t3-gles`, versionCode `1`; compileSdk/targetSdk 35; minSdk 26; GLES 3 required.
- APK size: **20,425 bytes**. SHA256 **`c6396bc89548eeb55fc85d354a47a5fa77b98dfb7a79218af2dbc2a902615078`** (checked after extracting actual Actions artifact).
- Built source SHA: `a4578ff4cd7f7d7928038abdb1d076d514096da8`. Source commit introducing lab: `1147eca961eddd2dd46edae8c7b8771bffba72fc`.
- [Successful Actions run 42496427649](https://github.com/alwansan/raf/actions/runs/42496427649) — **SUCCESS**, [artifact t3-gles-material-lab-a4578ff4...](https://api.github.com/repos/alwansan/raf/actions/artifacts/13623309536/zip) is a **ZIP containing the real signed debug APK**, uploaded 2026-11-08 15:46 UTC; expiry **2026-11-15 15:46 UTC**, size of artifact ZIP 17,532 bytes. API download may require GitHub authentication; normal Actions run page provides Artifact download in GitHub UI.
- First [CI 42496333650](https://github.com/alwansan/raf/actions/runs/42496333650) failed before build at obsolete Android SDK `sdkmanager tools` step, resolved in `a4578ff4` by using installed platform/build-tools. Do not interpret this infrastructure failure as a shader/game failure.
- APK remains independently installable and does not share the installed Raft package or private storage. Debug signature may change across lab rebuilds; uninstall **only this T3 lab** if needed for subsequent versions.

## Cases, owner actions, and expected results

Launch app, choose each test and take screenshots of **CASE02–CASE05**. On every case use PASS/FAIL/UNEXPECTED with a short observation; export logs using **Export logs** and send the JSONL together with screenshots. The test is entirely offline and does not require game files.

| Case | Action | Expected |
|---|---|---|
| CASE01 | Inspect red/green/blue fields. | Three separate solid RGB regions; GPU renderer/version in logs. |
| CASE02 | Inspect interpolated quad at corners and center. | Four-corner RGB/white gradient, not uniformly white. |
| CASE03 | Inspect tinted transparent smoke quad over blue. | Background remains visible through red overlay, not opaque square. |
| CASE04 | Compare two panels using correct straight vs premultiplied blending. | Both panels visually similar; large mismatch needs log/screenshot. |
| CASE05 | Compare UNORM gray (left) against sRGB-decoded gray (right). | sRGB half perceptibly darker; `pixel_rgba` logs present. |
| CASE06 | Trigger deliberately malformed GLSL and review exported JSONL. | `negative_control: PASS invalid shader rejected`; valid fallback still draws. |

For each case the diagnostic logs include `case_start`, pixel samples, `render` GL error, and `case_result` (manual classification). Startup records API/device/ABI. GLES renderer/vendor/version/GLSL and compile/link failures are recorded from real GLES callbacks. Pixel samples are read from the displayed GL surface but **not compared against original Raft GPU reference pixels**. This is a color/alpha/driver differential; it is neither a Unity shader import test nor a real Raft particle-material binding comparison.

## Safe testpack import and logs

- [Six-case declarative testpack](testpack.json), schema v1, type `note` only; optional import via **Import JSON** Android SAF file picker. It changes text instructions only and cannot execute shader/dex/so/script. The six renderer cases are embedded in the APK.
- Persistent app-private log: `getFilesDir()/sessions/events-<session>.jsonl`. Tap **Export logs** to write a copy using MediaStore at `/storage/emulated/0/Download/Games/cl/test/t3-gles-material-<session>/`. No root or all-files access is requested.
- Expected owner feedback: case grades and notes, screenshots CASE02–CASE05, exported JSONL containing `gles_context`, `pixel_rgba`, `render`, `case_result`; if CASE06 negative control unexpectedly compiles, include the exact JSONL.
- **Do not delete the Raft game or any original save.** Compare only with screenshots tied to an authenticated Raft APK/session (owner 2026-11-08 feedback), not mixed releases.
- If generic GLES controls pass but the game stays white/square, prioritize **real Unity Material→Shader→Texture/keywords/blend/sRGB/variant binding** versus original, rather than declaring GPU or Raft fixed. If controls fail, inspect GLES errors/device behavior and compare with the full game under a reproducible scenario.

## Evidence status / next

- Source built and signed: **SUCCESS 42496427649**, APK identity/hash independently verified. Device results: **NOT_TESTED**.
- No game-resource/.meta change, no full Raft XAPK request, no 5/5 vote, no READY claim.
- Follow-up T3 authentic path remains the ParticleSystemRenderer → Material → Shader → Texture/keywords/alpha comparison on authenticated ZIP2 and actual staged export. Scheduled 20261108T1529Z T3 negative fileID audit change has not yet been CI-tested; do not cite earlier 40/40 as verification of that later patch.
