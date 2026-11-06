# T2 scheduled — pinned CL evidence JSON fail-closed validation

- session_id: `20261106T0120Z-T2-scheduled-json-evidence-7c91`; origin: `scheduled`; agent: T2.
- baseline HEAD: `e3b9f5223fcf2e874d8c43e2fba9a1cfd615fc38`; plan commit `fe2092184649e87ecbd43b72008ffac61c00a99e`.
- resumed_from_sessions: `20261106T0024Z-T2-scheduled-water-summary-rootguard-c8e1`, `20261105T2241Z-T2-chat-foam-shaderlab-authored-6a9d`. Memory.md is older; not overwritten.
- owner phone evidence: [report](../../../../docs/DEVICE_FEEDBACK_42058825739_AR.md), [run 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739), pinned CL `520c4cf409aa20a4db54ff80ed87d8807d9cba57`. Owner confirms world enter/save/re-entry; package publication failed separately. Water pass errors 23,884 and 39,132, FFT errors 3,850 and 6,026. These are log totals, not shader pixel validation.
- read latest T3 CI 42142271779 success (source evidence only); T1 CI 42141540903 success. No in-progress Actions at final check, no duplicate workflow dispatched.
- identified concrete test fixture defect: `tests/test_t2_device_water_summary.py` nested `final_error_category_breakdown` under stop-time although production `classify` reads the top-level root. Fixed fixture and its two root-count mutation tests in commit `8270229420975aeb06665f6e1f9ff6f1a9031469`.
- added strict JSON duplicate key rejection in `read` via `object_pairs_hook` at commit `b536ff807aa34a4e7494197c2968dc43e353179c`; prevents silent override of authentic evidence fields, including nested material counts. Added tests for root and nested duplicates and valid JSON read. No raw proprietary data published.
- validation: fetched and reviewed final test/source text, **tests not executed** (local git network DNS unavailable; no equivalent CI launched). Need run `python -m unittest tests.test_t2_device_water_summary` on checkout and apply checker to pinned CL summaries. Do not assert source-to-device shader fix.
- scope: scripts/t2_device_water_summary.py and tests/test_t2_device_water_summary.py only; no Unity, ShaderLab, game files, audio, Settings, mouse, touch, .meta, GUID, .rgd or other workers' Actions modified.
- WATER-001 OPEN. Next: execute regression suite, then continue authenticated Foam CB0/texture upload and Spectrum/Blur ShaderLab integration with T1/T3 without treating log counts as pixel proof.
