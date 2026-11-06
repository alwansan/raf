# T2 SHA-original Graphics.Blit public overload role check

- session_id: 20261106T2211Z-T2-chat-blit-overload-b47a; origin: chat; status: active; base_sha: 084075ec1f31bba3aa5591c3db1ac8caefde057b; updated_at: 2026-11-06T22:11:52.613Z; issue: WATER-001.
- resumed_from_sessions: 20261106T2203Z-T2-chat-graphics-path-7d3e, 20261106T2148Z-T2-chat-cb0-array-bounds-5bc1.
- Proven source original [CI42302222142](https://github.com/alwansan/raf/actions/runs/42302222142): 13 exact Material field loads, two Graphics typed Material argument sites, both Graphics.Blit (2/2). No actual Unity pixels, source-destination role, or pass selector identity.
- Hypothesis: distinguish exact public Unity `Graphics.Blit(Texture, RenderTexture, Material)` from `Graphics.Blit(Texture, RenderTexture, Material, int)` with explicit pass selector; unknown/ambiguous overload must be recorded without guessed semantics. Public API type signatures only, not original argument values or source names.
- Work: prompt/coordination/work/WATER-001/20261106T2211Z-T2-chat-blit-overload-b47a.json; experiment key T2-original-Foam-Graphics-Blit-overload-Texture-RT-Material-optional-pass-v1.
- Scope: three T2-owned original scanner/validator/test files, not T2 scheduled Foam installer, T1 FFT, T3 shaders, T4 mouse or T5 Unity. Existing source-only workflow auto on exact code-path, 20min timeout; no new native request, no cancellation.
- Native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) older immutable SHA still in progress during preceding T2 check. Last Foam original script CI42302222142 green; summary builder event identity issue T3 separately reported.
- next_step: implement exclusive signature-family source-only counters, strict aggregate validator, Cecil synthetic typed Material stack tests, then original SHA-pinned CI and document what the real calls prove.
