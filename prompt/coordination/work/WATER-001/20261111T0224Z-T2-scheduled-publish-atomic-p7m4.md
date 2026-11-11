# T2 independent scope — 2026-11-11 02:24 UTC

session_id: 20261111T0224Z-T2-scheduled-publish-atomic-p7m4
origin: scheduled
issue_id: WATER-001
baseline_sha: da188e77dc04495dc158dc1ae0e8080a990f97e5
status: waiting_ci
experiment_key: T2-FOAM-PUBLISH-ATOMIC-v1:strict-aggregate-ingress:source-only
resource_key: none; no Unity/ZIP2/CL writes
intended_files: scripts/t2_foam_publish_aggregate.py; tests/test_t2_foam_publish_aggregate.py; prompt/coordination/clients/T2/sessions/20261111T0224Z-T2-scheduled-publish-atomic-p7m4.md

## Evidence and hypothesis
Owner device run 42058825739 (source e9c358e) proves world save/re-entry but has 23,884 water pass errors and 3,850 FFT kernel errors in 220911-559. Existing CI gate verifies strict aggregate parsing and product JSON shape, but its workflow says publisher_integration=UNKNOWN. Hypothesis: a separate fail-closed publication adapter can enforce sanitizer before writing a publishable file, with atomic destination replacement and no partial output for invalid input. This is not proof that legacy producers invoke the adapter.

## Boundaries
Read-only CL and original ZIP2. Do not touch T3 effects, T4 mouse, T5 resolution or shared Unity. No private shader data in artifacts. No CI dispatch. Do not claim ShaderLab, CB0, GPU or phone proof. Recheck HEAD before expected-SHA publish.

## Implementation checkpoint
Adapter and six subprocess regressions committed at feb2e7ddca4b2a5ecc583f0c7c9e3e7e6ae918e7; CI workflow wired at 5dd745975089b10bc02c18cb51636506c054b063. No fresh run visible in Actions listing at last check. Await new CI; legacy publisher integration remains UNKNOWN.
