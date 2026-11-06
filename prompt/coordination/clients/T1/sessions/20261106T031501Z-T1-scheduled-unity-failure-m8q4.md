# T1 scheduled checkpoint — 20261106T031501Z-T1-scheduled-unity-failure-m8q4
origin: scheduled
issue: WATER-001
branch: feature/android-native-port
base_head: 2764e46f70db7a7894c97e3c09034f52a6e0d0f2
scope_commit: 42c303732ded9e39a0f083d644587011f8ce6e01
resumed_from: 20261106T024340Z-T1-chat-84f0c6.md; 20261106T020900Z-T1-scheduled-trace-a7c2.md

## Evidence newly checked
Owner phone artifact run 42058825739 remains the current positive world/save/reopen evidence; release publishing failed. Owner CL 220911-559 water-pass 23,884/kernel 3,850 and 230108-327 water-pass 39,132/kernel 6,026; kernel index 6 is not yet identified as an original named Unity kernel. No phone water success.

The two pending Unity replay runs from the latest T1 chat checkpoint have now both completed **failure** (not pending): [42152199100](https://github.com/alwansan/raf/actions/runs/42152199100) at step 'Validate privately translated original FFT t0/t1/u2 HLSL resources for first candidate pair'; [42152295025](https://github.com/alwansan/raf/actions/runs/42152295025) advanced past that step but failed at 'Execute exact original-derived FFT ComputeShader import and two-pass GPU dispatch with PRIVATE captured GameCI logs'. The second is the corrected candidate SHA 4ed17012aaf5e3ed79bf17f230cd9c34767f4157. These step boundaries do NOT distinguish Unity shader import, FindKernel, Dispatch or GPU readback; no evidence of numerical comparison was returned. Do not report the corrected run as still queued or successful.

Prior [42141540903](https://github.com/alwansan/raf/actions/runs/42141540903) proved Vulkan self-parity only (64/64, 32/32), not Unity parity. Earlier cross-backend 63/64 and 31/32 mismatch remains unresolved. The source rewrite's effect on Unity is unknown.

## Scope and next experiment
[Independent work scope](../../work/WATER-001/20261106T031501Z-T1-scheduled-unity-failure-m8q4.md) recorded before this checkpoint. No equivalent CI repeated, no shared files edited, no game source/asset changes. First extract private Unity step logs and the candidate hash sidecar from 42152295025; classify failure by earliest explicit exception and asset/kernel identity. If logs are inaccessible, add a minimal fail-closed CI diagnostic in a distinct file only after reading current workflow and coordinating active T1 chat scope. Run paired baseline/promoted control only when import/dispatch is actually verified.

T4 physical mouse and T5 three buttons/Resolution remain actively owned, do not duplicate their edits. WATER-001 OPEN, readiness NOT_READY 0/3. No native/phone validation.
