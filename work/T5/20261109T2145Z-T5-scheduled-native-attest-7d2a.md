# T5 independent scope — 20261109T2145Z-T5-scheduled-native-attest-7d2a
origin: scheduled
baseline_sha: 1cccb086c30ee9a8e9f36af9a7a5880ff05985e9
experiment_key: t5-native-runtime-final-staging-attestation-42696228231
shared_resource: raft-native-engine (READ ONLY; no new Unity run)
files: this work file and matching clients/T5/sessions file only; no T4 mouse or shared workflow edits.
hypothesis: The owner-directed full build fails before Unity at final staged Android runtime source-byte parity, not at Unity compile or Release permission.
evidence: https://github.com/alwansan/raf/actions/runs/42696228231 at source 6316f457dd7587db47469ebd29ec0cbc849584dd: native-request-gate PASS; unity-license-preflight PASS; reconstruct FAIL on step "T5 attest final native Android runtime source bytes (read-only)"; publish-early-test SKIPPED; delivery-result FAIL as consequence. Prior run #42296450023 had reconstruct PASS but Release HTTP403, a distinct failure.
method: Inspect scripts/t5_validate_runtime_staging_parity.py and the final project copy ordering. Compare staged Assets/RaftAndroid/Platform *.cs with android-port/Runtime/Platform/*.cs, including LocalProfileStore.cs, on the same pinned source SHA. Distinguish missing/extra names from byte mismatch and symlink/size failure. Obtain step log via authorized GitHub job log access (REST log endpoint unavailable through current connector). Fix only proven cause, add synthetic regression, then request a fresh build only after coordination and owner permission; do not rerun Unity to discover the same failure.
state: BLOCKED_ON_EXACT_STEP_LOG; source code and workflow read, no device test or package generated.
next: obtain job 129428944191 exact stderr from Actions UI/log artifact; classify exception and patch precise staging stage, not loosen fail-closed attestation.
