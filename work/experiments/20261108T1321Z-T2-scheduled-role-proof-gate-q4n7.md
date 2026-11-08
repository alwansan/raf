# WATER-001 — optional strict classification gate
session_id: 20261108T1321Z-T2-scheduled-role-proof-gate-q4n7
origin: scheduled
base_sha: 1b706c8bfab2220ea8e7aba5f53df3956acda7f7
experiment_key: foam-role-unknown-strict-gate-sourceonly-v1

Existing role validation accepts unknown source/destination as a truthful unresolved classification. Added opt-in --require-classified to reject unresolved categories before a downstream stage may consume them. Default behavior remains backward compatible. This gate does not prove texture identity, original IL, CB0, ShaderLab, Unity compilation, or device rendering. Tests cover unknown rejection, known categories, missing pass. No proprietary data or CI launched. Test suite execution not yet verified; next run Python unittest on pinned source, then original Mono.Cecil trace from previous experiment.
