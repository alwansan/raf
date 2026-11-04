# W5 original CB reflection mismatch (resolved source-side; CI pending)

Author: raft-20261104T110558Z-73a56a7b / W5
Date: 2026-11-04
Evidence:41820611443/attempt1, source1059b050d3f938535f34165fff4bf1f57ff71f3f.
First hosted run authenticated originals and passed the actual host canary, then
failed before raster in first original vertex uniform normalization. This is W5
experiment code failure, not an original game failure or a numeric mismatch.

Root cause reproduced on actual local original SPIR-V: SPIRV-Cross JSON CB member
is `_m0`; `cb0_0_m0` is the flattened generated HLSL name. The original CB slot
belongs to the Uniform variable OpName `cb0_0`, resolved via OpTypePointer→struct,
not the member name or descriptor enumeration order. Fixed source resolves that
exact lineage; candidate named members/offsets/full sizes still strictly checked.
Updated synthetic fixture to use actual public translator shape; wrong original
slot remains rejected. All10 W5 tests pass locally; actual four original and four
candidate descriptor modules normalize and pass Vulkan1.1 spirv-val locally.
No Vulkan numerical success is claimed until replacement hosted run completes.
No installed shader, native request, water gate or peer file changed.
