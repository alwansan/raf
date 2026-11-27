# GT V11 — authored-only CI running | 27 نوفمبر 2026

[45966950183](https://github.com/alwansan/raf/actions/runs/45966950183) job 140397789957 on immutable `448fb0c77b116fbceeed856a617ba33046f01826`, source-only regression step SUCCESS; public exporter build in progress. Compatibility guard [45966949749](https://github.com/alwansan/raf/actions/runs/45966949749) SUCCESS. Independent local reconstruction of the exact C# authored fixture (Pillow DDS, integer Z oracle) confirms 70 expected pixels, 43 interior Z / 27 clamp; both fixtures distinguish packed data, swap X/Y, invert Y and both individual axis flips. These are only fixture controls, not actual export pixels; [local receipt](sessions/20261127-dxt5nm-route-v11/local-fixture-check.json) and reproducible script. A3 blocked, G0–G6 open, no original assets, no Unity/Android/XAPK. No V11 actual pass claimed.

**Next:** Inspect exact CI 45966950183 and archive, compare actual top SHA with local fixture and normal RGBA SHA; require all 12 controls, importer and route acceptance, no scope promotion. If fail, preserve failure and diagnose actual public converter. Only target branch; no full build.

---

# GT V11 — authored source gate and focused witness prepared / PENDING

Starting HEAD 5973d0fc26d86736779b869273d504d43a43d444 matched. V10 [45964427702](https://github.com/alwansan/raf/actions/runs/45964427702) and guard [45964869783](https://github.com/alwansan/raf/actions/runs/45964869783) succeeded. No accessible local checkout. Source gate commit [bc18e54](https://github.com/alwansan/raf/commit/bc18e5414b88b2b8288af22df076c0166a43a41f). Separate DXT5nm typed format12/usage3/Gamma0 proof; independent BC3/FlipY then pinned T3 X=alpha/Y=green and Z reconstruction, old R to new A. Actual authored two 5x7 textures with varied green, both alpha modes, 12 proposed counterfactuals, strict RGBA and importer GUID/type1/format12/sRGB0; independent integer Z oracle, distinct route and lower-mip scope exclusion. **Not yet executed.** No V8/V9/V10 promotion or actual Unity import/runtime/Android proof. A3 blocked, G0–G6 open, original assets not read, no XAPK. No writes on CL/lab/BLACK. Activate only dedicated authored workflow after source prep; inspect exact result and hashes, repair underlying issue if failed.

Pinned T3 blob ada9e63cf75c989f72ffe847ac993973e9cdd0fc; pinned public converter blob f8cec77003d86fa3d6ad1a04002927733a1986a6 and ImporterFactory blob 1072508b7b61b292f646d99cc79fb5e8f8e574d6 at public ref 036098ab525a3f9f693dc101edeb21faad4d32d8.
