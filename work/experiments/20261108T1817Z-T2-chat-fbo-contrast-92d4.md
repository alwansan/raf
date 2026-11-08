# T2-FBO-CONTRAST-20261108 — two-stage GLES3 FBO spatial assertion

session_id: 20261108T1817Z-T2-chat-fbo-contrast-92d4
origin: chat
base_sha: 6d8f2df68b04aa6c072db9777b5bda8293bc29d9
scope: T2-only compiled synthetic GLES FBO test in one unified Raft Team Lab; no full game build.
resource_key: WATER-001
status: SOURCE_PATCHED / DEVICE_UNTESTED
intended_files: apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T2GpuActivity.java, T2-only readiness row, this work, T2 session/memory/event/state
resumed_from: clients/T2/sessions/20261108T171538Z-T2-scheduled-fbo-audit.md
taken_over_from: T2 source CI 42496746941; earlier baseline audit 6eac6129368a5b348a6843657886bfee7a60d492

## Failure mechanism bounded to the test
Prior case T2-02 used FBO0 fragment output with a CONSTANT RGBA value, then FBO1 fetched the same flat texture and read one final pixel. Some spatial addressing/texture binding mistakes would be invisible because the whole source is flat. This was a test coverage blind spot, NOT a verified cause of Raft water failures.

## Source delta & expected device observations
- Commit [73924c998d91eb64be33c883d9922d44981accd4](https://github.com/alwansan/raf/commit/73924c998d91eb64be33c883d9922d44981accd4).
- CASE02 now draws two regions of an 8x8 RGBA8 FBO0 with a step in fragment x: left (0.125,0.375,0.625,1), right (0.875,0.125,0.25,1).
- Reads pixel (2,4)=32,96,159,255 and (6,4)=223,32,64,255 from first FBO; then second FBO pixel (4,4) retains original baseline and (6,4) validates contrasting sampled texel. Tolerance remains +/-2/channel. Each glReadPixels checks GL error.
- Bound GL thread, generated textures/FBOs, GLSL compile/link and negative cases T2-03/04 retained. Driver source fingerprint in unified Gradle includes this file; unchanged cases for other workers retain fingerprints.

## Validation / limits
- Source revision confirmed by GitHub fetch_file SHA 4670578f0f12728fa484ad1420d595abef414815.
- 7/7 static linkage/contract checks passed in session tool, including both stage pixel check presence and auto-result routing.
- Independent host mathematical oracle reproduces four RGBA values and nearest 8x8 texture coordinates. This is NOT Android GLES runtime or GLSL compilation evidence.
- Unified javac CI [42504045625](https://github.com/alwansan/raf/actions/runs/42504045625) succeeded on an older SHA; NOT post-change proof. Previous T2 standalone APK CI [42496746941](https://github.com/alwansan/raf/actions/runs/42496746941) is historical.
- Build vote [55ab1c80547a319b2809d2dea4bd66185cc927fa](https://github.com/alwansan/raf/commit/55ab1c80547a319b2809d2dea4bd66185cc927fa): only T2 row NEED_BUILD; requesting T5-reviewed SINGLE shared mini APK after updated unified javac. No T2 standalone APK or native Raft request.
- No original proprietary shader/CB0/Material/Texture data, Unity build, XAPK/OBB, or device pixel evidence changed. WATER-001 OPEN.

## Next step
T5: updated unified Java compile gate followed (if passing) by T5-reviewed one shared Mini APK delivery with stable signing; record source SHA/package/bytes/sha256; device T2-02 expected 4 pixels in output JSONL. T2: continue authentic original Foam pass0/1 producer -> destination + CB0/sampler binding before changing Raft ShaderLab. Avoid fake PASS and retain T1/T3/T4/T5 other cases.

## CI/event-ledger follow-up (18:24 UTC)
- Automatic T2 inherited-ledger summary runs [42509557131](https://github.com/alwansan/raf/actions/runs/42509557131) and [42509789222](https://github.com/alwansan/raf/actions/runs/42509789222) FAILED at pre-existing `scripts/refresh_b_team.py::read_records`. Precise first traceback: `ValueError: Missing record identity: prompt/coordination/B_TEAM/events/T3/20261106T1959Z-T3-chat-original-stage-probe-9f24.json`; T3 historical JSON has `session_id` but neither `id` nor `event_id`. This is a strict inherited-event-index validation failure, NOT a shader/device/Java compile failure or proof about T2 driver.
- The new T2 result event is explicitly `event_id`-identified and now includes `owner/issue_id/summary/at` (metadata commit `1a2d73179616f36fbfb33f867bb5955e7f93ef68`); leave T3's file untouched to respect worker ownership. Notify T3 to add an explicit stable ID with CAS and rerun index only after that source defect is corrected; do not weaken `refresh_b_team.py` to derive event identities automatically.
- At 18:24 UTC other worker Actions are QUEUED (T4 mouse and T5 source-only); do not cancel, duplicate or interfere. Updated unified Java compile after T2 source `73924c9` is STILL NOT proven.
