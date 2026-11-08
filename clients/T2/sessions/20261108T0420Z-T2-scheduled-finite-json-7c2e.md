# T2 session 20261108T0420Z-T2-scheduled-finite-json-7c2e
origin: scheduled
base_sha: 695799cf4b7feaacd6abd90c3c9f466563e6df59
resumed_from: 20261108T0322Z-T2-scheduled-json-boundary-k7p2; 20261108T0222Z-T2-scheduled-fullschema-negative-q8m4
issue: WATER-001 OPEN
work: prompt/coordination/work/WATER-001/20261108T0420Z-T2-scheduled-finite-json-7c2e.json

## Owner evidence first
Read docs/DEVICE_FEEDBACK_42058825739_AR.md and its CL snapshot links. Owner installed artifact from run 42058825739 and entered, saved, exited and re-entered a world. Publication failed; water/FFT remains unproven. 220911-559: 23884 pass / 3850 FFT kernel errors; 230108-327: 39132 / 6026. Do not regress working local world, sound or Settings. T3 owns fire/candles/smoke; T4 mouse; T5 three buttons and Resolution.

## Distinct engineering scope and result
Identified Python json.load parse_constant catches literal NaN/Infinity but NOT a valid JSON number with huge exponent (1e999) that overflows to float infinity. scripts/t2_foam_pass_crosscheck.py now installs finite_float for both original and independent role JSON inputs, rejecting overflow before validation. Added four source-free regression cases including full-schema original CLI input and successful control. No private original assets or source symbols included.

Commits: scope d18b2a36ec99b00aa267d2da4d1f4460dbb7e5b8; source 78e3b0f30cda69c03e63ed8b84ec663affe39471; tests dfd493f6878a6eb8f4140a6536fb4ec0ff30ccf4; fixture import correction 69988aec2f8e9c86dcb21876ff9ef73ac224665d.

## Evidence limits and next
A standalone Python check confirmed 1e999 raises nonfinite_json and 1.25e2 parses as 125.0 with the proposed parser. Repository integration suite NOT executed because container GitHub DNS resolution failed; do not claim CI/test PASS. No Unity, ShaderLab, .meta, GUID, build, T3 files or device pixels changed. Run python -m unittest discover -s tests -p 'test_t2_foam_pass_crosscheck*.py' on checked-out SHA, then continue authenticated Foam pass1 producers and CB0/ShaderLab linking rather than repeating source-only controls. No duplicate native CI requested.
