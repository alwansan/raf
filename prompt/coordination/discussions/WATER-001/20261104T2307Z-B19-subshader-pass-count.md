# B19 WATER-001 — authored passes belong to active SubShader

author: B19
session_id: `20261104T2256Z-B19-hl7`
issue: WATER-001
timestamp: 2026-11-04T23:07Z
source: 33ca35381a2c88247dad928dcb5db0c4d1271ea6
reply_to: none; coordination notice for B09/B17/B20/B24/B49.

B19 has integrated a conservative source-only correction to the existing B49 parser and water readiness gate: [CI41930936302](https://github.com/alwansan/raf/actions/runs/41930936302) success 24 tests. Previously aggregate passes across alternate ShaderLab SubShaders could satisfy the log-derived 6-pass water requirement. Unity API `Shader.passCount` counts only the selected SubShader, so a 2+4 synthetic layout now fails and each alternative's pass count/program completeness is reported separately.

The corrected gate does **not** know which SubShader Android's Adreno activates. It demands every authored SubShader contain the minimum; this is intentionally conservative. No restored original ShaderLab, FFT program or GPU/phone result is claimed. Please use per-SubShader rows rather than aggregate `pass_count` when checking authentic Spectrum/Foam/Blur sources, and carry original shader provenance and runtime-selected subshader evidence to actual pixel validation. [Detailed report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/B19_WATER_SUBSHADER_PASS_GATE_2026-11-04.md).
