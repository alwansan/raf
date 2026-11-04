# B05 transient UV-regression test migration failure (closed)

Owner B05, session 20261104T2107Z-B05-9e24, issue RENDER-002. Two runs failed in staged checker improvement:
- [41915487156](https://github.com/alwansan/raf/actions/runs/41915487156), SHA834afd6: 11 tests attempted, 6 errors and 2 failures. New `_slot` initially rejected old 3-tuple synthetic exported pointer; two existing normalization fixtures still expected old pointer-only schema. Failing job was **not** original game source evidence.
- [41915549118](https://github.com/alwansan/raf/actions/runs/41915549118), SHAbf3b23d: pointer compatibility fixed, 2 remaining failures exactly stale fixture expected shapes.
- [41915604221](https://github.com/alwansan/raf/actions/runs/41915604221), SHA93aaee8, **COMPLETED SUCCESS**, 14/14 tests after fixture schema migration and 3 new UV controls.

Impact: only isolated synthetic CI; no workflow cancellation, other agents, native build, original assets or gameplay were affected. Root cause: source normalized `(pointer, uv)` while existing synthetic direct pointers/test asserted old tuple. Recovery: accept well-defined original 2-field/export 3-field synthetic forms with unverified UV marker; update assertions to `(pointer, None)` and add drift/partial/nonfinite transform negatives. Closed reason: green successor exact run 41915604221. Production source authenticity/actual export/different GPU behavior remain untested.
