# T3 RENDER-002 scope
session_id: 20261108T2228Z-T3-scheduled-empty-material-z8q3
origin: scheduled
base_sha: 1f61bfdc338cf11072f613593670508242078881
experiment_key: T3-EMPTY-MATERIAL-20261108-z8q3
resource: source-only; no Unity, no shared APK, no game asset edits
files: scripts/t3_particle_external_material_resolution.py; tests/test_t3_particle_external_material_resolution.py; independent T3 session file
hypothesis: a zero-byte .mat with valid .mat.meta is currently counted as resolved although it cannot contain Unity Material serialization.
expected: zero-byte material classified separately, not resolved; preserve GUID privacy and all original resources.
prior evidence: T3 20261108T2131Z-T3-scheduled-orphan-material-m8q4; CI 42505587548; owner device report 42058825739.
coordination: independent audit script only; T1/T2 water/shader, T4 mouse, T5 UI/build unaffected. Recheck HEAD before source edit.
