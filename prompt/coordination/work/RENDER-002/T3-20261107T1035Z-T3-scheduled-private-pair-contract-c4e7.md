# T3 independent scope — 20261107T1035Z-T3-scheduled-private-pair-contract-c4e7
origin: scheduled
issue_id: RENDER-002
base_sha: ae9390ef3e19d82865397a877d3dbb8d11f6886b
status: completed
intended_files: scripts/t3_rgb_drift_strata.py; tests/test_t3_rgb_drift_strata.py; this work file; unique T3 session file
experiment_key: t3-private-pair-metadata-contract-106-30-run41968665857
resource_key: none (no Unity/private ZIP2 acquisition)
taken_over_from: T3 20261107T0927Z-T3-scheduled-artifact-provenance-k7m2; B02/B05/B44 source-export probes
hypothesis: aggregate-only artifact cannot support per-texture format/sRGB attribution; verify safe input contract and regression on local tool before requesting new private extraction.
No source asset mutation; do not publish per-pair identities/pixels. T4 mouse and T5 display/delivery excluded.

## Outcome (2026-11-07 10:35 UTC)
- Scoped commits: 0ebf8fa0 (scope), a31ffcad (metadata coverage), 0c537820 (regression), bd60c8ac (physical CLI newline fix). Intermediate e5a9cbde made no substantive additional change.
- Added aggregate-only metadata_coverage by field and opt-in --require-metadata to reject a completely UNKNOWN field rather than silently interpreting it. Existing default behavior unchanged.
- Local equivalent-source Python unittest: 6/6 PASS; py_compile PASS. **Remote GitHub Actions has not executed on final commit**; local mirror used because connector fetch is not container checkout.
- Original 41968665857 artifact 13389400444 still has aggregate JSON only. Cannot identify which of 30 drift textures are sRGB/format-related. Need private per-pair extraction in same authenticated export invocation; publish only aggregate bins.
- No device/Unity test, no asset edits, no new XAPK. RENDER-002 OPEN / NOT_READY.
