# T1 — bank1 FFT Vulkan Validation isolation (2026-11-05)

**WATER-001 remains OPEN. This is not a Unity or Android water fix.**

## New independent original-data diagnostic

Previous T1 original two-pass CPU Vulkan input-role probe ([41939314440](https://github.com/alwansan/raf/actions/runs/41939314440)) verified bank0 sampled-image sensitivity. Its bank1 negative trials were recorded accurately: candidate pair18/19 second-pass swap produced Mesa lavapipe SIGSEGV ([41938536760](https://github.com/alwansan/raf/actions/runs/41938536760)), whereas pair10/11 second-pass swap previously failed same-original-program comparator tolerance ([41939082498](https://github.com/alwansan/raf/actions/runs/41939082498)). Neither was a positive bank1 result.

Implemented `scripts/t1_fft_bank1_validation.py`, `tests/test_t1_fft_bank1_validation.py` and isolated `.github/workflows/raft-t1-fft-bank1-validation.yml`. The workflow stages only SHA-verified original ZIP2 `sharedassets0.assets`, size 115,978,112 B / SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, pinned ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. It authenticates the original ComputeShader object pathID2456 SHA256 `9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247`, extracts paired programs only in temporary directories, then runs the same original SPIR-V code as both source and comparator with baseline and second-pass sampled-image swapped descriptors. `VK_INSTANCE_LAYERS=VK_LAYER_KHRONOS_validation` is requested, and the layer's installation is checked via `vulkaninfo --summary`.

The executable captures driver stdout/stderr privately; emits only bounded outcome, numeric flags and counts of validation messages. No original code, shaders, DXBC, SPIR-V, pixels or raw driver messages are uploaded. A requested/listed validation layer and zero errors are not independent proof of activation of all validation features or lack of shader memory faults.

## Real CI result

[Original-data CI41942024538](https://github.com/alwansan/raf/actions/runs/41942024538) completed **SUCCESS as a diagnostic execution** with six synthetic negative controls, pinned source-byte check, C++ host build, four actual original software-Vulkan attempts and cleanup.

| Original compiled program pair | Descriptor profile | Process | Same-program numeric comparison | Validation error / warning / VUID markers |
|---|---|---|---|---|
| 10/11 | baseline | exit 0 | within tolerance, finite, wrote pixels | 0 / 0 / 0 |
| 10/11 | second-pass input swap | exit 0 | within tolerance, finite, wrote pixels | 0 / 0 / 0 |
| 18/19 | baseline | exit 0 | within tolerance, finite, wrote pixels | 0 / 0 / 0 |
| 18/19 | second-pass input swap | **SIGSEGV** | no numeric report | 0 / 0 / 0 |

The pair10/11 swapped-second comparator **passed** in the first validation run 41942024538, but **failed numeric tolerance again** in the follow-up original run [41942366020](https://github.com/alwansan/raf/actions/runs/41942366020), although both processes exited normally and wrote finite pixels. This is run-to-run instability for this deliberately invalid binding, not proof of any particular root cause. Pair18/19's SIGSEGV was reproduced even with a requested/available validation layer. Zero VUID markers cannot rule out shader out-of-bounds access, Mesa compiler/runtime defect, synchronization, host issues, or nondeterminism; no cause or corrective shader binding established.

Initial workflow attempt [41941989016](https://github.com/alwansan/raf/actions/runs/41941989016) failed at pre-original synthetic-controls step because the test module was not yet present on that commit; it is not a failed original workload. Test-containing source commit `8947361a0f601a9f145b6ee0d9c9fd0d7463a6ba` is the CI41942024538 candidate. Follow-up source commit `342e4634c18df161eb18224634a45252e0668e0b` distinguished attempted from completed; [CI41942366020](https://github.com/alwansan/raf/actions/runs/41942366020) SUCCESS diagnostically: four original attempts, three process exit0, one repeated pair18 SIGSEGV; pair10 swapped-second finite numeric comparison=false. Zero reported validation error/warning/VUID markers in all four attempts.

## Next real integration dependency

The contemporaneous T1 authored-FFT Unity-probe work has source-only CI successes ([41941690194](https://github.com/alwansan/raf/actions/runs/41941690194), [41941716641](https://github.com/alwansan/raf/actions/runs/41941716641)); these do **not** prove original-authored `.compute` import, Unity 2021 FindKernel/Dispatch selection or actual Adreno execution. Bank1 software fault remains unresolved and cannot justify swapping two sampled texture roles in a final binding. Coordinate any private Unity kernel-name manifest and real shader asset staging with the T1 original runtime probe and T5 rather than editing protected workflows or original assets speculatively.

Reproduction: `python3 -m unittest discover -s tests -p test_t1_fft_bank1_validation.py -v`; original-data commands, pinned acquisition, software Vulkan build and timeout are in the isolated T1 workflow. No audio/Settings/touch changes; Android game APK86 remains the newest published device-test version; WATER-001 OPEN and NOT_READY 0/3.
