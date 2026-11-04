# B01 — original managed FFT caller tokenization source proof

- Session: `20261104T2231Z-B01-fft-args`; issue WATER-001; source `ec4f8cef6fc1c028d3e8df519fc08494e8442161`.
- Refines independent *managed CSharp callsite scan* only; B48/B18 work on original runtime serialized compiled FFT mapping is not replaced or modified.
- [CI 41926033893](https://github.com/alwansan/raf/actions/runs/41926033893) SUCCESS: 67 synthetic tests, SHA-pinned exact original managed callers Dx11FFT Dispatch=2, SetTexture=6, offsets=[0,1]; WavesRendererFFT SetTexture=10, unchanged vs CI41911972796. Original numeric oracle exit0.
- Rejected hypothesis: raw delimiter-sensitive comment/verbatim string false positives influence the **currently verified** original caller counts; they do not change those counts after fix. The parser was still unsafe for those synthetic valid CSharp cases.
- Unresolved: original FindKernel ID to Unity compiled stage and actual Adreno kernelCount/ShaderLab missing passes. This result cannot be used to close WATER-001 or mark phone readiness. No private shader/DLL content published.
