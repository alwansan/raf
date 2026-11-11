# T1 WATER-001 scoped work
session_id: 20261111T1507Z-T1-scheduled-fft-dispatch-contract-6e4b
origin: scheduled
base_sha: 1793aa29bb80eb75ca7e94e37a0ca3a638a654de
issue_id: WATER-001
experiment_key: original-fft-kernel6-unity-dispatch-contract-device-42058825739-CL-520c4cf
resource_key: none (read-only pinned CL and original FFT metadata)
intended_files: prompt/coordination/work/WATER-001/T1-20261111T1507Z-T1-scheduled-fft-dispatch-contract-6e4b.md; prompt/coordination/clients/T1/sessions/20261111T1507Z-T1-scheduled-fft-dispatch-contract-6e4b.md
status: active

Hypothesis: the Unity exception "Invalid kernelIndex (6) passed, must be non-negative less than 0" indicates a zero-kernel ComputeShader object at Dispatch, not evidence that original compiled DXBC slot 6 is a valid Unity kernel index. Separate (a) asset import/HasKernel, (b) FindKernel name/index, (c) Dispatch dimensions and (d) device log trace. Never map DXBC slot to Unity index by integer coincidence.

Owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md (world enter/save/reenter on Artifact; publish failure). CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57, sessions 220911-559 and 230108-327. Source e9c358eda01785b65e4eb14f18723da426635628. Later owner 2026-11-08 mini-lab policy applies.

Acceptance: a single source-authenticated .compute asset with GUID and named kernels; Unity Editor HasKernel/FindKernel/GetKernelThreadGroupSizes records; matching Dispatch call site and exact resource bindings; first numeric FFT pass comparison against authenticated Vulkan reference; separate Android/Adreno evidence. Existing proximity/counter tools do not satisfy these gates. Do not run full Unity build or duplicate T5 mini-lab.
