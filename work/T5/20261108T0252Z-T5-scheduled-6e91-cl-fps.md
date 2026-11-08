# T5 work 20261108T0252Z-T5-scheduled-6e91
origin: scheduled
issue_id: PERF-LogRaft-CL-identity
status: active
base_sha: 2c8a1de3b97e8ceca752119051a03146075b5642
intended_files: work/T5/20261108T0252Z-T5-scheduled-6e91-cl-fps.md; clients/T5/sessions/20261108T0252Z-T5-scheduled-6e91.md
experiment_key: CL@520c4cf4/LogRaft-20261105-220911-559/metrics-00001@bb24dda68503897cf4e2a5e4e2d8aef3e71777b8/SurfaceFlinger-fps-validity
resource_key: none (read-only CL JSONL)
hypothesis: LogRaft CL records may already be flat, so no nested adapter needed; verify original format before implementing conversion.
owner_scope: T5 performance analysis only; no T4 mouse, Unity, or shared build resources.
