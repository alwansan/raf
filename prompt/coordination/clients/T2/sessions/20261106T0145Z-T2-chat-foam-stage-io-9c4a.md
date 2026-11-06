# T2 chat — original full Foam ShaderLab Vulkan vertex-fragment interface

- session_id: `20261106T0145Z-T2-chat-foam-stage-io-9c4a`; origin: chat; status: active
- base_sha: `16182a34039acafdb81552afe726abfeafb63c93`
- resumed_from_sessions: `20261106T0131Z-T2-chat-embedded-foam-hlsl-c4f7`, `20261106T0120Z-T2-scheduled-json-evidence-7c91`.
- work: `prompt/coordination/work/WATER-001/T2-20261106T0145Z-T2-chat-foam-stage-io-9c4a.json`; issue WATER-001.
- immutable source `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, source `sharedassets0.assets` 115978112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Last real T2 original [CI42144036981](https://github.com/alwansan/raf/actions/runs/42144036981) SUCCESS 4/4 embedded stage HLSL→SPIR-V Vulkan1.1, 27 synthetic tests. This does NOT establish cross-stage attribute/varying location/type compatibility.
- Objective: private `spirv-cross --reflect` after extracting the same two embedded original Foam programs from completed private ShaderLab, validate both pass VS output→PS input numeric ABI, including zero/unknown/duplicate/array/builtin guards. Only safe counts/categories, no original identifiers/ShaderLab/raw programs published. Failed matching is a source-backed integration blocker, not a device claim.
- Files `scripts/t2_foam_embedded_stage_io.py`, `tests/test_t2_foam_embedded_stage_io.py`, isolated `.github/workflows/raft-t2-foam-private-shaderlab-candidate.yml` and own records.
- Do not edit other T clients' work or mutable game .shader/.meta/GUID, no heavy Unity/native build or job cancellations. Sound/Settings preserved.
- next_step: synthetic ABI tests, source-pinned original workflow, update experiment/evidence and WATER-001 not-ready boundary.
