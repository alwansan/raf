# T2 — scheduled CFG bounded local-index safety

- session_id: `20261105T1916Z-T2-scheduled-localbound-c61f`; origin: `scheduled`.
- resumed_from_session: `20261105T1821Z-T2-scheduled-stackjoin-b4e9` and chat `20261105T1736Z-T2-chat-rt-return-reason-8e2d`.
- baseline_sha: `950bd1899713dd7ee8f55c8bc1bfa70254d7b2f8`; scope plan: `prompt/coordination/work/WATER-001/T2-20261105T1916Z-T2-scheduled-localbound-c61f.json` committed `8fefbd5b6d126b790d82c5794ee9bd18e91ff579`.
- Hypothesis: malformed `stloc` with a billion-index operand can allocate an enormous locals list before `max_states` takes effect. Previous analyzer did not bound local indices.
- Source fix: `2c055dfd149d30a698caca8aca90e8631d9da2dc` adds bounded local index and rejects bool operands; test commit `8f4465b2d8194c8a6b29ac859f57cec79a692cce` covers huge index and boundary behavior.
- Validation: static source review only; synthetic tests **not executed**. Local git access failed with `Could not resolve host: github.com`; no equivalent CI dispatched. No original DLL, Unity, GPU or device evidence.
- Latest checked HEAD at start `950bd1899713dd7ee8f55c8bc1bfa70254d7b2f8`. Recent Actions: T1 run 42091511060 failed on older SHA; T4 run 42086855402 succeeded; no new Actions launched or cancelled. Releases query top 3 returned lograf tags, not evidence of new game release.
- Scope excludes ShaderLab/assets/.meta/GUID, audio, Settings, touch, other T workers. WATER-001 remains OPEN; NOT_READY.
- Next: run `python -m unittest tests.test_t2_rt_return_cfg` in reachable CI, and inspect authentic CIL caller typed return provenance before claiming an actual RenderTexture allocation. Do not infer phone rendering from this check.
