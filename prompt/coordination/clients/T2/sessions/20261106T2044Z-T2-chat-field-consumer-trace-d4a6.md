# T2 — bounded SHA-original Foam Material field typed-API consumer trace

- session_id: `20261106T2044Z-T2-chat-field-consumer-trace-d4a6`; origin: `chat`; status: `active`; issue: WATER-001.
- base_sha: `bd807b012b9541b25869315177d52e4390fe2cef`.
- resumed_from: 20261106T2020Z-T2-chat-foam-export-guid-material-3c5e; 20261106T2021Z-T2-scheduled-foam-guid-collision-f8a3; 20261106T1942Z-T2-chat-foam-material-return-to-renderer-c9b7.
- Existing original success CI42284117891: exact Material(Shader) result stored in one managed field and 13 exact field reads in 4 methods, but zero *adjacent* Renderer setters. This is not evidence of Android water pixels.
- Latest scheduled installer collision CI42287347419 was independently reported SUCCESS; scheduled work file remains waiting_ci, so this chat avoids its installer/tests. T1 FFT active CI42290211798; T4 input and T5 native owned separately.
- Scope: bounded typed original mono.Cecil IL taint from exact 13 field loads to Material instance APIs and Material-parameter Graphics/CommandBuffer/Renderer calls (including nonadjacent), with synthetic negative guards, SHA-original CI. No private symbols, raw IL or compiled source may be exported.
- Team trial vote trial-20261106-r1 stays `لا يحتاج` absent significant integrated native Foam/CB0 fix; do not launch native Unity build.
- Next: modify *only own* existing original scanner/validator/tests, CI validate and document safe counts + unknowns; close work/session with exact evidence.

## Verified source-original completion — 2026-11-06T20:47:40Z

- Actual code commit: `589cdf6160176f913c90e69d9105d7255d00b835` (T2-owned Mono.Cecil scanner, fail-closed JSON validator, 9 new negative controls). Existing isolated original workflow auto-ran; no duplicate build/dispatch.
- **[CI42291227491](https://github.com/alwansan/raf/actions/runs/42291227491) SUCCESS** at exact SHA, job `128144861565`: 53/53 aggregate tests + 6/6 synthetic name tests + C# typed Mono.Cecil selftest. SHA original 115978112B shader owner and 3211776B managed source verified.
- Newly proven **13/13 exact original Material field load sites** scanned via bounded straight-line stack taint; **98** subsequent IL instructions; **9** sites pass actual alias as typed Material/Object receiver; **2** sites pass alias as exact `UnityEngine.Material` typed parameter to authentic `UnityEngine.Graphics`; 0 matching CommandBuffer, Renderer or other typed Material argument sites; 0 ambiguous/budget sites. Counts are source only, not Unity/Android execution.
- Source-safe artifact `13539837293` (1216B, sha256:039b502d19d067980352e014acae9243b7145e1249517bfa8681d08e9259d037); private shader name/original fields/IL purged; no data exported.
- Published report `docs/T2_ORIGINAL_FOAM_MATERIAL_FIELD_API_CONSUMERS_2026-11-06.md`, canonical event `prompt/coordination/B_TEAM/events/T2/20261106T2044Z-T2-chat-field-consumer-trace-d4a6-result.json`, experiment `prompt/coordination/experiments/T2/20261106T2044Z-T2-chat-field-consumer-trace-d4a6.json`. No other clients' files changed.
- No runnable game ShaderLab/material/CB0/native APK changes; T2 trial r1 stays `لا يحتاج`. WATER-001 OPEN and game NOT_READY.
- Next: private exact typed `Graphics` method classification and/or managed host scene-class join to 427 real types, then coordinate owner-authorized actual Unity export target and Adreno pixel checks.
- status: `completed`; origin: `chat`.
