# T5 independent work — CI42058541334 exact failure

session_id: 20261105T1646Z-T5-scheduled-c71e
origin: scheduled
base_sha_observed: 5081a37400dc9c6cd2364ba8af31da4e1650c9fb
scope: read-only historical job-log analysis; dedicated new work/session files only; no T3 source edits
experiment_key: T5|CI42058541334|job127353489260|exact-stderr|f224c5ab
shared_resource: none; no CI dispatch

## Hypothesis
Earlier metadata-only report could not isolate failing command. Decode job logs to distinguish py_compile from unit assertion, and compare against live test to avoid duplicating T3's fix.

## Proven evidence
- https://github.com/alwansan/raf/actions/runs/42058541334, immutable f224c5ab1093ec73f694e8d9dc8be61419174a93, job 127353489260.
- Job logs show py_compile succeeded; test_t3_stage_io_drift 5/5 passed; test_t3_original_top_shader_fourpass_translation had exactly one failure of 20 tests: test_opt_in_scheduled_stage_io_classifier_asymmetric_drift, line 221, expected io_drift_inputs_added_locations=4 but actual=8. Failure is assertion mismatch, not translator/runtime/Unity failure. Later suites were skipped due to set -e.
- Live test at HEAD 5081a374 now expects added inputs=8 and outputs=8, removed inputs=4 and outputs=4, and documents one removed plus one added per relocated field. This directly corrects the stale expected count. Do not re-edit T3 test.
- Newer https://github.com/alwansan/raf/actions/runs/42062161784 completed SUCCESS for authentic fourpass opt-in synthetic controls; this does not prove original shader semantic parity.

## Result / boundary
Historical CI failure root assertion identified; current source already contains expected-count correction. No game files changed, no device/GPU/water claims. T3 owns test suite; do not duplicate or relaunch.

## Next
Check any future T3 regression against exact failing test and immutable SHA; otherwise move to independent native/asset integration evidence, avoiding T1-T4 scopes.
