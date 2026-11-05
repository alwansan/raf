# T1 — isolated FFT Unity runtime-kernel probe (2026-11-05)

**Issue:** WATER-001 / P0 (OPEN). **Owner:** T1, session `20261105T002257Z-T1-fft-unity-contract`. **Scope:** an isolated private Unity Editor probe and SHA-bound staging guard, **not** restored game water, original source, verified original runtime kernel order, or Android execution.

## Baseline and hypothesis

Prior B48 [41912422220](https://github.com/alwansan/raf/actions/runs/41912422220) established 10 original source-selected two-pass *candidate* operations over 20 original serialized compiled programs, based on resolution/bank and group dimensions; B30 showed serialized variant headers/keywords could not prove runtime identity. Previous T1 [41939314440](https://github.com/alwansan/raf/actions/runs/41939314440) measured actual bank0 sampled-input sensitivity on six CPU Vulkan two-pass runs, with bank1 failures retained [41938536760](https://github.com/alwansan/raf/actions/runs/41938536760), [41939082498](https://github.com/alwansan/raf/actions/runs/41939082498). These are not Unity `FindKernel` indices and not Adreno proof.

A separately authored private `.compute`, its explicit private names/keyword choices, and an isolated Unity 2021.3.45f2 Editor process may reveal its *actual imported authored-source* `HasKernel`/`FindKernel` indices and `GetKernelThreadGroupSizes` output without conflating them with the original compiled variants. Original binary identity and authored-source reconstruction must still be independently established.

## Code integrated on the only permitted branch

- `scripts/t1_stage_unity_fft_kernel_probe.py` requires SHA256/size authentication of original `sharedassets0.assets` (115978112 bytes, `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`) and a SHA-bound private authored `.compute`. It validates the B48-only original object SHA (`9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`), all 20 unique **compiled candidate slots**, the original resolution/bank/pass selector and `2*r,1,1` expected groups. Names may repeat across compiled slots; 20 runtime kernel IDs are neither assumed nor fabricated. Existing B47 preprocessor/kernel-body guard is reused. Output must be newly created and remains private.
- `android-port/Editor/T1FftKernelRuntimeProbe.cs` loads the staged authored ComputeShader in a separate Unity Editor project, verifies the staged authored source SHA again, calls `HasKernel`, `FindKernel`, `GetKernelThreadGroupSizes`, and checks the source-selected expected group contracts. It emits only bounded numeric observations, never private shader source or names; each line explicitly says `original_unity_mapping_proven=false`. The probe is not copied to playable game runtime.
- `tests/test_t1_stage_unity_fft_kernel_probe.py` contains seven synthetic/negative suites covering selector collisions, provenance, stage overwrite, source drift, invalid names/keywords, missing original bytes and output redaction.
- Isolated, narrow `.github/workflows/raft-t1-fft-unity-kernel-probe.yml` has 6-minute timeout, `cancel-in-progress:false`, no Unity license, no original assets downloaded or public source artifacts, and no effect on the shared Unity native workflow.

## Verified tests, limits and next step

- [41941690194](https://github.com/alwansan/raf/actions/runs/41941690194): **SUCCESS**, source-only staging suite at commit `af101fe5c06603d567d58a23de557fae7d57d506`.
- [41941716641](https://github.com/alwansan/raf/actions/runs/41941716641): **SUCCESS**, same isolated suite after resolving runtime SHA lookup relative to `Application.dataPath`, commit `602e9963ea8f45e71823412d4b5e35016e370f7c`.
- Neither CI run executed Unity, created authentic authored FFT shader source, verified source↔original compiled program identity, used the Adreno GPU, built an APK or proved water pixels. Unity preflight is prepared for a **private authored-source input**, not claimed done. `WATER-001` remains **OPEN**; readiness `NOT_READY / 0 of 3`.

When actual original-authenticated authored FFT `.compute` and private name/keyword mapping become available, run an **authorized private staging** with:

```sh
python3 -m scripts.t1_stage_unity_fft_kernel_probe \\
  --original-owner /private/verified/sharedassets0.assets \\
  --authored-compute /private/fft_authored.compute \\
  --private-manifest /private/fft_probe_manifest.json \\
  --project /private/t1_fft_unity_project
# Then, in a licensed Unity 2021.3.45f2 environment with graphics enabled:
Unity -batchmode -quit -projectPath /private/t1_fft_unity_project \\
  -executeMethod T1FftKernelRuntimeProbe.Run -logFile /private/t1-unity-fft.log
```

Retain only aggregate redacted results and SHA/Unity version; never upload staged private `.compute` or manifest. An authored-source positive is a new Unity observation, **not** proof that the original game's serialized compiled slots have the same runtime kernel identity. Establish that original mapping independently before integration with T5 and Android/device testing. Protect existing audio/Settings and deferred touch/layout.
