<!-- OWNER_SHARED_MINI_LAB_20261108 -->
> **المختبر الموحد هو المرجع الحالي:** لا تطلب من المالك تثبيت APK هذا العامل بشكل منفصل. التجربة الجديدة داخل [تطبيق T1–T5 الواحد](../../TEST_CENTER.md)، [الحزمة الواحدة](../../unified/pack/team-testpack.json)، [سياسة التعاون](../../UNIFIED_LAB_POLICY_AR.md)، [صف جاهزية بناء Mini المشترك](../../SHARED_BUILD_READINESS.md). احتفظ بروابط APK القديمة وأدلّتها أدناه للأرشفة فقط. يمكن أن يحتاج العامل تغيير Java/renderer تحت unified، ولا يبدأ بناء مستقل؛ T5 ينسّق واحداً عند حاجة عامل واحد مثبتة.

# T4 — Android physical mouse mini lab (INPUT-005)

**READY_TO_TEST (APK exists; Android 15 device behavior NOT YET TESTED)**

## Immutable actual build
- Worker: T4; test app `com.alwansan.raft.lab.t4`; versionCode `1`, versionName `0.1.0-source-prototype`; targetSdk `35`; independent of Raft game and saves.
- [GitHub Actions 42496622364 — SUCCESS](https://github.com/alwansan/raf/actions/runs/42496622364), source SHA `1beab49d26aa31a6cc4765f0c6020c2d552cce7b`.
- Artifact `13623563385`, `raft-mini-lab-T4-1beab49d26aa31a6cc4765f0c6020c2d552cce7b`: run page **Artifacts** → download ZIP → extract `app-debug.apk`; ZIP size **35,398 bytes**, expires **2026-11-15 15:49 UTC**. The ZIP also contains `mini-lab-sha256.txt`.
- **Actual APK SHA256 from runner:** `a5a42b89642c75946f7d3fd5e46fab83b1f16ee800cbd7c2056a7ab74f3e2849`.
- Artifact ZIP SHA256 (different file): `4f356e648b29a35db8a22fdba049cd1ee83d1fe1e9c648bd261a7e213b1bc0a3`.
- [T4 nine-case testpack](https://github.com/alwansan/raf/blob/1beab49d26aa31a6cc4765f0c6020c2d552cce7b/apk-for-testing/examples/t4-mouse-testpack.json), manifest SHA256 `0d708913a7274507798843c27a10e2005844d33c7890663cd0ec055c8ef8702a`. This is **data-only**; pick it with Android official `Pick testpack` file selector. Without importing it the generic host displays only 3 built-in cases.

## Owner steps and expected evidence
Use the **real physical mouse** on Android 15. The pad receives Android callbacks only; it does not run Unity/Raft.
1. `T4-01`: Capture **OFF**, click LEFT; expect `BUTTON_PRIMARY`, `ACTION_DOWN/UP` or `ACTION_BUTTON_PRESS/RELEASE`. `T4-02`: Capture **ON**, move the mouse and click LEFT again; expected button survives relative movement.
2. `T4-03`: RIGHT with capture ON; expect `BUTTON_SECONDARY`. `T4-04`: MIDDLE with capture ON; expect `BUTTON_TERTIARY`. Observe press **and** release, not just one.
3. `T4-05`: scroll up/down with capture ON and OFF; expect nonzero `AXIS_VSCROLL`. `T4-06`: hardware horizontal wheel/tilt if available; expect `AXIS_HSCROLL` or explicitly `NOT_SUPPORTED` when absent.
4. `T4-07`: release/reacquire capture, send app background/foreground; ensure no stuck button and log callback routes. `T4-08`: keyboard and finger touch must remain working. `T4-09`: perform same actions in installed **full Raft** separately, recording Raft APK source/version; mini-lab pass alone does not prove game pass.
5. Each test: choose PASS/FAIL/UNEXPECTED, enter observed note, **Export logs** and share `events-*.jsonl`, relevant screenshots/short screen recording, and APK source/sha identity. An absent callback is only evidence if the physical action was actually attempted. Labels like `captured`, `activity_touch`, `activity_generic` and `view_generic` help distinguish Android View/capture routing.
6. Logs are continuously appended in app-private storage. The present generic host **actually exports** by MediaStore to `/storage/emulated/0/Download/Games/cl/test/t4-<pack>-<session>/`. **Outstanding mismatch:** the owner's expanded restore message requested an extra `raft log` segment in this path; this build does not include that segment. Report the actual path, coordinate any host-wide change with T5, and never misreport it as already compliant.

## Decision boundary and next change
- If Android shows actionButton/buttonState/scroll in Capture ON but Raft full game does not, debug the Unity Input System mouse button/scroll bridge, **without disabling the now-working camera capture**.
- If callbacks are absent under Capture ON but present OFF, inspect Android native captured dispatch and View listener consumption, not arbitrary forced Mouse0 pulses.
- A clean `T4-01..09` log under both capture states can be analyzed with `scripts/t4_analyze_mouse_lab_routes.py` (scheduled T4 source). A green source-only regression is not a device PASS.
- No game scenes/shaders/Unity code, .rgd worlds/saves, audio, Settings, keyboard, or touch overlay were edited in this T4 build session.

## Historical failed attempts (for provenance)
- [42496084526](https://github.com/alwansan/raf/actions/runs/42496084526): deprecated Android SDK `tools` package; T4 CI fix `6ab099095d3fdca135214c8c01f8fb85e3b2ad44` configures `platform-tools` only.
- [42496238418](https://github.com/alwansan/raf/actions/runs/42496238418): invalid Java newline escape in T5 MainActivity introduced after request; T5 fixed in `db8f507af7b1`.
- [42496449259](https://github.com/alwansan/raf/actions/runs/42496449259): Java definite assignment in T1ComputeProbe; T1 fixed in `ae450f1f84ef`.
- [42496622364](https://github.com/alwansan/raf/actions/runs/42496622364): **APK build and upload SUCCESS**, device test pending. Not game READY/3-of-3.
