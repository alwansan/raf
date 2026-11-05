# T1 | 20261105T121347Z-T1-paired-capture

resumed_from_session: 20261105T121028Z-T1-parity-oracle

Capture one-row authenticated Vulkan source/butterfly and both pass outputs; feed exact RGBA32F input bytes into the licensed private Unity fixture and compare both readbacks.

Shared identity files are preserved. Baseline 9560bc7c922e70d663f2869f30cffef9c1b90c41.

## Implementation checkpoint

Prepared private CI experiment: Vulkan captures original-derived SPIR-V pair 0/1 source, butterfly, intermediate and final RGBA32F images. Unity uploads the same input bytes with a linear float target, uses one workgroup and captures both passes. The comparator publishes counts and booleans only. Local Python compile, Vulkan host source transform, and workflow YAML parse passed. Actual execution pending.
