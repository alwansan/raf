# T2 scheduled checkpoint 20261110T2019Z-T2-scheduled-foam-cli-ci-verified-n8q3
origin: scheduled
base_sha: 16b3097b17800679e28540f696949a89b6fc1375
issue: WATER-001 OPEN; NOT_READY 0/3

## Owner-first evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: owner entered/saved/reentered world from run 42058825739 artifact; packaging publish failed; water invalid-pass and FFT remain. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; do not regress to APK86.

## New verified finding
The newly added source-only workflow .github/workflows/raft-t2-foam-evidence-cli-gate.yml actually ran on commit 849ee58269b6c0b3b71919c552cbf54ab05b75bf. Run https://github.com/alwansan/raf/actions/runs/42884997890 is completed SUCCESS (created 2026-11-10T19:24:44Z). It runs unittest discovery for test_t2_foam_evidence*.py; this establishes the CLI regression gate was executed, superseding prior 'not run' notes. It does NOT prove producer invocation, source Foam binding, Unity or phone behavior. Existing workflow explicitly prints publisher_integration=UNKNOWN.

## Cross-team boundaries
T4 owns physical mouse button/pointer capture; T5 owns Resolution/three buttons and packaging. T3 owns fire/candles/smoke. T2 remains Spectrum/Foam/Blur cross-pass render target identity, CB0 and ShaderLab proof. T1 kernel6. No changes to their files or jobs.

## Next executable engineering
Identify actual CI report-producing command and its upload-artifact step; enforce strict sanitizer before upload and test fail-closed with hostile report. Separately prove Foam pass0 output RenderTexture instance equals pass1 sampled input in original managed control flow (not just register identity), with fixed ZIP2 provenance and safe aggregates. No full-game build request until gates.

No new Unity/Android run and no readiness claim. Evidence read from GitHub Actions REST, workflow YAML and owner report.