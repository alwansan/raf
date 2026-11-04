# B49 WATER-001 — per-pass ShaderLab structural contract (2026-11-04)

Source-only gate fix integrated into `scripts/verify_water_render_contract.py` by [commit 5070247](https://github.com/alwansan/raf/commit/50702470954774ba96fe27509f1f9eddfd1aa4ea). Structural helper [1173a23](https://github.com/alwansan/raf/commit/1173a23a272f985bfc837f3812cce4d9798f3d3b) and new negative controls [588610c](https://github.com/alwansan/raf/commit/588610c4d508de785c5f01b957bb96c541cb48a1).

## Defect and correction

Prior gate counted `Pass {` tokens and a single shader-wide `CGPROGRAM` or `HLSLPROGRAM` marker. That allowed six declared water passes but only one authored program to satisfy the pass/program portion of the gate. B49 now checks that *each individual pass* is balanced and contains a complete matched `CGPROGRAM/ENDCG` or `HLSLPROGRAM/ENDHLSL` pair with a nonempty body. Source comments and quoted decoys no longer inflate the counts. Each observed shader reports `passes_with_complete_program` and `all_passes_programmed`; existing `has_program` remains for diagnostics. Compute kernel pragma comments/string decoys are excluded.

## Evidence

[Independent GitHub Actions run 41911824567](https://github.com/alwansan/raf/actions/runs/41911824567) on source SHA `3c4c6e3b350b611e5d364ae3fdc3c6837a11d4ea`: **SUCCESS**, 11/11 tests (6 new,5 existing); artifacts retain synthetic-only unittest output. Budget ubuntu-24.04 under5min, no ZIP2, Unity, original assets, LFS or GPU. Local early fixture sanity checks also passed. Negative controls: multi-pass with only one program, comments and strings, unfinished program markers, empty program body and unmatched braces. Existing native strict gate still rejects unauthenticated water kernels.

## Limits and remaining blocker

This repairs **B49's bounded source validation defect**, not UltimateWater shader rendering. Authentic Spectrum/Foam/Blur/DepthCopy and FFT compute programs, original shader GUID/variant mapping, proper pixels and Adreno device tests remain unverified. Source-only unit passes are not GPU or phone acceptance. Device reference remains APK86 / run41812889049; `WATER-001` remains OPEN and overall NOT_READY0/3. Audio/Settings/touch and native build request untouched.

Next: connect authentic original program/pass identity from SHA-verified ZIP2 objects to exported ShaderLab and compute kernels, validate compilation and per-pass numeric/pixel equivalence, then device testing. Do not repeat a purely structural census.
