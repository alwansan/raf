# T2 chat — GLES FBO multi-pass contrast verification
session_id: 20261108T1817Z-T2-chat-fbo-contrast-92d4
origin: chat
resumed_from: clients/T2/sessions/20261108T171538Z-T2-scheduled-fbo-audit.md; prompt/coordination/clients/T2/MEMORY.md (historical)
base_sha: 6d8f2df68b04aa6c072db9777b5bda8293bc29d9
branch: feature/android-native-port
scope: T2-02 compiled-in GLES3 offscreen FBO positive control; no proprietary Raft assets, game XAPK, or T5 shared UI changes.
intended_files: apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T2GpuActivity.java; this session; own T2 work/experiment; only T2 readiness row after meaningful merge.
experiment_key: T2-FBO-CONTRAST-20261108
resource_key: WATER-001 (OPEN, source authenticity/device blocked)
run_urls: historical CI 42496746941 T2-only APK; unified javac 42504045625; no queued/in_progress/pending runs observed at 18:16 UTC.
taken_over_from: T2 scheduled FBO audit (6eac6129); earlier T2 independent GLES case CI 42496746941.

## Hypothesis
The current two-pass FBO test draws a spatially constant source color, so the second pass does not check spatial texture addressing or contrasting texels. Improve T2-owned CASE02 with a second distinguishable source region; read back both FBO stages and verify contrasting pixels, with actual GL error checks. Keep original baseline pixel contract, do not change shared pack or other workers' files.

## Initial limits
CI compile or synthetic GLES tests cannot confirm original Raft Foam/Spectrum/Blur/ShaderLab, pass bindings/CB0, authentic Unity, or Adreno runtime. Build of the unified APK is T5's decision.
status: SOURCE_PATCHED_DEVICE_UNTESTED
source_commit: 73924c998d91eb64be33c883d9922d44981accd4
readiness_commit: 55ab1c80547a319b2809d2dea4bd66185cc927fa
work_path: work/experiments/20261108T1817Z-T2-chat-fbo-contrast-92d4.md
event_path: prompt/coordination/B_TEAM/events/T2/20261108T1817Z-T2-chat-fbo-contrast-92d4-result.json
validation: 7/7 source/linkage checks PASS and four expected RGBA values confirmed by host mathematical oracle. NO post-patch javac/real device evidence.
run_urls: CI 42504045625 shared javac PASS on older source; CI 42496746941 standalone T2 APK PASS historical; zero queued/running/pending at 18:16 UTC (point-in-time).
scope_boundary: T2GpuActivity.java was the sole Android driver file edited; no shared UI, shared pack, full game/XAPK/OBB or original shader/raw source modified.
next_step: T5 to run updated unified Java compile gate and review one shared mini build under SHARED_BUILD_READINESS. Await T2-02 4-pixel phone JSONL and continue original Foam two-pass operand/binding proof without synthetic-to-Unity false equivalence.
