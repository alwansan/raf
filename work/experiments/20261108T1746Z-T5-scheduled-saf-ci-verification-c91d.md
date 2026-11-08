# T5 — scoped CI verification
session_id: 20261108T1746Z-T5-scheduled-c91d
origin: scheduled
issue_id: T5-SAF-PACKAGE-IDENTITY
base_sha: e85b778fccc7ed458e9f155aa23a5e84cc1c2e4a
intended_files: work/experiments/20261108T1746Z-T5-scheduled-saf-ci-verification-c91d.md; clients/T5/sessions/20261108T1746Z-T5-scheduled-c91d.md
experiment_key: t5-saf-stream-sha256-8b98dff0-jdk
resource_key: none
status: verified_source_only

Live CI run https://github.com/alwansan/raf/actions/runs/42502155293 completed SUCCESS at 2026-11-08T16:53:54Z for 8b98dff0d371486aab03e3aae56f2422c1ad7a05. All digest steps succeeded: T5 declarative testpack validation, compile/run streamed SHA256 regression without Android emulator, and static async SAF handoff check. This closes prior waiting_ci for source tests only; it is NOT phone validation, APK/OBB identity or on-device hash.

Current unified mini policy supersedes five independent APKs. SHARED_BUILD_READINESS.md shared-20261108-r1: no NEED_BUILD yet, T2 WAITING_MERGE, other workers NOT_REVIEWED. TEST_CENTER has no published shared APK. Do not dispatch duplicate build. T4 owns mouse button events. Next: check actual unified driver change and worker request before one mini build; then device SAF hash and signed APK/OBB manifest verification, Resolution and right controls.
