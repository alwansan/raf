# T3 smoke SHA provenance equivalence — 2026-11-09 10:35 UTC

- session_id: `20261109T1035Z-T3-scheduled-smoke-gate-tests-x7q2`; origin=scheduled.
- resumed_from_sessions: `20261109T0932Z-T3-scheduled-smoke-provenance-n8q3`, `20261109T0838Z-T3-scheduled-smoke-state-gate-m4q8`.
- Initial inspected branch HEAD: `68b05db76ecd2941094bd09696e51cd2e4e7006b`. Scope records committed at `cea640fb` and `423b2eb4`; no force pushes.
- Read `AGENTS.md`, owner requirements, status, team protocol and device feedback. Owner's artifact 42058825739 demonstrates limited world/save/reentry on phone, **not** rendering restoration. CL screenshot references and test directory `CL/main/test` reviewed; new binary pixel proof not produced.
- Independent issue RENDER-002. Hypothesis: SHA256 hex is case-insensitive, so identical 32-byte source digests encoded `a` vs `A` must not trigger `different_original_source`. Original gate validated either spelling but compared strings case-sensitively, a false-negative in metadata verification.
- Fix `f2c45894b0150f3e41738d331fae70dee7ae83d2`: normalize both valid hexadecimal strings to lowercase for comparison. Test `9c305e9836e5859297ed6a672e060ac6aa17c41b`: one positive regression for equivalent digest spellings, preserving existing different-digest rejection test.
- Verification: code review confirms narrow change; **new unittest has not run** (local GitHub DNS unavailable). No original Shader48 `m_ParsedForm` / Pass / Blend / Alpha extraction; no material, .meta, GUID, shader, Unity, APK, or phone modification.
- Existing source/export 34-use smoke shader must remain distinct from 108-use fire shader. Gate is **metadata-only**, cannot authenticate source SHA by itself and does not establish visual correctness.
- CI: latest observed platform run [42600762847](https://github.com/alwansan/raf/actions/runs/42600762847) succeeded on T2 commit; no duplicate Unity dispatch. No claim of current full CI acceptance.
- Next: run `PYTHONPATH=scripts python -m unittest discover -s tests -p test_t3_smoke_render_state_gate.py -v`; obtain pinned ZIP2 original smoke-linked shader and actual export in bounded private workflow, extract shader states and material/texture links, then correlate with CL square smoke screenshot. RENDER-002 OPEN; NOT_READY 0/3.
