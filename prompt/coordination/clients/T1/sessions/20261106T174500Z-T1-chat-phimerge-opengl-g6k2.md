# T1 — Trial build voting adoption + isolated Unity OpenGLCore Phi/CFG address experiment

- session_id: 20261106T174500Z-T1-chat-phimerge-opengl-g6k2
- origin: chat
- issue: WATER-001 OPEN / NOT_READY 0/3
- status: waiting_ci
- base_sha: 99658d34f59ce64a8f961e942c641882c0750110
- resumed_from_sessions: 20261106T172258Z-T1-chat-bitcarrier-textureload-c4e9; 20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4; 20261106T171240Z-T1-chat-unity-keyword-runtime-9f3a
- new owner policy: [TRIAL_BUILD_POLICY_AR.md](../../../T_TEAM/TRIAL_BUILD_POLICY_AR.md)
- live trial vote: [TRIAL_BUILD_READINESS.md](../../../T_TEAM/TRIAL_BUILD_READINESS.md)
- vote: **T1 = لا يحتاج**, round `trial-20261106-r1`, commit `d5330515a091e4503187040361cad226a01fb35b`, UTC 2026-11-06T17:43:16Z
- latest actual device: owner enters/saves/reopens world on e9c358eda01785b65e4eb14f18723da426635628, GitHub Actions [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739); no new original-authored FFT integration into game from T1 yet.
- preceding positive: real original-vs-HLSL same Vulkan [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) 384 keyed reads matching and sourcefree Unity OpenGLCore bitcarrier [42261467757](https://github.com/alwansan/raf/actions/runs/42261467757) 320 reads zero mismatch, **not original Raft water**, unchanged vote.
- active run: [42264618337](https://github.com/alwansan/raf/actions/runs/42264618337)
- work: prompt/coordination/work/WATER-001/20261106T174500Z-T1-chat-phimerge-opengl-g6k2.json
- experiment: prompt/coordination/experiments/T1/20261106T174500Z-T1-chat-phimerge-opengl-g6k2.json
- event: prompt/coordination/B_TEAM/events/T1/20261106T174500Z-T1-chat-phimerge-opengl-g6k2.json
- source ZIP2: pinned 15964ea8f246b6e076ce26b60931ee2e1a9a2385, **not accessed**.

## Vote decision and concurrency

Read the whole 2026-11-06 owner [trial-build policy](../../../T_TEAM/TRIAL_BUILD_POLICY_AR.md) and current vote ledger, and checked branch HEAD/nonterminal Actions. Wrote only the T1 table row with expected blob SHA; did not alter T4's `يحتاج` or unset T2/T3/T5 votes, T5 build decision, round id or native request. The current FFT work is sourcefree/synthetic diagnostic and can progress without a new phone APK. It is **not sufficient** for a T1 `يحتاج` vote because no major fully integrated original FFT water fix exists. Later source-authentic integration and real phone acceptance question can justify revising **T1's own** row, not now.

New independent scope registered before changes; latest scheduled T1 `20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4` reserved a distinct authentic original-Unity readback investigation but no overlapping synthetic files/CI.

## Engineering test

The prior basic uint4/float4 bitcarrier and swizzle Texture2D.Load all pass on Unity OpenGLCore. Original translated butterfly1 X and butterfly2 X/Y HLSL SSA provenance terminates at float32 `OpPhi`; simple bitcasts therefore are not sufficient explanation.

- Public authored synthetic `android-port/Experiments/T1/T1FftPhiMergeTextureLoad.compute`: 64 GPU threads sample 64×32 RGBAFloat from identical coordinate-coded pixels via 5 paths: 2 direct integer control sites; simple branch merged `float2`; nested branch merged `float2`; dynamic per-thread loop-carried `float2` with `[loop]`. Actual sample coordinate bits derive from `asfloat(uint4)` then `asint` after CFG merge.
- `android-port/Experiments/T1/T1FftPhiMergeTextureLoadTests.cs`: Unity2021.3.45f2 NUnit 1-case exact test, asserts OpenGLCore backend, 320 uint32 GPU readback words, emits only five bounded 0–64 per-site mismatch counts. No original shader, raw private trace, APK, or Adreno.
- `tests/test_t1_fft_phi_merge_texture_fixture.py`: 3 synthetic source guards; additional established Unity fixture controls.
- Isolated `.github/workflows/raft-t1-fft-unity-phi-merge-texture.yml` uses pinned GameCI v0.1.72, existing licensed Unity2021 image and `raft-native-engine-${{ github.ref }}` mutex with cancel-in-progress:false. No original data sparse checkout, no GPU test artifacts, private log/XML/project erased. Only authorized aggregate five-counts and strict NUnit one-case verdict visible.

Published code commits: `cf838948d986f8c209a4d57e2f3f7c48bb24ae0f`, `93f14b17ca296f204473e835a6c27f869d286460`, `dcbaf1d5edc16bb43e64c6d8a11e9d6778019ab3`; workflow commit `c5c05827589db1810b1ab9bb738c92028fce6e4a`.

## Evidence status and next action

At checkpoint [42264618337](https://github.com/alwansan/raf/actions/runs/42264618337) has started and actual Unity test is pending. Read terminal job and exact `RAFT_T1_PHI_MERGE_TEXTURE_COUNTS` and `RAFT_T1_PHI_MERGE_NUNIT`; if nonzero synthetic OpenGLCore site count but direct controls pass, narrow compiler CFG hypothesis. If zero, reject basic nested Phi alone as sufficient cause; actual original SSA arithmetic/unresolved alias and Unity binding remain. Preserve source-only vs actual Unity vs device levels of proof.

No work performed on other T clients' files or credentials. No build, no change to full readiness, no all-five consensus claim. **T1 vote remains لا يحتاج** until proven integrated major game change needs new phone test.
