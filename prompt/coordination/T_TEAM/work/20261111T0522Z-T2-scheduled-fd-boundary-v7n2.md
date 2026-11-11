# T2 fd-boundary scope
session_id: 20261111T0522Z-T2-scheduled-fd-boundary-v7n2
origin: scheduled
baseline_sha: db00a2503c8ab2b47f22e12a36f458110beaac87
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world/save/re-entry success on 42058825739, water FFT failures remain.
previous: prompt/coordination/clients/T2/sessions/20261111T0325Z-T2-scheduled-input-boundary-n6q4.md
hypothesis: source.is_symlink + source.open allows TOCTOU replacement. Verify input identity with os.open(O_NOFOLLOW) and fstat on the opened descriptor; fail closed on unsupported platforms.
files: scripts/t2_foam_publish_aggregate.py; tests/test_t2_foam_publish_aggregate.py; unique T2 session and work files.
experiment_key: T2-FOAM-PUBLISH-FD-20261111-0522
shared_resource: none; no Unity/CI manual dispatch; rely on existing path-triggered CI.
limits: evidence publisher only, not connected to producer; no ShaderLab/device proof.
