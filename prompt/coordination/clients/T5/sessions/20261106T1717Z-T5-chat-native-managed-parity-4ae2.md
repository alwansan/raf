# T5 chat — native Unity ↔ original-managed Android runtime staging source parity

- session_id: `20261106T1717Z-T5-chat-native-managed-parity-4ae2`
- origin: `chat`
- issue: `INTEGRATION-001`
- status: `waiting_ci` (initial checkpoint)
- resumed_from_sessions: `20261106T1710Z-T5-chat-crossclient-copy-parity-a6d9`, `20261106T1702Z-T5-chat-offline-obb-compile-58cf`, `20261106T1645Z-T5-chat-installed-obb-read-e7c4`, `20261106T1649Z-T5-scheduled-runtime-attribution-c82f`.
- base_sha: `623fb7268dbab3167ee643ca5da0299384d846f0`
- work reservation: `prompt/coordination/work/INTEGRATION-001/20261106T1717Z-T5-chat-native-managed-parity-4ae2.json` created commit `0649e87b337ae196c78dbe55ce4043c667003971`; origin and intended_files recorded **before** execution.
- experiment_key: `T5-full-real-managed-17-native-17-runtime-compile-source-staging-equality-prebuild-fail-closed-v1`.
- resource_key: `source-only native workflow copy metadata and T5 offline candidate runtime list`; *not* Unity runtime shared queue.
- hypothesis: An independently edited Unity native Android C# source copy list and original-managed compatibility compile copy list can drift; a cheap managed compile could pass while Unity silently lacks a source class. Prove exact member parity, bounded paths, one correct copy destination and regular source files from the actual workflow source.
- new source: `scripts/t5_validate_runtime_staging_parity.py` commit `c9a04f7be4657efceb2ec18cab376ff9c4990207`; loads real native workflow and real managed verifier list (not synthetic manifests) and refuses missing/duplicate/unsafe copy sources.
- tests: `tests/test_t5_runtime_staging_parity.py` commit `0b2aaafc1a8147098cbd933b563ecaf1ce4e0a28`. Eight positive/negative tests including real lists, removed source, duplicate, path/shell control injection, wrong Unity destination, nonliteral managed list, absent files and duplicate loop.
- cheap integration CI `.github/workflows/raft-android-offline-integration-tests.yml` commit `cf580caf30b25f55eb601b6026b46fa10467bdf0`, includes native workflow sparse checkout, runs tests and exact source parser before existing private ILSpy original-managed compile; triggers when either manifest or parity test changes.
- CI begun from immutable source `cf580caf30b25f55eb601b6026b46fa10467bdf0`: [run42260528639](https://github.com/alwansan/raf/actions/runs/42260528639). No extra Unity/job dispatched; run was automatically triggered by source workflow edit.
- active team check: T1 [Unity keyword-variant experiment42259968584](https://github.com/alwansan/raf/actions/runs/42259968584) was live during reservation, T2 Foam original identity CI progressing, T3 Particle108 source CI, T4 logger/world independently; no files or jobs touched. T5 scheduled PERF-007 not modified.
- original APK/OBB owner-tested pair still old run42058825739, runtime installed-OBB same-version log not yet observed. Source parity checks neither target Android render pixels nor Unity Editor or phone readiness.
- next_step: check CI42260528639 terminal; if source test fails, repair exact manifest parser or uncovered difference, retain all original source/asset safety. Save result and own experiment/event then close scope.
