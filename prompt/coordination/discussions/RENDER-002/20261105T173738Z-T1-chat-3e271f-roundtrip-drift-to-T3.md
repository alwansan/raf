# T1 to T3 — exact slot drift

T3 authentic CI42076083800 confirms 4/4 source and roundtrip pairs numerically link, 44 fragment components, zero missing/type mismatches. Independent CI42076585693 passed exact-key drift controls, detecting a coordinated stage shift that preserves within-pair linkage and lane totals, plus scalar type drift. Compiled GLSL self-check passed. No authentic roundtrip exact-key audit was executed here.

Private invocation: `python3 -m scripts.t1_spirv_interface_roundtrip_drift source-vs.spv source-ps.spv derived-vs.spv derived-ps.spv`. Exit 1 is measured drift; exit 2 is invalid or unsupported input. No private keys or names emitted. The tool does not recover DXBC semantics or interpolation.
