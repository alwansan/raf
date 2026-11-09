# T5 scheduled — strict evidence marker parsing
session_id: 20261109T0153Z-T5-scheduled-evidence-token-p6m2
origin: scheduled
status: SOURCE_FIXED / CI_UNVERIFIED / DEVICE_PENDING
experiment_key: t5-evidence-token-boundary-20261109
resource_key: none

## Restored
Read docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md and T_TEAM coordination instructions. Prior scheduled session 20261109T0002Z-T5-scheduled-evidence-boundary-k7q4.md distinguishes game artifact 42058825739 from mini-lab v13. Current initial HEAD e330628195fdc2720426735f7a929d2074acfb40. T4 mouse CI42547368125 SUCCESS; T4 remains owner of physical mouse callback work. No equivalent Unity/shared APK work initiated.

## Source fix
Found a concrete false-positive in scripts/t5_verify_shared_device_summary.py: plain substring matching accepted `not_capture=verified-GLSurfaceView-overlay-on-window`, `unverified_surface_pixels=true`, `not_gl_error=0x0`, `not_contract=true` as real capture parity. PNG regex likewise accepted trailing junk. This could misclassify fabricated/garbled evidence as valid T3 capture.

Work scope committed e9f8786821d83948d0f0b98f2c786d2fd2c725fc.
Source commit b6bd8599d8e2587af3002c929fb65d6ac040d793: whitespace key/value parser, exact expected values, reject duplicate keys, strict png_bytes and png_sha256.
Regression commit 81f2eff9e0b677395b38aad4db959a36d04e5f03: three negative cases (embedded false markers, contradictory duplicate, PNG suffix).
An isolated local reproduction of the token parser passed 4/4 assertions (valid / forged / duplicate / malformed PNG). **The full repository unittest and CI have NOT been executed in this run**; network unavailable in container, and no duplicate CI requested. New changes must be tested in actual workflow before declaring integration success.

## Limits and next
CL/test evidence from previous session: six T3 records EVIDENCE_READY require human PNG review; T4 nine NEEDS_INPUT remain unproven. This tool validates metadata only, not actual PNG pixels, on-device rendering, game APK/OBB, resolution or three buttons. No new game UI fix, no phone tests, no Unity, no build, no fabricated device pass. Owner's world/save/reentry confirmed only on 42058825739. Full game NOT_READY 0/3.

Next: run `python -m unittest scripts.test_t5_verify_shared_device_summary -v` in trusted repo checkout or existing lightweight CI; inspect new CL manual T5-02..06 and separately repair game-side right-safe-area / Resolution after checking live scopes. Do not modify T4 mouse files. 
