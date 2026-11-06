# T2 — SHA-original Foam Material typed Graphics API route classification

- session_id: 20261106T2203Z-T2-chat-graphics-path-7d3e; origin: chat; status: active; issue: WATER-001; base_sha: 884475aadb32ee1d3c8451d7be5f3db12f4b7421; updated_at: 2026-11-06T22:03:34.193Z.
- resumed_from_sessions: 20261106T2155Z-T2-chat-blur-export-guid-guard-9f1c, 20261106T2148Z-T2-chat-cb0-array-bounds-5bc1, 20261106T2044Z-T2-chat-field-consumer-trace-d4a6.
- original evidence: [CI42291227491](https://github.com/alwansan/raf/actions/runs/42291227491) validated exact Shader.Find→Material field chain, 13 exact Material field loads and 2 typed UnityEngine.Graphics material parameters; destination Graphics method families not classified. No Unity runtime binding/device pixels proven.
- independent T2 latest: Foam original CB0 source CI42300107157 success but VS/FS reflection sizes differ, Blur source-only GUID guard CI42300619078 success; no authentic Foam Unity import.
- HEAD checked: 884475aadb32ee1d3c8451d7be5f3db12f4b7421; native owner run [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) in_progress, old immutable source a1737bd; other T1/T3/T4/T5 work left intact. T2 scheduled scope overlap not seen in latest runs; if overlaps, preserve own session and avoid concurrent file edits.
- scope: public `UnityEngine.Graphics` method categories only (`Blit`, `DrawMesh`, `other`, `mixed`); classify only when the **same original field value** reaches a typed Material parameter, not mere presence of a Graphics method. No private method/class names or source strings in report. Keep category partition exclusive per field-load site, with strict schema and selftests.
- experiment_key: SHA-original-115978112-shader-3211776-DLL-T2-Material-Graphics-API-method-category-v1; resource_key: T2 isolated SHA-original Mono.Cecil source-only workflow; no Unity or T5-native.
- planned code files: android-port/Experiments/T2/FoamShaderFindResultFlow/Program.cs, scripts/t2_foam_shaderfind_return_report.py, tests/test_t2_foam_shaderfind_return_report.py.
- Workflow: `.github/workflows/raft-t2-foam-original-shaderfind-resultflow.yml` (existing source-only, no manual dispatch). Preserve original source SHA manifests; don't request Unity/native.
- next_step: implement classification, synthetic negative checks, authenticate original in existing CI, interpret counts as IL static flow only; record result, remaining unknowns, and safe T5 handoff.

## Source commit and CI checkpoint — 2026-11-06T22:08:13.782Z
- Code committed on allowed branch at [3bbb7b04](https://github.com/alwansan/raf/commit/3bbb7b040b7a626e61f68e5572d402ee49a93a4d), changing only the original T2 Mono.Cecil scanner + safe report schema + source-free tests. No original source/Unity asset mutation.
- [CI42302222142](https://github.com/alwansan/raf/actions/runs/42302222142) auto-triggered on that immutable SHA; currently in_progress. Do not dispatch duplicate or assume original counts until PASS. Preexisting platform adapter workflow 42302222216 auto-triggered independently, no native build.
- New fields classify two previously known typed Graphics receiver sites by public `Blit`, `DrawMesh`, `Other`, `Mixed` families, mutually exclusive by exact original material field load site. Tests require complete 1-of-4 partition and reject false name-only evidence.
- When CI settles, read logs for aggregate safe method-family counts and selftest, record evidence and handoff; if RED, fix real regression without bypassing validation.
