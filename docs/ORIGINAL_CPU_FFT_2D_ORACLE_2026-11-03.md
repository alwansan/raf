# Original CPU FFT two-dimensional oracle — 2026-11-03

## Evidence
Source: 555e7f6e39416b65d0e657db43e71d0be7d1949e.
[Actions run](https://github.com/alwansan/raf/actions/runs/41637650224), attempt 1, job 125922799795: completed success.
Implementation: scripts/verify_original_fft_cpu_2d.py and .github/workflows/raft-fft-cpu-2d.yml.
The generator retains the authenticated original-body hash checks from verify_original_butterfly_numeric.py. Original source remains private temporary runner input; logs contain aggregate results.

## Experiment and actual result
The original CPU complex lane executes all rows then all columns for four 32×32 inputs: asymmetric complex impulse, constant, asymmetric complex tone, and deterministic real random input. Comparison is against an independent direct two-dimensional DFT with negative exponent and no normalization, rather than a second separable FFT.
- Four cases passed: maximum relative L2 = 1.8933043868319998e-7, threshold 1e-5.
- Two negative controls passed: a transpose and an extra 1/(N*N) normalization are rejected on the random signal.
- Existing original butterfly suite also passed: 40 cases, 194893 checks, 3 negative controls; maximum float relative L2 1.88937368177527e-7, half-table 0.00023868836710026192, original CPU 2.0495406296816126e-7.
- Local Python syntax and workflow YAML checks passed before submission; actual C# execution was performed by Actions, not locally.

## Limits and next work
This establishes a bounded CPU oracle for axis order, sign and normalization at N=32 using the original complex lane. It does not execute a translated shader, a Unity import, GPU, half-precision intermediate render textures, every CPU lane, or Android. It cannot close WATER-001, RENDER-002 or FFT-FORMAT-009. No runtime source, original asset, GUID/meta, quality setting, build request or scheduled task changed.
Next use this oracle when authentic shader bodies/resource bindings become available; validate two-pass shader output and intermediate precision independently. Project remains NOT_READY, no candidate, 0/3 complete reviews.
