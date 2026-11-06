# T2 original Graphics.Blit explicit pass literal trace

- session_id: 20261106T2217Z-T2-chat-blit-pass-literal-2c9e; origin: chat; status: active; base_sha: dc6518bbbfadbd6887be868cdc1ff3996ebb2e09; updated_at: 2026-11-06T22:17:11.529Z; issue: WATER-001.
- resumed_from_sessions: 20261106T2211Z-T2-chat-blit-overload-b47a, 20261106T2203Z-T2-chat-graphics-path-7d3e
- prior immutable original [CI42303074180](https://github.com/alwansan/raf/actions/runs/42303074180) SUCCESS: exact 2/2 Foam Material Graphics.Blit calls have public `Texture,RenderTexture,Material,int` signature; still cannot assert actual pass argument values or runtime.
- hypothesis: immediate source-original integer push to `Graphics.Blit` pass last parameter can be conservatively classified `literal0/literal1/other_literal/unknown` using bounded no-branch IL direct predecessor (up to 4 NOP); mixed literal sources must not be double counted.
- scope: only three T2-owned scanner/reporter/tests; execute original SHA-pinned Mono.Cecil source-only CI, never log original private names/methods/IL/other argument values.
- owner native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) separate; no new build request, no work on shared T1 FFT, T3 particles, T4 input, T5 delivery.
- work: prompt/coordination/work/WATER-001/20261106T2217Z-T2-chat-blit-pass-literal-2c9e.json; experiment_key: T2-original-Foam-2xBlit-explicit-pass-literal-stack-adjacent-v1; resource_key: T2 isolated source-only original Mono.Cecil scan; same pinned DLL, public pass argument only
- next_step: implement strict public pass literal categories, synthetic positive/negative controls and original CI; preserve unknown if any argument computation is not direct.
