# T5 scheduled checkpoint — 20261111T2351Z-T5-scheduled-badging-6d72
session_id: 20261111T2351Z-T5-scheduled-badging-6d72
origin: scheduled
resumed_from_session: clients/T5/sessions/20261111T1848Z-T5-scheduled-graph-bounds-c9e2.md
base_sha: b2cc78a3aeab615a5ddc63fa70c52512f38c8a9f
scope: clients/T5/work/20261111T2351Z-T5-scheduled-badging-6d72.md
issue_id: APK-OBB-BADGING-UNIQUENESS
status: waiting_ci

Read owner docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM live protocols, previous T5 session and live Actions. The owner proved world/save/reentry on original 42058825739 only; original signed APK/OBB parity and new performance cohort remain unresolved. T4 owns physical mouse. No touch layout/Settings edits, no Unity build, no cancellation.

Source defect: scripts/t5_verify_apk_obb_pair.py used BADGING.search and accepted first valid aapt package line even when later package lines contradicted it. Commit e3d9689f4f69d56ce5510f5f4842766a167a9b9a replaces first-match acceptance with exactly one package declaration. Commit 55ec3bfc37609252fc5ab8ec97d5223e9ce9a161 adds positive control and three adversarial duplicate/conflicting declarations using synthetic manifests and mocked ZIP structural checks. This is a verifier hardening change, not signed-byte proof. No real APK or OBB payload published.

Verification: workflow 43123065340 started on intermediate SHA e3d9689, in_progress when inspected. New test SHA 55ec3bfc not yet proven by CI. Local container could not resolve raw.githubusercontent.com; do not claim local unit test PASS. Concurrent GT Actions 43123035437 in_progress; leave untouched.

Next: inspect current HEAD and CI for final SHA 55ec3bfc; run python -m unittest discover -s tests -p 'test_t5_verify_apk_obb_pair_badging.py' -v on available runner, resolve any failure, then test actual signed pair if obtainable. Check overlapping GT and T4 work before edits. No new phone performance measurement, NOT_READY.
