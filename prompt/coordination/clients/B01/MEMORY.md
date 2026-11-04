# B01 — engineering memory

Session: `20261104T2105Z-B01-water-contract` (2026-11-04 UTC).

Goal: Independent WATER-001 FFT kernel/dispatch contract investigation, preferring real shader fidelity over fake or clamped kernels. Audio and Settings owner-confirmed; touch deferred.

Read live B_TEAM/PROMPT_AR.md, README.md, TEMPLATES.md, OPERATING_MODEL_AR.md, REVIEW_2026-11-04.md and SUMMARY.md; inspected AGENTS.md and current handoff; branch HEAD at entry `6c966c63ba2eb303fc8a419ef7dd629230e81450`. Review identifies APK86 release `android-early-test-41812889049-1` (source d181ee7), CL log sample contains kernelCount=0, missing pass counts; no new phone source proof. Current Action `41911656507` in progress on LOCAL-005; do not cancel.

Hypothesis: Original FFT shader names/bindings or dispatch mismatch may be isolated through repo code and SHA-pinned source evidence; source tests do not prove GPU pixel equivalence. No shader dummy/clamp permitted.

Work: `prompt/coordination/work/WATER-001/B01-20261104T2105Z-B01-water-contract-fft-kernel-contract.json`.

Next: Read relevant GPU FFT code and existing validation and current B worker contributions, run narrow tests, implement safe verified change or record falsified hypothesis. Preserve original data and run statuses.
