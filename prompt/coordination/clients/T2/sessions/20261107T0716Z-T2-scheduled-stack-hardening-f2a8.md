# T2 — synthetic IL stack fail-closed hardening

- session_id: 20261107T0716Z-T2-scheduled-stack-hardening-f2a8
- origin: scheduled
- base_sha: 491c18157ac9724e7d0d1516c43f738b3304a9e9
- resumed_from_session: 20261107T0620Z-T2-scheduled-pass1-stack-boundary-c4e9; docs/T2_FOAM_PASS_ROLE_AUTHENTIC_2026-11-07.md
- owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; real device entered, saved and reopened world from artifact; water/FFT still broken; release publication failed.
- scope: prompt/coordination/work/WATER-001/20261107T0716Z-T2-scheduled-stack-hardening-f2a8.json, committed b73867ca311e025dfc327ded542371780a2c9141 before source changes.
- finding: synthetic model accepted bool as int for stloc, accepted arbitrary ldarg identifier, and raised TypeError rather than Unresolved for unhashable ldloc operands. Invalid max_steps and ignored operands also risked inconsistent fail-closed behavior.
- code: scripts/t2_pass1_stack_provenance.py commit 25760c3146665062c4538308f0f3cae445e5ee5f; tests/test_t2_pass1_stack_provenance.py commit 172152447d407970332fa0a35a803fef88101fd0.
- test: local Python 3 unittest smoke with equivalent hardened interpreter and six grouped tests PASS (6/6), including 8 malformed operand cases and four invalid budgets. Exact repository test suite not executed in GitHub Actions this cycle; no CI dispatch or Unity build.
- limits: synthetic source-free model only. Original Mono.Cecil IL not yet consumed; authentic Foam pass0 RenderTexture -> RenderTexture, pass1 UNKNOWN -> UNKNOWN. No shader/runtime/GPU/device proof. WATER-001 OPEN.
- next: run repository unittest suite in CI or isolated checkout; integrate bounded Mono.Cecil adapter privately only after overlap check with T2 chat, then prove pass1 source/destination and CB0/ShaderLab bindings. Coordinate graphics effects with T3. No APK trial vote until integrated fix.
- final HEAD checked: 172152447d407970332fa0a35a803fef88101fd0.
