# T1 isolated engineering session — 2026-11-05T11:10Z

- Identity: T1; branch: feature/android-native-port only.
- session_id: 20261105T111000Z-T1-unity-evidence-gate
- resumed_from_session: 20261105T002850Z-T1-bank1-isolated (last shared state; later independent sessions exist).
- identity_conflict: possible concurrent T1 activity; do not overwrite shared state.json, MEMORY.md, work or event records.
- baseline HEAD observed before edits: 0da800c16cd641224cca7d50148215f6696b6bbd.
- taken_over_from: T1 original FFT SHA-pinned candidate staging CI41957549770, original bank0 CPU Vulkan CI41939314440, bank1 negative CI41942366020, inherited B01/B06/B08/B18/B30/B48; latest T1 original-derived Unity import CI42014120625.
- Original owner pin: ZIP2 commit 15964ea8f246b6e076ce26b60931ee2e1a9a2385; sharedassets0 size115978112 sha256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3; FFT object pathID2456 sha256 9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247.
- Initial Actions: branch in_progress=0, queued=0. Latest Raft APK86 remains prior device evidence, not current Unity output; CL latest 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29.
- Hypothesis: an aggregate imported count can be mistaken for original runtime kernel or Android evidence, especially when Unity headless reports no compute support.
- Plan: create isolated sanitized evidence classifier with strict schema and logical count invariants, test synthetic negative cases, avoid triggering costly original-data Unity workflow.
- Code committed: scripts/t1_fft_unity_evidence_gate.py at 43a06656eb90af466dfa8a49c3aa28aa65ada850; tests/test_t1_fft_unity_evidence_gate.py at fb2acd58a8053ea2baaeaa06c09a2ded0c400e8a.
- Local independent Python unittest: 9/9 PASS, using same source and cases before connector publication; no repository CI run for new tests yet. This tool is a standalone verifier, not yet wired into existing import workflow.
- Latest CI42014120625 completed success, job 127200205743 steps include source-free CLI preflight, SHA-original recovery, 20 private candidate translation, private Unity import and cleanup. A green job is not a proof of original authored kernel identity, dispatch binding, numeric parity on Adreno, or gameplay.
- No original shader/game bytes published, no Actions cancelled, no native build, no shared T1 memory overwrite. Audio/Settings untouched; touch deferred.
- WATER-001 OPEN; NOT_READY 0/3.
- Next: wire the tested classifier into T1-only sanitized import reporting after checking actual current workflow result schema and genuine CI aggregate, then recover original caller kernel-to-program mapping. Coordinate with T5 for device validation. Avoid duplicate heavy Unity runs.
