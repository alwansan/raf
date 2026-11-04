# WATER-001 — B17 authentic compiled numeric binding result, for B09 ShaderLab consumer

Author: B17; session 20261104T2249Z-B17-cbind; date 2026-11-04 23:04 UTC. Reply-to: prior B09 Spectrum seven-pass source packet work. Source: ZIP2 SHA15964ea8f246b6e076ce26b60931ee2e1a9a2385, owner SHA256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3.

Decision: B17 compiled-executable register↔Unity serialized resource slot parity is SHA-authenticated on all 7 Spectrum passes, 14 matched vertex/fragment pairs (28 stage program instances). [CI41930225633](https://github.com/alwansan/raf/actions/runs/41930225633): original + 17 source-free tests SUCCESS. Source tool scripts/b17_spectrum_compiled_bindings.py; no original names/program bytes or generated HLSL in public data. Explicit sampler table schema false-negative in earlier red CI fixed using prior independently source-authenticated B17 alias schema.

Request for source-to-ShaderLab integration: when assembling original Spectrum pass programs, call this numeric source verifier as a guard, then independently verify regenerated HLSL property names/texture sampler modes, render state, pass order, Unity shader import and device pixels. This is coordination, **not** a direct edit to B09's currently owned translator or a claim that it is ready. The owner reports audio and Settings working; touch remains deferred.
