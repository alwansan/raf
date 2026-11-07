# T4 scoped work — 20261107T0245Z-T4-scheduled-release-permissions-p4x8
origin: scheduled
owner: T4
baseline_sha: f0b88b20f43d9073c600d80ed83bd6770a9fd9c3
experiment_key: T4-release403-permission-provenance-20261107
shared_resource: none; no native workflow requested
files: prompt/coordination/work/20261107T0245Z-T4-scheduled-release-permissions-p4x8.md; prompt/coordination/clients/T4/sessions/20261107T0245Z-T4-scheduled-release-permissions-p4x8.md
hypothesis: HTTP 403 in release creation is an authorization/policy failure, not a Unity build failure. Distinguish effective token permissions from workflow YAML declarations without disclosing tokens.
source: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42296450023; prior T4 session 20261107T0135Z-T4-scheduled-release403-a6q9.md.
constraints: no changes to release workflows, .rgd, mouse/keyboard, or existing CI; no redundant build. T5 owns release integration.
acceptance: verify job permissions and trigger context from failed run; isolate exact failed API call, distinguish 403 from 404/422, and only then propose minimal change.
status: investigation only; no source or device validation claimed.
