# T1 handoff to T3 — RENDER-002

CI42074345951 passed three synthetic controls for direct 32-bit scalar/vector VS-output to PS-input numeric Location/Component linkage: matching coverage, separate missing-component/type mismatches, and overlap/unsupported-layout rejection. Original shader modules and runtime interpolation were not tested.

Run privately with `python3 -m scripts.t1_spirv_interface_component_audit vertex.spv fragment.spv` after validating both modules. Direct BuiltIn variables are excluded. Interface blocks, arrays and non-32-bit scalar/vector formats are outside scope. A failure on an unsupported interface says nothing about its compatibility.

https://github.com/alwansan/raf/actions/runs/42074345951
