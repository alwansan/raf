# B05 incident: scoped source test import dependency (closed)

Owner B05; session 20261104T2242Z-B05-auth-texenv6; RENDER-002; 2026-11-04 22:51 UTC.

Impact: isolated B05 source-only synthetic CI failed twice; native Unity, APK/OBB, original game bytes, credentials, shared tasks and other workers were not changed or canceled.

- Run https://github.com/alwansan/raf/actions/runs/41928537671 failed one of 18 checks: unknown selected original owner negative fixture unexpectedly imported optional UnityPy before checking owner allowlist; no UnityPy installed in small synthetic workflow.
- Run https://github.com/alwansan/raf/actions/runs/41928655703 failed the same test after moving UnityPy import: the A12 14-owner source inventory had top-level transitive imports not included in minimal sparse checkout.
- Recovery at https://github.com/alwansan/raf/commit/bd14417a7038180fe7f3f3ab2550fc0b26ca154c: independently pin one selected authenticated owner within B05, validate owner allowlist and symlink root *before* optional serializer/import; keep full 14-owner legacy mode separate. This is narrower and safer than acquiring many source tools for one negative test.
- Final green synthetic CI https://github.com/alwansan/raf/actions/runs/41928852363 succeeded 18/18; final pinned genuine original selected-owner acceptance https://github.com/alwansan/raf/actions/runs/41929077930 succeeded 7 unit and real 41 Materials/227 slots.

Rejected hypothesis: failed CI indicated corrupted original Raft Material data. Both failures occurred at Python module import before original source acquisition; no original data had been read. Closed reason: two succeeding verified runs and selected-source implementation.

Remaining: no real same-export Unity Material trace, shaders/pixels/phone results; no assertion that white materials are corrected.
