# T2 — bounded SHA-original Foam Material field typed-API consumer trace

- session_id: `20261106T2044Z-T2-chat-field-consumer-trace-d4a6`; origin: `chat`; status: `active`; issue: WATER-001.
- base_sha: `bd807b012b9541b25869315177d52e4390fe2cef`.
- resumed_from: 20261106T2020Z-T2-chat-foam-export-guid-material-3c5e; 20261106T2021Z-T2-scheduled-foam-guid-collision-f8a3; 20261106T1942Z-T2-chat-foam-material-return-to-renderer-c9b7.
- Existing original success CI42284117891: exact Material(Shader) result stored in one managed field and 13 exact field reads in 4 methods, but zero *adjacent* Renderer setters. This is not evidence of Android water pixels.
- Latest scheduled installer collision CI42287347419 was independently reported SUCCESS; scheduled work file remains waiting_ci, so this chat avoids its installer/tests. T1 FFT active CI42290211798; T4 input and T5 native owned separately.
- Scope: bounded typed original mono.Cecil IL taint from exact 13 field loads to Material instance APIs and Material-parameter Graphics/CommandBuffer/Renderer calls (including nonadjacent), with synthetic negative guards, SHA-original CI. No private symbols, raw IL or compiled source may be exported.
- Team trial vote trial-20261106-r1 stays `لا يحتاج` absent significant integrated native Foam/CB0 fix; do not launch native Unity build.
- Next: modify *only own* existing original scanner/validator/tests, CI validate and document safe counts + unknowns; close work/session with exact evidence.
