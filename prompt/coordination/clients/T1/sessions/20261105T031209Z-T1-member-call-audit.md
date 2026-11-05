# T1 isolated session — 20261105T031209Z-T1-member-call-audit

- Identity: T1; resumed_from_session: 20261105T002850Z-T1-bank1-isolated (last state read); identity_conflict: possible concurrent T1, so state.json and MEMORY.md deliberately untouched.
- Scope: WATER-001 structural caller audit, NOT original program-to-kernel proof. ZIP2 source pin: 15964ea8f246b6e076ce26b60931ee2e1a9a2385; no private source downloaded.
- Before work: read T_TEAM instructions, state/MEMORY, status, existing audit and tests; repository container git remote DNS unavailable. Existing T1 bank0 CPU Vulkan six cases CI41939314440 remain the only positive original numeric evidence; bank1 negative runs41938536760/41939082498 not superseded.
- Hypothesis: unqualified FindKernel()/Dispatch() declarations or helper calls can falsely satisfy current audit's syntax-present field. Confirmed by regex analysis of the previous implementation; old expression matched bare names. Replaced matcher with explicit dotted member syntax; indirect helper calls intentionally remain unknown.
- Files: scripts/t1_fft_dispatch_evidence.py, tests/test_t1_fft_dispatch_member_calls.py. Changes: 026bb266e19a6bc7b5208da17289f169261ee711 and fa7d79256bfe1eeb56b3613f8858fef2e3e8cc8a. Earlier 5494725894a7631d8f57fc7662e0c3dfd2791eeb was a no-op and is NOT a functional fix.
- Test: local Python re.search smoke verified declaration=false, member=true, unqualified=false. Full repository unittest and GitHub Actions not executed in this session; CI unknown.
- Limits: dot syntax is only structural and does not prove receiver type, actual original runtime mapping, resource dataflow, Unity 2021, Adreno or water. No native build, no actions cancelled, no audio/Settings/touch changes. WATER-001 OPEN, NOT_READY 0/3.
- Next: run unittest against current HEAD, then SHA-authenticated original caller runtime selection and resource-binding analysis, with T5 for Unity staging/device evidence. Avoid modifying other T1 active session files.
