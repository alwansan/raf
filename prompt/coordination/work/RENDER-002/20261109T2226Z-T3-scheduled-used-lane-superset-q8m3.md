# T3 RENDER-002 — used vs declared SPIR-V lanes

session_id: 20261109T2226Z-T3-scheduled-used-lane-superset-q8m3
origin: scheduled
branch: feature/android-native-port
experiment_key: smoke34-used-lane-subset-declared-spv-v1
resource_key: source-only-python-no-unity-no-zip2
base_head: ec86477dd24a2299be77a9a9fbb9ffefbd06c3f0

## Hypothesis and scope
Authenticated original smoke34 reports 22 PS-used lanes and 28 declared SPIR-V lanes (CI42696526193). The synthetic provenance gate incorrectly demanded equality of mapped *used* lanes and all declared SPIR-V lanes, causing a false incomplete_coverage verdict even if a correct mapping is supplied. Touch only scripts/t3_smoke34_location_provenance_gate.py and tests/test_t3_smoke34_location_provenance_gate.py; do not touch shader assets, CI, other T-team scopes or private data.

## Change and evidence
Updated validator to require injective, complete mapping of all original used lanes into a subset of declared SPIR-V lanes, while preserving strict uniqueness and membership checks. Return STRUCTURAL_INJECTION_ONLY and explicit unused_reflected_lanes; never claim semantic authenticity. Two new regression tests for valid unused declared lanes and invalid undeclared mapped lane. Source commits 0f3abc478cc0497cdcecd72a94cd0ad6fb139f10 and dca85c845448eb916e9ee4cd174c9a8d928e6de8. Tests have not yet run in CI; previous 57/57 CI42696526193 applies to previous source only.

## Limits and next
Source-only logic fix, not original mapping or device rendering. Run isolated Python tests, then inspect original DXBC instruction-to-SPIR-V variable dataflow. RENDER-002 OPEN, NOT_READY 0/3. No duplicated native builds.
