# T3 scope 20261110T1828Z-T3-scheduled-guid-regex-fix-n4q7
origin=scheduled; issue_id=RENDER-002; status=active
baseline_file_sha=7c5fd058f2a30f9a2d1fcc6e4ae2d7ddfcb0ad96
intended_files=scripts/t3_unity_guid_link_audit.py; tests/test_t3_guid_audit_regression.py; prompt/coordination/clients/T3/sessions/20261110T1828Z-T3-scheduled-guid-regex-fix-n4q7.md
experiment_key=guid-audit-regex-escape-literal-backslash-v1
resource_key=none (source-free local regex audit)
Hypothesis: raw regex patterns contain two literal backslashes, making GUID and inline Unity references invisible. Fix only pattern escaping and add explicit regex contract tests; do not modify game assets.
Inherited: 20261110T1730Z-T3-scheduled-guid-fixtures-p8r4; source-free tests were published but not executed. Phone artifact 42058825739 proves world/save/re-entry only. No Unity or GPU acceptance claimed.
No shared build/CI requested; T4 mouse and T5 resolution untouched.
