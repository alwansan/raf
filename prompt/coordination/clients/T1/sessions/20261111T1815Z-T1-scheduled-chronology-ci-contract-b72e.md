# T1 — scheduled chronology CI contract repair
session_id: 20261111T1815Z-T1-scheduled-chronology-ci-contract-b72e
origin: scheduled
resumed_from: 20261111T1712Z-T1-scheduled-preworld-order-93ac; 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
baseline_sha: 281a770541aec0484842f2429b253f96600372c3
scope_commit: dc6015d3fc58f3841f7d2c36e40261a61fbc9528
fix_commit: ca617f92c2cf933cf40b56ae793fee7cb9ffd635
work: prompt/coordination/work/WATER-001/T1-20261111T1815Z-T1-scheduled-chronology-ci-contract-b72e.md
failure_evidence: https://github.com/alwansan/raf/actions/runs/43066215281 (5/5 synthetic tests passed; pinned CL step exit 2 due to unsupported --session and --source-commit)
change: workflow now verifies pinned summary SHA256, invokes current positional-only analyzer and checks its actual list-of-one JSON output schema, instead of obsolete fields. No change to analyzer source, original shaders, or game.
new_ci: https://github.com/alwansan/raf/actions/runs/43074969754
ci_status_at_record: in_progress (waiting_ci); do not repeat workflow or claim green before completion.
owner_evidence: https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md ; owner world enter/save/reenter success preserved, package publish failure separate. 8 Nov CL summary is a distinct later evidence sample, not merged with 5 Nov counts.
limitations: no Unity/Adreno/GPU numerical parity, no original authored .compute GUID/FindKernel mapping, no new phone execution. WATER-001 OPEN NOT_READY 0/3.
next: inspect CI43074969754, fix only if new concrete failure; authenticate original .compute/.meta GUID and kernel names, instrument FindKernel/Dispatch and compare first numerical FFT pass in authorized isolated run. Leave T4 physical mouse and T5 Resolution/button scope intact.
