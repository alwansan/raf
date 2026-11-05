# T3 independent session 20261105T0829Z-T3-diagnostic-error-boundary
Identity T3; resumed_from_session 20261105T0726Z-T3-diagnostic-integrity. Baseline HEAD 6a88e22792a974379d587969ab7ea796a8cb5d2a. Shared T3 state/MEMORY stale while multiple independent sessions exist; paused_identity_conflict, do not overwrite.

## Before-edit engineering plan
Read T_TEAM operating/restore/source rules and current T3 genuine pixel runner. Genuine run 41968665857: 76 exact/30 RGB drift from 106 authenticated pairs, not a Unity/Adreno proof. T5 repaired a newline error and CI41989640298 passed; do not repeat. Current `t3_authentic_decoded_pixel_export.run` wraps original decode, PNG load, parity, **and diagnostic classify** in one `except (NotImplementedError, ValueError, TypeError, OSError)` which silently converts a diagnostic classifier failure into `UNSUPPORTED_MODE`, falsely blaming source decoding. A genuine mismatch must remain fail-closed and preserve provenance.

Implement a strict boundary: keep decode/export errors classified separately from optional diagnostic failure; fail closed with INCONCLUSIVE on diagnostic error rather than fabricating unsupported texture. Add adversarial synthetic tests that inject a diagnostic ValueError and prove it cannot be reported as UNSUPPORTED_MODE. Do not trigger the 2.26GB export unless the tests justify a new bounded run and no conflicting T jobs. No game assets, settings, audio, touch, save, shader or other agents' workflows changed. RENDER-002 OPEN, NOT_READY 0/3.

## Checkpoint
IMPLEMENTED, CI PENDING. The exact genuine 106-pair runner previously caught diagnose_pair ValueError in the same decoder catch and mislabeled it UNSUPPORTED_MODE. The diagnostic call is now outside that decoder exception handler; a diagnostic exception bubbles to main() which emits INCONCLUSIVE and exit 2, preserving fail-closed behavior. No genuine source/export run was repeated.

Commits: 792407ff0e8b6339343b51d6eecb30e737001990 (production diagnostic boundary), e7ca59cc87ea334a68aca71c88c61e959227aebd (two AST source controls), 6448bdd3578afb310e94946ffac52b636ac4e9cb (isolated CI wiring). GitHub connector HEAD confirmed 6448bdd3. At final CI query the newest listed decoded-controls run was 41989640298 SUCCESS at 70f54acad (T5's previous fix), not a run for new SHA. New tests are committed but NOT YET CI VERIFIED; no claim of passing them.

Prior 41968665857 76 exact/30 RGB drift remains; no new decoded pixel evidence. Scope source only; no Unity, Adreno, APK, shader, game assets, audio, Settings, touch or save changes. RENDER-002 OPEN, NOT_READY 0/3. No running Actions cancelled.

Next: inspect CI run for 6448bdd3, repair any failure; then run one bounded genuine SHA-locked source/export only when no competing heavy jobs, collect safe per-format/sRGB/alpha aggregate and diagnose 30 RGB mismatches. Do not infer a rendering fix from diagnostic control success.
