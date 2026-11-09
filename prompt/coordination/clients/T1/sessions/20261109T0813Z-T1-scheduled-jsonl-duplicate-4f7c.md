# T1 scheduled — FFT JSONL duplicate-key evidence integrity

- session_id: `20261109T0813Z-T1-scheduled-jsonl-duplicate-4f7c`
- origin: `scheduled`
- issue_id: `WATER-001`
- baseline: `scripts/t1_fft_dispatch_pair_audit.py` blob `905e4270c067fca51a51eb191bccf25571314f86`
- resumed_from_session: `20261109T0718Z-T1-scheduled-pair-presence-b8e4` (prior reported checkpoint); state/MEMORY remain secondary.
- owner evidence: [5 Nov device feedback](../../../docs/DEVICE_FEEDBACK_42058825739_AR.md) and [8 Nov mouse/water update](../../../../apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md).
- scope: `prompt/coordination/work/WATER-001/T1-20261109T0813Z-T1-scheduled-jsonl-duplicate-4f7c.json`; no changes to T2–T5, touch, Settings, audio, original shader bytes, or .meta.
- experiment_key: `T1-FFT-JSONL-duplicate-object-keys-input-hardening-v1`.

## Actual changes
- `38bae453c14998e7eeb495dad21a0430d34246a6`: reject duplicate JSON object keys at parse time (including nested objects), preventing ambiguous event/identity evidence being silently overwritten by Python JSON parser.
- `a54f48243b9873027683ac458c3b19c7ccf414d4`: four synthetic unittest controls: top-level duplicate, nested duplicate, valid Before/After pair without GPU claim, mismatched kernel.
- Work-plan commit `816f667fffcb746ac8212c13531791a84421ff3e`.

## Verification and boundaries
- Connector read of live source and commits; tests **authored but not executed** in this environment because the container cannot resolve github.com and has no checkout. Do not claim CI pass or Android GPU proof.
- Source integrity hardening only; it does not establish Unity `FindKernel`, GPU `Dispatch`, numeric Vulkan-vs-Unity agreement or authentic FFT shader restoration.
- 42058825739 phone world enter/save/re-enter is owner-confirmed for that Artifact only. 8 Nov CL report: 74,359 water-pass and 11,165 FFT-kernel errors; independent session, do not add counts to 5 Nov logs.
- WATER-001 OPEN; NOT_READY 0/3.

## Next
Run `python3 -m unittest discover -s tests -p 'test_t1_fft_dispatch_pair_jsonl.py' -v` in repository CI/checkout, confirm actual trace JSONL shape from CL, then collect same-build shader GUID/kernel name/FindKernel result/Dispatch groups/resource bindings and compare first numeric FFT divergence with Vulkan. Coordinate unified mini lab with T5; do not launch redundant full Unity build.
