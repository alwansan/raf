# T2 independent scope — 20261111T0820Z-T2-scheduled-parent-ancestor-r5p8
origin=scheduled
baseline_sha=f04814ee0403470bebb4c42cdf5df0c82f8cb17a
experiment_key=T2-FOAM-PUBLISH-ANCESTOR-SYMLINK-20261111
files=scripts/t2_foam_publish_aggregate.py; tests/test_t2_foam_parent_ancestor_symlink.py; prompt/coordination/clients/T2/sessions/20261111T0820Z-T2-scheduled-parent-ancestor-r5p8.md
hypothesis=The existing immediate-parent symlink check permits a symlink in an ancestor directory. This is an isolated publisher safety regression; it does not prove Foam shader recovery.
coordination=T1 FFT and T3 effects untouched; T4 mouse and T5 resolution untouched. No shared CI/build resource.
validation=Python unit test; no Unity/Adreno inference. Check HEAD before next write.
