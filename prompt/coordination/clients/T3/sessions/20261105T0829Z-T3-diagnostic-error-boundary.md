# T3 independent session 20261105T0829Z-T3-diagnostic-error-boundary
Identity T3; resumed_from_session 20261105T0726Z-T3-diagnostic-integrity. Baseline HEAD 6a88e22792a974379d587969ab7ea796a8cb5d2a. Shared T3 state/MEMORY stale while multiple independent sessions exist; paused_identity_conflict, do not overwrite.

## Before-edit engineering plan
Read T_TEAM operating/restore/source rules and current T3 genuine pixel runner. Genuine run 41968665857: 76 exact/30 RGB drift from 106 authenticated pairs, not a Unity/Adreno proof. T5 repaired a newline error and CI41989640298 passed; do not repeat. Current `t3_authentic_decoded_pixel_export.run` wraps original decode, PNG load, parity, **and diagnostic classify** in one `except (NotImplementedError, ValueError, TypeError, OSError)` which silently converts a diagnostic classifier failure into `UNSUPPORTED_MODE`, falsely blaming source decoding. A genuine mismatch must remain fail-closed and preserve provenance.

Implement a strict boundary: keep decode/export errors classified separately from optional diagnostic failure; fail closed with INCONCLUSIVE on diagnostic error rather than fabricating unsupported texture. Add adversarial synthetic tests that inject a diagnostic ValueError and prove it cannot be reported as UNSUPPORTED_MODE. Do not trigger the 2.26GB export unless the tests justify a new bounded run and no conflicting T jobs. No game assets, settings, audio, touch, save, shader or other agents' workflows changed. RENDER-002 OPEN, NOT_READY 0/3.

## Checkpoint
PLAN_RECORDED. Follow-up pending.
