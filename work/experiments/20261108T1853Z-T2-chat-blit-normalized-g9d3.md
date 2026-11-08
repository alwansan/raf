# T2 — synthetic normalized Foam Blit operand evaluation gate (2026-11-08 UTC)
session_id: 20261108T1853Z-T2-chat-blit-normalized-g9d3
origin: chat
branch: feature/android-native-port
base_sha: 21ae71a828d55da9337fa252f38c8b39b7a6395c
resource_key: WATER-001 (OPEN)
experiment_key: T2-FOAM-BLIT-NORMALIZED-20261108
status: SOURCE_ONLY_TESTED; AUTHENTIC_ORIGINAL_PRODUCER_UNVERIFIED
resumed_from: clients/T2/sessions/20261108T1817Z-T2-chat-fbo-contrast-92d4.md and clients/T2/sessions/20261108T1822Z-T2-scheduled-gl-ready-k8p3.md
taken_over_from: work/experiments/20261108T1119Z-T2-scheduled-pass1-original-chain-m6r8.md
scope: T2-only source-free normalized CIL validation; no proprietary DLL/assets/Unity/Android changes
intended_files:
  - scripts/t2_foam_blit_operand_gate.py
  - tests/test_t2_foam_blit_operand_gate.py
  - T2 own chat session, memory, state, work

## Source engineering
Existing `scripts/t2_pass1_stack_provenance.py` models ldarg/ldloc/stloc/dup/pop but rejects call; it cannot validate which stack values an exact four-argument Graphics.Blit consumes. New bounded `classify_two_pass_blits` handles a **source-free** normalized straight-line CIL fixture with explicit typed argument/local values and exact static overload descriptor (Texture, RenderTexture, Material, Int32) and pass literal 0/1; only two unique sites allowed. On unknown/unsupported instruction, branch, field access, instance/callvirt, cast, type alias, pass/descriptor mismatch, stack underflow, 128-step budget or >32 stack entries: raises Unresolved; no guessed matching.
- Source commit: [e98e0d6147e57c2dd42d3a844b8b05615a6bd89f](https://github.com/alwansan/raf/commit/e98e0d6147e57c2dd42d3a844b8b05615a6bd89f), blob `5424874afc7b767495355c44fa051ed16dde92e9`.
- Tests commit: [3a0f82bccc1f44b8f2862fe2f618f01748ec0cdc](https://github.com/alwansan/raf/commit/3a0f82bccc1f44b8f2862fe2f618f01748ec0cdc), blob `2086915118606137fcaa6da6030e1d9e17570ada`.
- Container scratch `PYTHONPATH=/mnt/data/t2_work python3 -m unittest discover -s /mnt/data/t2_work/tests -p test_t2_foam_blit_operand_gate.py -v`: **10/10 PASS**; `py_compile` PASS. Re-fetched live GitHub text sizes 5911B and 5269B, matching scratch source sizes; no GitHub CI launched for this source-free tool. It does not ingest original IL and no matching original managed field identifiers or actual original Foam producer/destination have been proven.

## Evidence boundaries
- Output includes `normalized_fixture_only=true`, `original_assembly_authenticated=false`, `original_texture_instance_identity_proven=false`, `Unity_or_Android_pixels_verified=false`. No private DLL/raw IL/PathIDs/short-name hashes/compiled shaders exported.
- The chosen overload descriptor is a **caller-provided normalized fixture**, and passing it never authenticates a real Unity method call or underlying source/destination identity. A private authentic Mono.Cecil emitter must validate original SHA and real typed method/callsite bodies; field/call/CFG producer modeling and crosspass target identity remain blocked.
- Do not conflate this bounded source model with FBO evidence or original Raft ShaderLab recovery. WATER-001 still OPEN / full game NOT_READY.

## Shared mini-lab delivery reconciliation
- [CI42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) SUCCESS, first team lab r1; exact embedded parent `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8` contains T2 current `T2GpuActivity.java` blob `6a7abb91f3356e4e2fcb688c8953219859d8bc1d` (two-stage contrast + 7s EGL readiness).
- [T2 own row d11d383f8bd222c7873f50a97d348d955998f44c](https://github.com/alwansan/raf/commit/d11d383f8bd222c7873f50a97d348d955998f44c) = NO_BUILD in shared-20261108-r2; original APK ZIP only, versionCode 9, SHA256 cee2df1b3bb2a1a3c8e9ab757f520040d36c5bf16d711587f7e2bc537f917472. No duplicate mini, no full XAPK request. Need Android 15 T2-01..04 raw JSONL plus visual/full game evidence separately.

## Next
1. Privately authenticate ZIP2 managed assembly byte SHA and real Mono.Cecil typed `Graphics.Blit` callsites (exact signature and pass constants), then normalize actual producers from field/branch paths or report Unresolved; protect private IDs.
2. Cross-check original Foam pass0/1 argument roles with strict independent aggregate, actual source-to-destination resource lineage, original CB0 offsets, samplers, pass states, material and shader binding before real Unity compile and device pixels.
3. Ask T5 to use existing shared APK for first device pass; do NOT reissue a build for this Python-only tool.
