# B18 — authenticated original FFT DXBC resource role parity

2026-11-04 / WATER-001. This experiment compares authentic compiled
DXBC t0/t1/u0 + threadgroup declarations to same-slot Unity serialized
resource metadata; no private shader/source code or image bytes published.

## Successful authenticated original evidence

- CI: https://github.com/alwansan/raf/actions/runs/41922333604
- Source changes: https://github.com/alwansan/raf/commit/42476b87626031f23db37808d00e1c76604e5b33
- Immutable ZIP2 source: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- Original reassembled Raft_Data/sharedassets0.assets: 115978112 bytes,
  SHA256 0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3
- Original FFT ComputeShader pathID2456 SHA256:
  9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247
- Source-free synthetic controls 13/13 PASS, exact original SHA and ordered
  compiled program authentication PASS, 20/20 executable SHDR/SHEX compiled
  program t0/t1/u0 read/read/write numeric roles and workgroup XYZ agree with
  same-slot original Unity serialized metadata.
- RDEF reflection chunks detected in those original compiled programs: 0.
  Compiled resource names therefore NOT proven by this path.

## Negative hypotheses — retained

Initial RDEF-only hypothesis fails on authentic source even while synthetic
fixtures pass: CI41920845862 and CI41921227456 REJECTED because RDEF absent.
CI41921950901 synthetic test error from tuple length extraction, corrected
at ee91a759. CI41922116469 synthetic passed but original rejected extra DXBC
instruction encoding; official CustomData block and unrelated extended
instruction length handling fixed in 42476b8. CI41922333604 SUCCESS.

## Scope

Code scripts/b18_fft_compiled_rdef_bindings.py
Tests tests/test_b18_fft_compiled_rdef_bindings.py
Workflow .github/workflows/raft-b18-fft-rdef-parity.yml

The parser uses SHA-authenticated original ZIP2 owner, exact original FFT
object bytes SHA, typed-to-original compiled DXBC order check, strict
resource register and workgroup shape constraints; disallows unknown
resource/CB/sampler declarations, duplicate registers and malformed tokens.
Where RDEF exists in synthetic fixtures, SHA-only names also match. Where
RDEF is absent in authentic original programs, numeric SHEX declarations
are checked but names are explicitly not inferred.

Outstanding: Unity runtime FindKernel index to compiled program mapping,
actual authoritative ComputeShader import into Unity, GPU execution on
Adreno, water visual screenshot fidelity and device effects. Compiled slot
is not runtime kernel index. Do not mark WATER-001 resolved or claim
Android device render. No ShaderLab, Unity/game source, textures, .meta/GUID,
.rgd, audio, Settings or deferred touch modifications. NOT_READY 0/3.

Public format reference:
https://github.com/tpn/winsdk-10/blob/master/Include/10.0.10240.0/um/d3d11TokenizedProgramFormat.hpp

## Follow-up: source authentic DXBC -> SPIR-V image role verification

B18 second separate workflow:
https://github.com/alwansan/raf/actions/runs/41923703800
Source commit: ea07d9d1c8d6009df460a102ee95dbdf25792a91

Original pinned ZIP2 source owner and original FFT object re-authenticated.
10/10 independent synthetic tests PASS. Twenty of twenty real compiled
original DXBC programs translated privately by vkd3d-compiler; each
generated SPIR-V program has exactly two *sampled* Texture2D input images,
one *storage* Texture2D output image and the same compute local-workgroup
shape as the input DXBC declarations. No proprietary module uploaded.

This adds evidence that **image resource class/count** survived a
DXBC-to-SPIR-V translation across the original 20 slots, but does not
establish which exact source t0/t1/u0 register maps to which destination
SPIR-V DescriptorSet/Binding. The translated modules are not installed
into Unity. Native Unity FindKernel, texture SetTexture call binding,
correct actual ShaderLab reconstruction, phone Adreno output, source
materials and full 3D scene pixels remain UNTESTED. WATER-001 OPEN.
