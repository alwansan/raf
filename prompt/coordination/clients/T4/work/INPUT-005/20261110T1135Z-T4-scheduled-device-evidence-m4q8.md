# T4 work 20261110T1135Z-T4-scheduled-device-evidence-m4q8
origin: scheduled
issue_id: INPUT-005
base_sha: 9bc14b73295fc139ffbf0709c4d044cbd960b99e
status: active
experiment_key: T4-native-gate-vs-legacy-consumer-CL20261109-233132-app731d7a68-source9bc14b73
resource_key: none (read-only CL, source-only audit)
intended_files: prompt/coordination/clients/T4/work/INPUT-005/20261110T1135Z-T4-scheduled-device-evidence-m4q8.md; prompt/coordination/clients/T4/sessions/20261110T1135Z-T4-scheduled-device-evidence-m4q8.md
hypothesis: CL shared test summary lacks actual captured-device traces; do not infer native pointer-capture denial from NEEDS_INPUT. Separate source gate from legacy consumer evidence, and preserve existing signed-world save success.
observed: source HEAD 9bc14b73295fc139ffbf0709c4d044cbd960b99e; last T4 source CI 42776921454 success; CL/test/shared-20261109-233132-554663211 contains six T3 PNG, T1/T2 JSONL and shared summary, not an independently named T4 captured session.
owner evidence: run 42058825739 world enter/save/exit/reopen passed on phone; package publish failure distinct. INPUT-005 still OPEN. No T5 resolution files changed.
next: audit per-case T4 statuses, source captured gate, and define falsifiable next signed-game trace contract; no duplicate CI.
