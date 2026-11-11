# T3 scope — 20261111T1731Z-T3-scheduled-texenv-parser-r6m2
origin: scheduled
baseline_sha: c7f042d490fd713f23d1c6b22ce08b472c1e6516
issue: RENDER-002
status: scoped
files: scripts/t3_material_texture_binding_audit.py; tests/test_t3_material_texture_binding_audit.py; clients/T3/sessions/20261111T1731Z-T3-scheduled-texenv-parser-r6m2.md
hypothesis: A static TexEnv scanner may misclassify nested YAML slot boundaries and therefore conceal missing textures; test actual fixture semantics before altering parser.
experiment_key: T3-TEXENV-PARSER-BOUNDARIES-20261111
shared_resource: none; CPU-only tests, no Unity build
coordination: T4 owns physical mouse, T5 resolution and delivery, T1/T2 water; do not modify those paths.
owner_device_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, artifact 42058825739 demonstrates world save/reload, not render correctness.
prior_evidence: T3 scripts/t3_material_texture_binding_audit.py and test suite; previous orphan-meta fix 8f93bd94. Check actual current HEAD before edit.
