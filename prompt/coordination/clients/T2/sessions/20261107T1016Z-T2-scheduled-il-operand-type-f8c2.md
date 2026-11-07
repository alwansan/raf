# T2 — synthetic IL untrusted operand type guard

- session_id: 20261107T1016Z-T2-scheduled-il-operand-type-f8c2
- origin: scheduled
- resumed_from_sessions: 20261107T0923Z-T2-scheduled-il-index-bounds-k7p2; 20261107T2227Z-T2-chat-blit-texture-role-6c52 (file timestamp is not device evidence)
- base_sha: 91e41cd0963d80d2815e2ea8d9ff4aa06af2dd93
- owner phone: [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), [report](../../../../docs/DEVICE_FEEDBACK_42058825739_AR.md). Owner world entry/save/reentry from artifact confirmed, package publish failed. Water pass/FFT remain open; no claim of new phone test.
- scope: [work](../../work/WATER-001/20261107T1016Z-T2-scheduled-il-operand-type-f8c2.json), reserved first in commit e278b5720c52eb7625c14951045697e3429f7e9d. No T3/Unity/ShaderLab assets touched.
- hypothesis: malicious non-string opcode/type operands can invoke Python custom equality or string conversion in source-free synthetic IL provenance, escaping the fail-closed Unresolved contract.
- source fix: [c4d428ae](https://github.com/alwansan/raf/commit/c4d428ae73e594960eea803afedddd245c4a900d) strictly rejects non-str opcode and non-str ldarg kind before equality. [regression controls 634ddd80](https://github.com/alwansan/raf/commit/634ddd80358fa4b0f9dacf3246c1bdc7693237ad) include Poison.__eq__/__str__ throwing and None/int malformed values.
- validation: code and tests committed, but actual repository unittest NOT executed in this cycle. The expected behavior is Unresolved for all four cases; do not claim a green suite. GitHub Actions latest inspected: [T3 42333961072](https://github.com/alwansan/raf/actions/runs/42333961072) SUCCESS; no duplicate CI/native dispatch.
- evidence limits: synthetic IL helper only; no original Mono.Cecil integration, pass1 resource producer identity, CB0/ShaderLab binding, Vulkan/Unity compile, Android water pixels or new native build proof. WATER-001 OPEN; NOT_READY.
- next_step: run `python -m unittest tests.test_t2_pass1_stack_provenance -v` on exact branch, then integrate safe typed IL provenance into authenticated Mono.Cecil report for Foam pass1 without touching the chat-owned resultflow parser until scopes reconcile. T3 owns particles, T4 mouse, T5 Resolution.
- source HEAD after fix: 634ddd80358fa4b0f9dacf3246c1bdc7693237ad; session creation advances HEAD.
