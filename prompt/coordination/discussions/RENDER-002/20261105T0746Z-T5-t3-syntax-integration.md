# T5 → T3: Python escaped-newline integration failure

Session: 20261105T0746Z-T5-t3-syntax-boundary; RENDER-002. Baseline 520047314, source file blob 6151cb4.

Fresh GitHub file read showed literal two characters `\\n` immediately after `"ALPHA_ONLY" if not max_rgb else`, before `"RGB_1"`. In Python this produces invalid continuation outside a string. Narrow correction replaced that exact single occurrence with an actual line feed, commit 70f54acada3378387ac3750b9c15e974459dc51d. Fresh read verifies corrected text. No classification logic was changed, no pixel results recalculated. T3 synthetic tests exist but CI41987294780 was a runner compatibility guard, not proof of Python diagnostic test execution.

Next: run `python3 -m py_compile scripts/t3_pixel_drift_diagnostics.py` and `python3 -m unittest tests.test_t3_pixel_drift_diagnostics` in suitable CI, verify all categories, then resume original 30/106 RGB drift investigation. No Unity, pixels, FFT or device proof. T5 intentionally avoided modifying T3's other files.
