# T3 independent session 20261105T0726Z-T3-diagnostic-integrity
Identity T3 only; resumed_from_session 20261105T0625Z-T3-pixel-drift-differential. Baseline HEAD d0a8992341733a820a8422879ecb4fd61b011e2c. Shared T3 state/MEMORY remains stale (20261105T0024Z) while independent sessions exist; avoid overwriting possible parallel T3 owner.

## Before-edit plan
Authentic CI41968665857 failed closed with 76 exact / 30 RGB drift of 106 SHA-proven source/export pairs. Latest listed T1 Unity boundary CI41978496060 failed, no active jobs among last 15 at inspection; no cancellation. Existing diagnostic code conflates ALPHA_ONLY drift with RGB_1, and original runner catches diagnostic ValueError as UNSUPPORTED_MODE, obscuring source/decoder failure. Fix first error with exact tests; do not alter any original asset or CI heavy workflow. Preserve separate channel drift and no phone success claims. Then inspect new CI evidence before expensive genuine export rerun. No source images or per-object identifiers public.

Status: PLAN_RECORDED; RENDER-002 OPEN, NOT_READY.
