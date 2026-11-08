# T3 — Arabic, portrait-ready real visual case launching

- **session_id:** `20261108T1940Z-T3-chat-arabic-manual-visual-v4c8`; `origin=chat`; worker T3; track `RENDER-002`.
- **resumed:** `20261108T1852Z-T3-chat-png-integrity-k8m2`, live latest T3/T5 files and readiness r2.
- **base_sha:** `aed5beb86c035789ef81a4a642d4ac412dfc9b29` before T3 work reservation.
- **owner physical-phone bug:** tapping T3 tests opened no graphics or new page. Verified old shared host `openPending` only displayed text; `launchManualCase` T3 path only suggested AUTO T3. Old TESTPACK v1 is incompatible with unified schema v2, but native UI bug exists even with bundled 29-case pack.
- **coordination:** Concurrent T5 modified shared host and manifest, providing Arabic strings and portrait UI during this session. Re-read latest host `e0c988870beb51546f7e80cc7241df36f70dd96a` and patched only T3-specific request/host bridge plus six visible test case buttons using CAS. Preserved `ArabicLabStrings`, translated host strings, portrait manifest and all T5 SAF/result engine changes. No direct change to T5 state. Did not edit team pack or original game assets.

## Source changes
- `389b0779`: T3 GLES Activity Arabic titles/steps/expected, portrait-friendly RTL layout; manual `manual_case_id` view holds the exact selected synthetic GPU graphic visible, hides alternate case switches, shows deliberate `📷 التقاط صورة هذا الاختبار والعودة إلى النتائج` and `رجوع دون حفظ نتيجة`. Capture goes through existing pixel/frame/PixelCopy/MediaStore PNG+SHA path. Does **not** mark PASS.
- `7a03a277`: Unified host `T3_VISUAL_PREVIEW` request, guarded `manual_case_id` and shared session, real openPending() and RUN selected routes, correct exact-ID child result retention, URI readability before EVIDENCE_READY, canceled preview retains prior evidence.
- `bef7f88f`: six persistent directly tappable Arabic T3 case buttons on shared home (even if case previously cached), to avoid hunt through pending requests.
- `55d8908`, `5e387f0`: T3 `tests/test_t3_shared_visual_frame.py` expanded from seven to **ten** source-only regression tests for preview, explicit action, 6-case launch buttons, Arabic and T5 portrait preservation, real child state and no fake PASS.
- T3 dedicated source-only workflow already targets changed `T3LabActivity.java` and tests: `.github/workflows/raft-t3-shared-png-source-gate.yml`. **Actual current CI run number and Java compiler result not independently verified.** Direct live fetch, 18/18 source/content invariants PASS, not compiled or phone-tested.

## T5 build request and acceptance
- Own vote [shared r2](../../../../apk-for-testing/SHARED_BUILD_READINESS.md): **T3 NEED_BUILD** for **one** T5-coordinated shared Mini, because user-confirmed old APK UX bug cannot be tested without compiling source changes. T5 alone can create mini build request, check source/CI, verify APK/signature artifact, then provide new build. `0.2.9-shared` from prior CI42509945996 (source `cbe7a038`) does NOT include new UI or portrait.
- Original Unity full-game XAPK 5/5 vote unchanged; actual RENDER-002 graphics, Unity fire/water/Particle Shader48 still OPEN NOT_READY 0/3.
- After new APK exists: user taps any `▶ فتح T3-01..06` button; sees color/alpha/GLES preview as long as necessary; deliberately presses picture capture+return; then reviews picture, writes real observation and marks PASS/FAIL; exports `summary-*.json`, `events-*.jsonl`, `T3-*.png` to `Download/Games/cl/test/shared-<session>/`.
- [Full documentation](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_SHARED_ARABIC_MANUAL_LAUNCH_2026-11-08.md); [T3 event](../../B_TEAM/events/T3/20261108T1940Z-T3-chat-arabic-manual-visual-v4c8.json).

**Status:** integrated source handoff ready for T5 compile/build assessment; device and full game **UNVERIFIED**.
