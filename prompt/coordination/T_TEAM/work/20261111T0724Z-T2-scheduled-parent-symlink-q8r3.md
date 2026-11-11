# T2 scoped work 20261111T0724Z-T2-scheduled-parent-symlink-q8r3
origin=scheduled
baseline_sha=44a33169533c936c1adf355b72f0c6b9461dc9c4
experiment_key=T2-FOAM-PUBLISH-PARENT-SYMLINK-20261111
scope=scripts/t2_foam_publish_aggregate.py; tests/test_t2_foam_parent_symlink.py; clients/T2/sessions/20261111T0724Z-T2-scheduled-parent-symlink-q8r3.md
hypothesis=Destination parent symlink is followed by Path.is_dir and NamedTemporaryFile; reject parent symlink before publishing to avoid unintended output outside selected directory.
shared_resource=none; no Unity/CI dispatch
source=docs/DEVICE_FEEDBACK_42058825739_AR.md (world load/save/reopen confirmed; water FFT errors remain)
coordination=T2 isolated publisher boundary; T1 FFT, T3 visual effects, T4 mouse, T5 resolution/build remain separate.
validation=local Python unittest plus CI if triggered; do not infer device water success.
