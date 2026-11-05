# T3 independent session 20261105T0726Z-T3-diagnostic-integrity
Identity T3 only; resumed_from_session 20261105T0625Z-T3-pixel-drift-differential. Baseline HEAD d0a8992341733a820a8422879ecb4fd61b011e2c. Shared T3 state/MEMORY remains stale (20261105T0024Z) while independent sessions exist; avoid overwriting possible parallel T3 owner.

## Before-edit plan
Authentic CI41968665857 failed closed with 76 exact / 30 RGB drift of 106 SHA-proven source/export pairs. Latest listed T1 Unity boundary CI41978496060 failed, no active jobs among last 15 at inspection; no cancellation. Existing diagnostic code conflates ALPHA_ONLY drift with RGB_1, and original runner catches diagnostic ValueError as UNSUPPORTED_MODE, obscuring source/decoder failure. Fix first error with exact tests; do not alter any original asset or CI heavy workflow. Preserve separate channel drift and no phone success claims. Then inspect new CI evidence before expensive genuine export rerun. No source images or per-object identifiers public.

Status: PLAN_RECORDED; RENDER-002 OPEN, NOT_READY.

## Execution checkpoint
- f6fc6b146c4ea7719ca45efc42a9081cefcc9180: diagnostic now distinguishes ALPHA_ONLY from RGB_1; old code mislabeled alpha-only drift as RGB drift magnitude because zero max RGB met <=1. Does not change original compare_pair or fail-closed parity.
- a6a7648fc69867428e439ecee7cad47fb04fc8c8: two adversarial tests for alpha-only and transparent exact channels.
- 60c840cbb97d46c0171705f8305f5efc2c47a95d: extend existing isolated decoded-pixel-controls CI to install Pillow and execute new diagnostic controls on changes; does NOT trigger 2.26GB private original export.
- No original files, game code, shader, Settings, sound, touch, .rgd, or other agents' workflows changed. The earlier 76 EXACT / 30 RGB_DRIFT finding remains unchanged; this patch fixes future reporting integrity, not the 30 RGB mismatches.
- Pending: CI confirmation for the new isolated tests; no Unity/Adreno/device evidence. RENDER-002 NOT_READY. Next engineering question: use actual safe drift aggregates by format/sRGB/alpha to distinguish exporter/decoder/color-space causes; perform at most one new SHA-locked source export after CI and resource coordination, then fix measured cause.
