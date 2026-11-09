# T3 RENDER-002 — authentic smoke state extraction contract

session_id=20261109T1829Z-T3-scheduled-smoke-extraction-contract-v6p2
origin=scheduled
base_sha=e18cd6ba082e62ee17dbf36a0489e7034e32d4f7
status=IN_PROGRESS; no CI requested
experiment_key=T3-SMOKE48-AUTHENTIC-PASS-STATE-20261109
shared_resource=none (private ZIP2 export not launched)

## Scope / files
This new work record and an independent T3 session only. No Unity, game assets, .meta, GUID, .rgd, workflows, or shared indexes. T1/T2 own water; T4 owns physical mouse; T5 owns resolution, APK and shared lab. No competing CI run is launched.

## Measured baseline
Owner's artifact 42058825739 entered/saved/reopened world on phone; smoke square and white surfaces persist. In authentic bounded same-export material checks: CI41939404454 matched 227/227 UV slots and 89 internal pointers (25 external not verified); CI41940350604 matched 150/150 RGBA slots. This does NOT establish original smoke Shader48 pass parity. Source-only smoke metadata regression CI42656207137 succeeded, but its fixture uses synthetic a*64 SHA and one synthetic Forward pass.

## Precise remaining experiment and falsifiers
1. Verify ZIP2 provider pin and SHA before parsing. Resolve actual smoke ParticleSystemRenderer -> material slot -> Shader PPtr chain, preserving original fileID/pathID and distinguish 17 renderers / 34 slots from the unrelated 108-use shader. Reject unresolved links or synthetic placeholders.
2. In a single SHA-pinned private exporter invocation, capture original Shader48 and same-export ShaderLab state for every subshader/pass: order, tags/queue, Src/Dst Blend including separate alpha factors, BlendOp including alpha, ZWrite/ZTest, Cull, ColorMask, alpha test/clip, keyword/variant and program presence. Capture linked material main texture alpha reference, tint and particle renderer vertex streams separately. Do not publish original source, compiled shader bytecode, private assets or secret paths.
3. The current scripts/t3_smoke_pass_state_gate_v2.py supports only src_blend,dst_blend,blend_op,zwrite,cull,color_mask,alpha_clip,program_present. It does NOT cover separate alpha blending, ZTest, queue, tags, renderer streams or texture alpha. Do not report its SCOPED_PASS_STATE_MATCH as visual or shader authenticity proof. Authenticate SHA and graph independently; then compare only supported fields and report all unsupported dimensions as UNKNOWN.
4. On verified difference, repair the smallest material/shader/import binding with preserved GUID; test source+export and phone pixel/alpha with same capture method. If same, shift to texture alpha/particle vertex stream and Android shader variant; do not modify original data speculatively.

## Observations / current status
HEAD e18cd6ba082e62ee17dbf36a0489e7034e32d4f7; latest 20 GitHub Actions: no running or queued; T3 smoke run 42656207137 success; T2 Foam 42673027759 failure and 42664186862 success, outside scope. CL test directory contains later shared sessions, but no verified fresh smoke Shader48 pass extraction. No raw CL image decoding or real ZIP2 binary access in this runtime; local git DNS lookup failed. RENDER-002 OPEN, NOT_READY 0/3.

## Resume
Read latest HEAD, T3 chat/scheduled sessions, CL screenshots, and other active scopes before starting private extraction; do not repeat synthetic smoke gate CI. The first required evidence is authenticated Shader48 source/export pass data, not another parser hardening patch.
