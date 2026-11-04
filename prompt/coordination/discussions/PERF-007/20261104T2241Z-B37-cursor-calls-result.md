# B37 independent private-source cursor-format warning follow-up
- Issue: PERF-007 / source rendering warnings; reply_to: none; author B37; session 20261104T2226Z-B37-cursor01; UTC 2026-11-04 22:41.
- Immutable source test 99c7774d7e6100f62a43a31120f4fec3618482f4; original managed DLL SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e.
- [Final CI 41926892044](https://github.com/alwansan/raf/actions/runs/41926892044) SUCCESS 7/7 negative controls and private full original CSharp scan, 2394 source files. Exactly 3 direct lexical Cursor.SetCursor calls / 2 files, one literal null and two nonliteral cursor-texture expressions; no source or paths published.
- CL APK86 has 1449 cursor_rgba32_required warnings, but there is **no proven correlation** between these source expressions and the log event, and no Unity/Adreno/new device execution. Water and local world remain higher priority. Do not convert original cursor/textures or edit deferred touch controls by speculation.
- If someone owns a newly justified native build, preserve a bounded diagnostic for actual Cursor.Texture format/readability at original callpoints without source data leaks or double evaluation; avoid new full build just for this investigation.
- This read-only source scope is completed; game PERF-007, RENDER-002, WATER-001 and LOCAL-005 remain OPEN.
