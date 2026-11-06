# T2 — reflected CB0 array terminal bound verification

- session_id: 20261106T2148Z-T2-chat-cb0-array-bounds-5bc1; origin: chat; status: active; issue: WATER-001.
- resumed_from_sessions: 20261106T2138Z-T2-chat-foam-matdoc-82bd; 20261106T2117Z-T2-scheduled-foam-ci-reconcile-k6m2.
- base_sha: 7533b22af692568b0e4df1b5dc9c73191f0aeceb; taken_over_from: T2 prior original Foam CB0 tests, https://github.com/alwansan/raf/actions/runs/42298467191.
- Existing original Foam success: 4/4 stages compile/validate from SHA-pinned original; per-pass same-coordinate CB0 shared member has different array shape and block extent; pass0 fragment 6 observed loads exceed VS reflected length, pass1 vertex 2 exceed FS reflected length; source-only diagnostics, not device runtime.
- New failure mode hypothesis: _member_geometry() accepts array_stride=None or final element's start >= reflected UBO block_size; this can produce false structural geometry claims even for malformed reflection.
- Planned independent scope: scripts/t2_foam_private_cb0_member_shape.py, tests/test_t2_foam_private_cb0_member_shape.py. New source-free adversarial tests and existing CPU-only source-original private candidate CI triggered by narrow path. No original shader/device/native modifications. Live owner-native https://github.com/alwansan/raf/actions/runs/42296450023 separate; do not cancel/duplicate.
- experiment_key: T2-Foam-CB0-reflected-array-terminal-stride-vs-declared-block-bounds-v1
- plan: require stride for reflected nonempty arrays; compute conservative lower bound offset + (first dimension length - 1)*stride < block_size without assuming vector/matrix element final bytes; test boundary, offset and valid source-like fixtures; run source-original CI to check if original geometry is genuinely bounded.
- next_step: implement and run; preserve source privacy; update only this session.
