# T5 independent post-fix verification scope
session_id: 20261111T1653Z-T5-scheduled-ci-postfix-71d4
origin: scheduled
baseline_head: f1f7b1330a941af60827ea5a7dbfa2a22821b57a
issue_id: CI-T2-TEAM-SUMMARY-43028966025
experiment_key: t5-postfix-readonly-log-43028966025
resource_key: none
intended_files: work/20261111T1653Z-T5-scheduled-ci-postfix-71d4.md; clients/T5/sessions/20261111T1653Z-T5-scheduled-ci-postfix-71d4.md
status: evidence_collected

Hypothesis: last T2 summary run predates the targeted missing event_id repair. Distinguish failed old run from a post-fix regression without rerunning T2's workflow. No T4 mouse, T1/T2 shaders, Settings or Unity files edited.

Evidence: job 130550744042 traceback at scripts/refresh_b_team.py:32 reports missing identity in prompt/coordination/B_TEAM/events/T1/20261109T2002Z-T1-chat-cl-t105-proof-6e8a.json. Current branch file contains event_id equal to session_id, and refresh_b_team.py normalizes event_id into id. GitHub Actions branch list still shows latest run 43028966025 at pre-fix head 6485e86c, so no post-fix CI pass is proven. Next: test generator on current tree or let T2's next legitimate run verify; do not duplicate.

Original device 42058825739 world/save/reentry is owner-confirmed only. APK/OBB byte identity and current device performance remain unknown. Resolution original serialized callback unknown. NOT_READY 0/3.
