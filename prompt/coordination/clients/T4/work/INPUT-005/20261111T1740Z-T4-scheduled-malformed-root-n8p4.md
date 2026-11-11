# T4 scope — malformed root input
session_id: 20261111T1740Z-T4-scheduled-malformed-root-n8p4
origin: scheduled
baseline_head: 408fdce57133ee7bff3d12609b3136d1e2690845
issue: INPUT-005 OPEN
experiment_key: T4-INPUT005-ROOT-SCHEMA-20261111
files: scripts/t4_capture_gap_classifier.py; tests/test_t4_capture_gap_classifier.py; this work file; separate T4 session
hypothesis: JSON root may be list/null/string and classify(summary) calls .get unconditionally, raising AttributeError instead of returning invalid evidence. This can break triage on a mixed/corrupt CL export.
method: reject non-dict root as invalid evidence, add regression for null/list/string; retain existing per-button semantics; no gameplay or device acceptance inferred.
shared_resources: none; no CI/Unity build requested.
owner_acceptance: Artifact 42058825739 successfully entered local world, saved, exited and re-entered .rgd on phone; delivery packaging failed separately.
coordination: T5 owns Resolution/visible controls; T4 owns physical mouse callback/reader evidence; keyboard and save remain untouched.
next: run Python regressions and obtain same-build Android/Unity mouse traces for actual input fix.
