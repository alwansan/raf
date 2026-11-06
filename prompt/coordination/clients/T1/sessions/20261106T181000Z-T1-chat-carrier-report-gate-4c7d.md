# T1 — rigorous sourcefree Unity float-carrier context evidence gate

- session_id: 20261106T181000Z-T1-chat-carrier-report-gate-4c7d
- origin: chat
- base_sha: ce8a29caca3fa5fc95e582bcd49f64039cf417d3
- resumed_from_sessions: 20261106T175623Z-T1-chat-float-carrier-context-b82c; 20261106T174500Z-T1-chat-phimerge-opengl-g6k2; 20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4
- issue_id: WATER-001 OPEN / NOT_READY 0/3
- status: completed (local Python evidence gate only; GPU fixture still pending)
- work: prompt/coordination/work/WATER-001/20261106T181000Z-T1-chat-carrier-report-gate-4c7d.json
- experiment: prompt/coordination/experiments/T1/20261106T181000Z-T1-chat-carrier-report-gate-4c7d.json
- event: prompt/coordination/B_TEAM/events/T1/20261106T181000Z-T1-chat-carrier-report-gate-4c7d.json
- original ZIP2 pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 (NOT acquired)
- trial policy: prompt/coordination/T_TEAM/TRIAL_BUILD_POLICY_AR.md
- vote round: trial-20261106-r1; T1=**لا يحتاج** (unchanged from d5330515a091e4503187040361cad226a01fb35b)
- previous trial build: source e9c358eda01785b65e4eb14f18723da426635628 / Actions 42058825739.

## Live recovery and evidence boundary

Rechecked latest T1 chat and scheduled original FFT evidence, branch HEAD, voting ledger and last 65 GitHub Actions runs. No nonterminal branch Action at first checkpoint; votes were T1/T2/T3/T5 `لا يحتاج`, T4 `يحتاج`, round COLLECTING, 5/5 unmet. Retained T1's row unchanged because no substantial integrated original water FFT repair exists. No changes to T2–T5 files.

Earlier actual synthetic Unity OpenGLCore [42129683073](https://github.com/alwansan/raf/actions/runs/42129683073) reported 63/64 bitcast-only and subnormal-multiply mismatches, but direct-integer/normal-float zero. Later actual Unity simple Texture2D bitcarrier [42261467757](https://github.com/alwansan/raf/actions/runs/42261467757) 320/320 exact and Phi sourcefree [42264618337](https://github.com/alwansan/raf/actions/runs/42264618337) 320/320 exact. True original-vs-generated HLSL Mesa Vulkan [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) same-input 384/384 keyed read parity, but source-derived Unity/OpenGLCore [42198180194](https://github.com/alwansan/raf/actions/runs/42198180194) still shows collapsed butterfly X and output mismatch. The precise Unity data-flow/FTZ mechanism remains unproven.

Session [20261106T175623Z-T1-chat-float-carrier-context-b82c](https://github.com/alwansan/raf/blob/feature/android-native-port/prompt/coordination/clients/T1/sessions/20261106T175623Z-T1-chat-float-carrier-context-b82c.md) committed isolated 10-category sourcefree Unity ComputeShader/C# NUnit fixture (64 invocations, expected 640 output words), but `.github/workflows/raft-t1-fft-unity-carrier-context.yml` was blocked by tool security checks and still returned 404. **No new actual Unity GPU test was executed**, and no trial APK requested. This cycle does not attempt a bypass or duplicate engine run.

## Engineering change and local tests

Published exactly two new independent T1 source-only files, without modifying any peer or original game file:

1. `scripts/t1_fft_carrier_context_result_gate.py` commit `41e016403a179d885fd13c13b6a9eebcaeaa902a`: strict one-case 2021 Unity NUnit evidence boundary, fail-closed return code/suite/counters/identity, rejects private XML failure/reason text and unbounded payload, accepts only ten canonical newline-delimited decimal 0–64 mismatch counts, refuses positive-control mismatches in categories 0/3/4, **retains diagnostic nonzero** categories 1/2/9 materialization and 5/6/7/8 Texture2D contexts. Emits only bounded category-level summaries; `original_raft_shader_compiled_or_compared=false`, `android_adreno_water_proven=false`. Can run later with `python3 -m scripts.t1_fft_carrier_context_result_gate --xml <privateNUnit> --metrics <privateCounts> --exit-code <unityExit>` inside an authorized ephemeral Unity runner. No original bytecode data included.
2. `tests/test_t1_fft_carrier_context_result_gate.py` commit `204944ec664c4e994d60b87f5fe40e3255fb7126`: 14 local adversarial tests. Tests exact case, source-free all-zero, valid materialization-only, valid fetch-only, mixed, positive control rejection, count 64 boundary, 9/11 count and noncanonical payloads, CRLF/trailing text/BOM, malformed/oversized XML, missing/wrong case, duplicate case, failure/reason, failed/skipped/inconclusive and nonzero Unity exit, symlinks, oversized file, and public CLI redaction.

Actual **local CPython command**: `(cd /mnt/data/t1-carrier-local && python3 -m unittest discover -s tests -p test_t1_fft_carrier_context_result_gate.py -q)`: **14/14 PASS** (no Unity or external GitHub runner involved), plus Python `compileall` successful. Critical content authenticity: calculated local Git blob SHA1 for script `dc5d7492eabf9e680d00e3e28d5f10a93df338ad` and test `92983941d0ed90a571e337b8aeb80832c9539198`; verified both *exactly* match live GitHub `fetch_file` blob SHAs after commit. Local SHA256 script `93e6f27dd2e032096c2181048c236ce1789c174f7129412f23eef7e16e47b0c6`; tests `a69b00d35febd9d373b1f73afa8a8acf8aab84fae322d20b34151532580e9081`.

No CI run or released APK/OBB/XAPK resulted from this new source-only work. The new gate does NOT authenticate a compiler itself; it is only intended to validate a genuine Unity NUnit result and diagnostic metrics on a trusted licensed runner, where the actual original game data stays private. The 14 tests use synthetic XML fixtures, not real Unity.

## Handoff

- Scope completed and resource released; code and full local negative-control evidence checked in.
- Underlying sourcefree 10-category actual Unity test **remains BLOCKED** pending authorized workflow publication and one execution. Do not interpret the new gate's 14 Python tests as 640 GPU values measured.
- Follow-on independent first priority: use original-source authenticated same-input *Unity* keyed FFT readback against Vulkan and localize first real butterfly mismatch before altering game kernels; if Unity workflow publication becomes available, execute the ten-category fixture once with this strict gate, without creating extra schedules or firing native build.
- WATER-001 OPEN / NOT_READY 0/3; trial vote T1 **لا يحتاج** stays unchanged. No alterations to T5 build control, audio/Settings/touch, other workers, or native workflow.
