# T3 chat checkpoint — 20261108T1540Z-T3-chat-gles-material-lab-6b2a

- worker: **T3**
- origin: **chat**
- session_id: `20261108T1540Z-T3-chat-gles-material-lab-6b2a`
- base_sha: `615b19729e20af76df0f326a1959d20cd88188e5`
- resumed_from_sessions: `20261108T1529Z-T3-scheduled-neg-fileid-q7m2`; `20261108T1430Z-T3-scheduled-particle-yaml-k6d2`; `20261108T1326Z-T3-scheduled-audit-ci-n4q8`
- issue: **RENDER-002** (OPEN, NOT_READY)
- work: `prompt/coordination/work/RENDER-002/20261108T1540Z-T3-chat-gles-material-lab-6b2a.json`
- experiment_key: `t3-gles3-adreno730-rgba-srgb-alpha-blend-device-differential-20261108`
- scope: independent synthetic GLES 3.0 color/texture/particle blend diagnostic with six numbered phone tests, safe data-only instructions pack, app-private logging and MediaStore export.
- files: `apk-for-testing/workers/T3/gles-lab/**`, `.github/workflows/raft-t3-gles-material-mini-lab.yml`, `apk-for-testing/workers/T3/testpack.json`, `apk-for-testing/workers/T3/README.md`, own T3 row in `apk-for-testing/TEST_CENTER.md`, own work/session/event.
- concurrent check: no queued/in-progress Actions at first inspection; T4 reserved separate mouse mini host scope during this session, T5 did separate SAF regression. No shared host source, Raft game source/Unity assets, T4 files, native build request, or scheduled task changed.

## Verified engineering result

1. Created self-contained Android GLES 3.0 Java lab in `1147eca961eddd2dd46edae8c7b8771bffba72fc` with six controls: RGB baseline, vertex interpolation, straight alpha particle overlay, premultiplied-alpha comparison, UNORM vs sRGB, negative GLSL compilation control. Each records shader and GL diagnostics/pixel sample; manual PASS/FAIL/UNEXPECTED notes. Import accepts `T3` declarative testpack note cases only, does not execute programs from imports; logger app-private and MediaStore Download export. No real game textures/decompiled proprietary shaders.
2. [CI 42496333650](https://github.com/alwansan/raf/actions/runs/42496333650) **FAILURE before Gradle** at Android action `sdkmanager tools` obsolete package on hosted runner. This was infrastructure, not source/renderer failure.
3. Fixed isolated workflow in commit `a4578ff4cd7f7d7928038abdb1d076d514096da8`: use preinstalled Android 35 SDK/build tools or install explicit Android 35 packages, no obsolete `tools`.
4. [CI 42496427649](https://github.com/alwansan/raf/actions/runs/42496427649) **SUCCESS**: Android SDK check, Gradle assembleDebug, aapt package verification, and Artifact upload. Source SHA **`a4578ff4cd7f7d7928038abdb1d076d514096da8`**. Downloaded real artifact ID `13623309536`; extracted APK; verified ZIP contents, valid APK ZIP and signed APK Signing Block and SHA256.
5. APK identity: package `com.alwansan.raft.lab.t3.gles`, versionCode **1**, version `0.1.0-t3-gles`, size **20,425 bytes**, SHA256 **`c6396bc89548eeb55fc85d354a47a5fa77b98dfb7a79218af2dbc2a902615078`**. Artifact ZIP 17,532 bytes, expires **2026-11-15T15:46:28Z**. Run page [42496427649](https://github.com/alwansan/raf/actions/runs/42496427649). Debug APK is available for owner testing; user can download directly from the conversation or Actions Artifact. Do not invent a GitHub release APK.
6. Six-case data-only `testpack.json` committed `29af263b20cf205b15e1aacc1a57eaea3b4032ca` (all `note` types, no code), T3-only center row `7617826d`, detailed [worker README](../../../../../apk-for-testing/workers/T3/README.md) `9eefaeda`.

## Evidence distinction and limitations

- **Confirmed:** Source compiled for Android; actual signed APK was produced and downloaded; package/hash/size checked. Source-only synthetic GLES cases exist inside the app.
- **Not confirmed:** Any case on owner's Adreno 730; visual output, accurate pixel expectations on real phone, Unity shader variant/import, Raft original material/particle textures, fire/lighting quality or restored gameplay. RENDER-002 remains OPEN, full Raft XAPK readiness unchanged, no 5/5 vote.
- Owner November 8 CL report `LogRaft-20261108-164850-270`: water pass and FFT error floods, cursor warning and persistent graphics defects. Mouse click/scroll belongs to T4. Different LogRaft runs are not merged. Do not assume generic GLES success fixes Unity.
- Last T3 scheduled negative Material PPtr fileID change (`b4f7d645` + fixture `3825975d`) was **not** tested by previous CI 42485092438 because that run predates the patch. Its own source regression and authenticated ZIP2 scan remain separate next steps.

## Device feedback request and next

Ask owner to run CASE01–CASE06, record manual ratings and notes; send screenshots of CASE02/03/04/05 and exported `/storage/emulated/0/Download/Games/cl/test/t3-gles-material-<session>/events-*.jsonl`. For CASE03 expect a translucent red overlay exposing blue background; CASE04 both blend contracts similar; CASE05 sRGB darker, CASE06 deliberate shader compile failure with negative_control PASS. If that differs, collect GPU errors before assuming game defect.

When the device evidence arrives, compare generic GLES alpha/sRGB results with a verified Raft screenshot/artifact, then trace actual Unity ParticleSystemRenderer → Material → Shader → Texture/keywords/blend/alpha and full game integration. If no device result yet, continue authenticated original/export source analysis or source-only negative-fileID CI in a *separately coordinated scope*. No continued work in background is claimed.
