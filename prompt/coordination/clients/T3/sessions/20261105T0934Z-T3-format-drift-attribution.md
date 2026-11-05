# T3 independent session 20261105T0934Z-T3-format-drift-attribution
Identity T3. Resumed from 20261105T0829Z-T3-diagnostic-error-boundary. Shared T3 state/MEMORY is stale and same-name concurrent sessions cannot be excluded: paused_identity_conflict; do not overwrite shared state/MEMORY.

## Before-edit plan
HEAD 03c635950540cb9a9346247ff547cf0a5849090e. Latest decoded-controls CI41994969127 SUCCESS at SHA6448bdd3; previous 41968665857 original-to-export 106 pairs yielded 76 exact/30 RGB drift. No current active Actions among last 12 runs; T2 latest genuine Foam CI42001669563 SUCCESS. Original source SHA pins remain workflow-owned; no fresh bytes fetched here. T1 FFT import CI41978496060 FAILED; T4 source controls CI41996790205 SUCCESS. Do not cancel any job or repeat heavy ZIP2 export.

Observed actionable diagnostic gap: t3_pixel_drift_diagnostics.aggregate emits only marginal distributions for format and drift. Those marginals cannot establish whether the 30 RGB mismatches concentrate in a texture codec, so running another 2.26GB authentic export with unchanged diagnostics would not answer the next causal question. Implement bounded non-identifying format-by-drift grouped counts (no IDs, hashes, filenames, raw pixels or individual rows) and negative controls, retaining fail-closed validation. Use a distinct small-group bucket to avoid exposing singleton format populations; do not infer decoder bug or device correction from correlation.

Planned files: scripts/t3_pixel_drift_diagnostics.py, tests/test_t3_pixel_drift_diagnostics.py, this session. No source game assets, GUID, Settings, audio, touch or .rgd changes. RENDER-002 OPEN; NOT_READY 0/3.
