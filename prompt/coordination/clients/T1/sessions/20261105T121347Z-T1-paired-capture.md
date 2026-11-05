# T1 | 20261105T121347Z-T1-paired-capture

resumed_from_session: 20261105T121028Z-T1-parity-oracle

Capture one-row authenticated Vulkan source/butterfly and both pass outputs; feed exact RGBA32F input bytes into the licensed private Unity fixture and compare both readbacks.

Shared identity files are preserved. Baseline 9560bc7c922e70d663f2869f30cffef9c1b90c41.

## Implementation checkpoint

Prepared private CI experiment: Vulkan captures original-derived SPIR-V pair 0/1 source, butterfly, intermediate and final RGBA32F images. Unity uploads the same input bytes with a linear float target, uses one workgroup and captures both passes. The comparator publishes counts and booleans only. Local Python compile, Vulkan host source transform, and workflow YAML parse passed. Actual execution pending.

Launched [paired capture CI](https://github.com/alwansan/raf/actions/runs/42025620147) from `7f79121a6366c0d7ddea89df8c90883b9fda51f1`. Local checks passed; CI result pending.

## Actual CI result

CI 42025620147 completed with a genuine numerical mismatch for pair 0/1 (1024×32 RGBA32F, one group per dispatch). Authenticated original-derived CPU Vulkan capture succeeded, and licensed Unity 2021 passed both private NUnit tests with observed writes. Both input blobs matched byte for byte. Pass 0: 64 written pixels compared, 63 outside tolerance. Pass 1: 32 compared, 31 outside tolerance. Both stages: zero write-coverage mismatches and zero nonfinite pixels. Cleanup succeeded. This is a negative parity result for this fixture.

Localize pass 0 first: add private per-channel aggregate error and a source-free GPU image upload/readback control on the exact same formats; then compare texture-load/coordinate and arithmetic semantics in original SPIR-V versus Unity-generated code. Preserve the failing baseline. No Android, author kernel identity, or in-game water validation.
