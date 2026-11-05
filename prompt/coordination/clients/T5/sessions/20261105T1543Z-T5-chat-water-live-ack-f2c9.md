# T5 — authenticated renderer water limitation gate drift

- session_id: `20261105T1543Z-T5-chat-water-live-ack-f2c9`
- origin: `chat`
- status: `active`
- base_sha: `523565b107732b5817056feeac0d90cd3b3877a9`
- resumed_from_sessions: `20261105T1508Z-T5-chat-native-retry-c2b7`, `20261105T1453Z-T5-scheduled-6e82`
- issue: INTEGRATION-001 (crosses WATER-001 but does not take over T1/T2 source ownership)
- work: `prompt/coordination/work/INTEGRATION-001/T5-20261105T1543Z-T5-chat-water-live-ack-f2c9-water-ack-source-gate.json`
- experiment_key: `T5|CI42052375742|original-water-gate-live-v1|DepthCopy-false-Blur-true|exact-ack-to-existing-guard`
- resource_key: `t5-isolated-python-water-ack-validation` and only later one `raft-native-engine-feature/android-native-port` if source-only CI passes and no conflicting heavy jobs
- status and run_url: source-only test planned; original [CI42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) **completed failure** on immutable `b0c4b4c05011d915cd845259f06b5f80ee368092`.

## Verified live source failure

The original native request/Unity license both succeeded, full original Mesh position audit 4708 entries was completed, and graphics source restoration/export progressed through material/source stages. Its first real failed native step was `Authentic water gate (strict) or exact documented trial limitation`, not Unity Editor compilation. Job `127331915972` shows original strict water inspector source report: `UltimateWater/Utilities/Blur (Subsurface Scattering)` now satisfies required pass count 2, whereas `UltimateWater/Depth/Depth Copy` has two candidate SubShaders with pass counts [6,3] against required >=4 per active subshader and is unsatisfied. Other still-unmet: Foam/Global 1/2, Spectrum 1/6, no authentic water FFT kernel identity, no candidate compute. Existing `.github/raft-native-build-request.json` still acknowledges Blur as missing and omits Depth. `scripts/record_documented_water_limitation.py::check` compares the exact sets and raised `ValueError: Documented water limitations do not exactly match the live unmet conditions`. This is correct fail-closed logic; do not weaken it or fake original water readiness.

Release state: no signed APK/OBB/XAPK from run42052375742. Three small renderer staging artifacts are not native delivery. Last confirmed actual game release remains APK86. No new phone or same-world RGD proof; project NOT_READY 0/3.

## Implementation boundary

Build a **source-free genuine-run aggregate replay** invoking the actual `unmet_conditions` and `check` implementation. Negative controls: old request fails exactly, corrected set passes as experimental-only with `strict_water_gate=not_passed`, partial/extra/drifted conditions fail, no `authentic_water_kernel_identity_verified=true` or device claim. Use the exact public 5 shader names only and safe booleans: no shader source/bytecode, GUIDs, private identifiers, actual original asset material or RGD. Preserve source guard and its tests. After successful isolated CI and another overlap audit, **one** request update may use the corrected 5 conditions. No other active T1/T2/T3/T4 work touched and no duplicate Unity builds.

next_step: write fixture, independent replay/tests and opt-in CI; inspect logs; then update native request exclusively after exact match evidence. Record immutable source and outcome in separate event/experiment/work.
