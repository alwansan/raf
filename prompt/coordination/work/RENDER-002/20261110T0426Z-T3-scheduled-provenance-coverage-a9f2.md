# T3 — RENDER-002 source-provenance implementation boundary
session_id: 20261110T0426Z-T3-scheduled-provenance-coverage-a9f2
origin: scheduled
baseline_head: c26c0c8c16c5306d51a294d11a441fde5b73e161
scope: source-only diagnostic review; no shared runtime files
experiment_key: RENDER-002-smoke34-dxbc-defuse-authenticity
shared_resource: none

## Read-before-action and inherited proof
Owner phone report confirms world/save/reopen on 42058825739; white raft/hand, square smoke and lighting remain. T3 prior same-instance authentic Material 41/227 TexEnv and 150 RGBA parity excludes those scoped internal pointer/UV/color losses. T3 synthetic SPIR-V gate 14 tests passed on 42728727179. Latest scheduled session 20261110T0333Z-T3-scheduled-original-provenance-source-gate-b7q2 did not extract an original def/use mapping. No source runtime change justified.

## Specific verified blocker and implementation requirement
Current scripts/t3_smoke34_location_provenance_gate.py returns STRUCTURAL_INJECTION_ONLY even when a caller fabricates a mapping consistent with all declared lanes. It deliberately has no authenticated source trace input, and does not claim to. A future proof must bind original DXBC blob SHA256, stage and variant, instruction-level source register component reads and def/use chain, compiler build SHA, SPIR-V blob SHA256 and destination location/component to the same transaction. Hashes alone are insufficient: optimization, interpolation and component packing must be traced or explicitly INCONCLUSIVE. Reused registers and unused declared SPIR-V lanes require explicit handling. Only safe counts/status should be public; raw compiled game binaries remain private.

## Acceptance criteria
For each of two original smoke34 keyword variants: authenticated source/export hashes; all 22 actually read original input components traced to output declarations or a documented optimization with evidence; no guessed matches from numeric locations or semantic names; 28 declared lanes audited separately; compare blend alpha, separate alpha, ZTest, ZWrite, ColorMask, render queue, particle material texture alpha and camera-depth context. A missing link is INCONCLUSIVE, not MATCH. CI pass is not device smoke proof.

## Coordination
T1/T2 water/FFT, T4 physical mouse, T5 resolution/delivery unchanged. No CI duplication or APK requested. No game resources, .meta, GUID, .rgd, audio or Settings changed.
