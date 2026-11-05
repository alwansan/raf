# T2 WATER-001 — verified Foam used sampler edges (2026-11-05)

[Real original-data CI41942245746](https://github.com/alwansan/raf/actions/runs/41942245746) succeeded: 13/13 new synthetic tests, SHA-authenticated ZIP2 original four-stage Foam program packet, privacy cleanup, aggregate-only artifact 13376913366 (ZIP SHA256 `36e24d0bad2775337316f28cacc392d446aeb2eef3cbc549bcf59f1cbd72c0f6`).

New isolated source code: `scripts/t2_foam_spirv_sampler_use.py`, `tests/test_t2_foam_spirv_sampler_use.py`, `.github/workflows/raft-t2-foam-sampler-use.yml`. It traces actual used SPIR-V `OpSampledImage` and sample instructions through SSA aliases to numeric sampled-image and sampler descriptors. Ambiguous chains fail closed. B20/B24/B25 authored prior original source translation; T2 reused their authenticated packet and earlier descriptor gates.

| Stage | Used sample calls | Distinct compiled set0 image→sampler bindings |
| --- | ---: | --- |
| Pass0 vertex | 0 | none |
| Pass0 fragment | 17 | 6→1, 7→2, 8→3, 9→4, 10→5 |
| Pass1 vertex | 0 | none |
| Pass1 fragment | 4 | 2→1 |

This proves **21 compiled sample uses and six distinct actually used numeric pairs**, including all six compiled images/samplers. It does **not** prove a join to the six original `m_TextureParams` property names or original `m_Index/m_SamplerIndex`, authored sampler state, Unity Material upload, ShaderLab import or Adreno pixels. Prior exact original-to-translated literal image-name comparison was 0/6 [CI41941354379](https://github.com/alwansan/raf/actions/runs/41941354379), so using literal names as aliases is unsound.

Last actual game test is APK86. WATER-001 remains OPEN; NOT_READY 0/3. No game files, shader assets, source material, .meta/GUID, audio, Settings, touch, Unity native build, APK or active Actions altered. Follow up with private numeric original parameter register→compiled pair verification and material property/upload integration, then real ShaderLab/Unity/device validation. T2 identity collision was isolated in a distinct session and work record; shared T2 state/MEMORY left untouched.
