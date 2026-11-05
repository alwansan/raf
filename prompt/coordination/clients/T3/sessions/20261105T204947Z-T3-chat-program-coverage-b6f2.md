# T3 chat — fail-closed partial ShaderLab Pass/SubShader classification

- session_id: `20261105T204947Z-T3-chat-program-coverage-b6f2`
- identity: T3; origin: **chat**; issue: **RENDER-002 OPEN**; readiness: **NOT_READY**.
- resumed_from_sessions: `20261105T2034Z-T3-scheduled-7c91`, `20261105T1933Z-T3-scheduled-a91f`, `20261105T1815Z-T3-chat-native-source921-guid-6cb4`.
- base_sha: `bfa62d362244987f4633cf71cc98fdb6c497ca86` (registered `prompt/coordination/work/RENDER-002/20261105T204947Z-T3-chat-program-coverage-b6f2.json` before source edits at commit `526d7d08f33f21eafbc93b313e3734bb932bb5fb`).
- experiment_key: `t3-native-original-921-marker-free-all-pass-and-subshader-program-coverage-failclosed-synthetic-v1`. resource_key: null; pure source-free tests, no full Unity/ZIP2 run.
- intended_files: `scripts/t3_native_original_921_shader_target_audit.py`; `tests/test_t3_native_original_921_shader_target_audit.py`; this session/work/experiment/event/discussion only.

## Proven starting point and team coordination

T3 scheduled [CI 42104666494](https://github.com/alwansan/raf/actions/runs/42104666494) completed SUCCESS for Python syntax + synthetic original921 native GUID controls on `87c8658`. Its scheduled work file is completed. At checkpoint, other source/platform CI could be running; none was cancelled or re-run. The authentic original six-scene shader identity-to-full-native private trace remains **NOT RUN**. Owner phone feedback [DEVICE_FEEDBACK_42058825739_AR](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/DEVICE_FEEDBACK_42058825739_AR.md) confirms that the newer test package entered/saved/reentered a world; white graphics/water are unresolved. T5 full-native postrestorer aggregate measured 110/142 ShaderLab Dummy and 770/1536 Material documents pointing to Dummy; no source identity attribution to the high-use 921 original shader.

## Concrete bug and change

`strict_native_top_join` previously rejected marker-free ShaderLab profiles with zero programs, unknown exporter or malformed braces, but could still call a **partially programmed** shader `NON_DUMMY_NATIVE_PROGRAM_AUTHENTICITY_UNPROVEN` when `partial_subshader_coverage=true` or `programmed < pass_count`. A single synthetic complete Pass can coexist with a missing program in a sibling SubShader or Pass; it must not count as a fully interpretable marker-free native program.

Atomic source+test commit [fcddfca6](https://github.com/alwansan/raf/commit/fcddfca6e9cf0ac42573e4d9e75eeb9dd959415c) adds a fail-closed `non_dummy_native_shader_incomplete_program_coverage` classifier. Three source-free negative/positive controls independently check incomplete sibling SubShader, one unprogrammed Pass, and retention of explicit Dummy evidence even with incomplete coverage. No private identifiers, GUIDs, original assets, audio, Settings, input, save, native build requests or game shader content changed.

## Validation

[GitHub Actions 42107128075](https://github.com/alwansan/raf/actions/runs/42107128075), job `127524777143`, commit **fcddfca6**, completed **SUCCESS**. Step `py_compile` PASS and three source-free unittest suites PASS: **23 native top921 + 13 original source→export + 16 ShaderLab/Material audit = 52/52**. Triggered by the code/test file paths in existing `.github/workflows/raft-t3-native-921-guid-source-controls.yml`, not a heavyweight new dispatch. Previous CI syntax failure 42094853931 was fixed in the scheduled session, not this one.

**Boundary:** these are all synthetic contracts; no original ZIP2 data was compared to an actual full-native W1 private trace in this cycle. No proof that the highest-use original Shader48 still maps to a Dummy after full restoration, or that its DXBC variants render matching Android pixels. A marker-free fully programmed profile still has program **authenticity unproven**. `RENDER-002` remains OPEN; no READY claim.

## Handoff / next step

Coordinate one bounded source-authenticated same-export run with T5. On the same runner, verify pinned ZIP2 six scenes and four owners; use the SAME full native W1 exporter invocation private lineage and postrestorer Assets to invoke `python3 -m scripts.t3_native_original_921_shader_target_audit`. Keep original IDs, raw source and private Shader GUIDs off public logs. Publish the allowlisted status + counts only. If the exact high-use shader is Dummy, replace real Pass resources/CB/variant mapping under unchanged GUID, then Unity compilation + phone pixels. If INCONCLUSIVE, debug failed profile privately without weakening invariants. Continue with unaffected graphics work while CI runs; do not cancel T5/T1/T2.

Current work status: **completed (guard only)**. No active resource lock, pending CI or state/MEMORY overwrite from this chat session.
