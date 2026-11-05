# T3 chat — independent source-free VS/FS SPIR-V component coverage

- session_id: `20261105T1633Z-T3-chat-vf-component-coverage-b71d`
- origin: **chat**; owner: **T3**; issue: **RENDER-002 OPEN**; readiness **NOT_READY (0/3)**.
- branch: `feature/android-native-port`; base_sha: `466b59718e271a5ca7071258b2f5938f34e702e9`.
- resumed_from_sessions: `20261105T1607Z-T3-chat-spv-name-location-7c2d` (genuine source Shader48 CI42062573338), `20261105T1625Z-T3-scheduled-dxbc-contract-8f2c` (new scheduled DXBC signature contract).
- work record: `prompt/coordination/work/RENDER-002/20261105T1633Z-T3-chat-vf-component-coverage-b71d.json` registered **before code edits** at commit `503684c741f475b9d0beaf863b09ed6ac1c7d2de`.
- experiment_key: `T3-SPIRVCross-VSPS-Location-Component-typed-coverage-sourcefree-v1`; resource_key: null (light independent CPU test).
- intended files registered: `scripts/t3_vf_spirv_component_coverage.py`, `tests/test_t3_vf_spirv_component_coverage.py`, `.github/workflows/raft-t3-vf-spv-component-coverage.yml`, and this session/experiment/event.

## Verified baseline and why this scope

Authenticated [CI42062573338](https://github.com/alwansan/raf/actions/runs/42062573338) showed 921-use original Shader48 / 4 exact linked V/F pairs with 8 real DXBC stages valid after Vulkan SPIR-V and HLSL roundtrip, but compiler-generated labels retained 0/34 input and 0/29 output label identity. Name/Location/type multiset cannot prove original semantic correspondence. The parallel scheduled T3 cycle 16:25 handles `scripts/t3_dxbc_signature_contract.py` and DXBC signature record validation. This chat deliberately avoids those files and instead prepares independent VS↔FS `Location+Component+scalar-family` overlap evidence. At check, T5 full native [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) remained in progress inside Unity Editor import; not interrupted, duplicated or cancelled.

## Exact implemented change

- [classifier](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/t3_vf_spirv_component_coverage.py) commit `51f0e695c0474e095cb3f6592632b18a26d17094`: accepts only sanitized bounded SPIR-V reflection records, same Location and component lane, vector/scalar-family matching, rejects lane overlap, bad schema, malicious user labels, fake booleans, cross-location unsupported packing. Unknown matrix/array/double layout => INCONCLUSIVE, not a spurious pass.
- [17 synthetic regression controls](https://github.com/alwansan/raf/blob/feature/android-native-port/tests/test_t3_vf_spirv_component_coverage.py) commit `e17ffd6d19a0907cf3e0333b2a7a09beda33a553`.
- [isolated short path-scoped GitHub Actions workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t3-vf-spv-component-coverage.yml) commit `920d52a9d83f051c4e758c2977fb4681490a233d`; no Unity, external binary or ZIP2 pull, no other agent's workflow touched.
- **[CI42065947764](https://github.com/alwansan/raf/actions/runs/42065947764) completed SUCCESS** at 16:35 UTC: `python3 -m py_compile` passed, `PYTHONPATH=scripts python3 -m unittest discover -s tests -p 'test_t3_vf_spirv_component_coverage.py' -v` **17/17 PASS**. Job `127379935644`.

## Evidence boundaries and handoff

No original DXBC bytes, private HLSL, DXBC semantic/register mapping, shader labels, .meta/GUID, Unity project resources, scenes, FMOD, Settings, touch, save files, device images or game build changed. `STRUCTURAL_CANDIDATE_ONLY` means structurally compatible *sanitized SPIR-V* component coverage, **not original DXBC semantic or interpolation match, correct rendered pixels or repaired white materials**. 0 real original shader programs fed into this new classifier yet. RENDER-002 stays OPEN; NOT_READY.

Next engineer: add fail-closed private SPIRV-Cross reflection adapter that strips all original/generated labels and correlates only authenticated `Location`, `Component` and types with existing original four-pass source reflection. Run one distinct actual 921-use Shader48 source/roundtrip 4-pass experiment on pinned ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385` after checking CI resource overlap. Compare source V/F and derived V/F summary privately; never publish shader/source/generated names or hashes. Schedule cycle can independently extend real DXBC signature semantic parser. No false game/pixel/readiness claim.
