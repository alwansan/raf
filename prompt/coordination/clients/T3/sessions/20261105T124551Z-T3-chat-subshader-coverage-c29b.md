# T3 — independent chat continuation: multi-SubShader diagnostic integrity

- session_id: `20261105T124551Z-T3-chat-subshader-coverage-c29b`
- origin: `chat`
- resumed_from_sessions: `20261105T1213Z-T3-native-shader-dummy-audit`, `20261105T1130Z-T3-nonnormal-semantic-guard`
- base_sha: `c2b4948875748f38cc3bcf5086c4e51d3715ba47`
- status: `completed`
- issue: RENDER-002 OPEN; scope: `scripts/t3_audit_exported_material_programs.py`, `tests/test_t3_audit_exported_material_programs.py`
- work_id: `prompt/coordination/work/RENDER-002/T3-20261105T124551Z-T3-chat-subshader-coverage-c29b.json`
- experiment_key: `T3-post-restorer-shaderlab-all-subshaders-coverage-source-56d3f6a-b49-structural-pass-coverage-v1`
- origin evidence: CI42026630845 authentic pre-restorer 511/511 custom Material links to 54 dummy Shader GUIDs; post-restorer native CI unexecuted; CI42026545273 existing synthetic controls SUCCESS. 
- competing work: at check 2026-11-05 12:43Z no in_progress or queued Actions. Last T3 shader work marked completed; T1 FFT/T2 Foam/T4 local/T5 integration files are out of scope.
- hypothesis: an actual multi-SubShader file can contain one structurally complete Pass and another incomplete SubShader; the diagnostic currently counts it under *has a completed pass* with no aggregate warning. Add distinct source-only incomplete-coverage counters and negative test, do not claim runtime branch selection or original authenticity.
- files/experiment planned: `scripts/t3_audit_exported_material_programs.py`, `tests/test_t3_audit_exported_material_programs.py`; existing push-trigger workflow `.github/workflows/raft-t3-native-material-shader-quality.yml`; no Unity native or game resource changes.
- result: COMMITTED script `efb1d7bc675ff7b9650f6a3e246c1c7f6fb1aeda`, tests `f0062b39297b1e4953bac2934e479e25fa199a27`; [CI42030761276](https://github.com/alwansan/raf/actions/runs/42030761276) SUCCESS at head f0062b3. Test logs: 15 T3 + 8 W1 + 8 B49 = 31 passed; py_compile passed. Structural source-only partial SubShader counters added, not Shader authenticity or Android visuals.
- run_urls: [https://github.com/alwansan/raf/actions/runs/42030761276]
- next_step: Review `t3-native-material-shader-quality.json` on next authorized full native post-restorer import; prioritize source-authentic shader restoration, Unity compile and Adreno/device visual test. The native post-restorer importer was NOT run in this cycle; RENDER-002 remains OPEN. Preserve working audio/Settings and deferred input/touch.
