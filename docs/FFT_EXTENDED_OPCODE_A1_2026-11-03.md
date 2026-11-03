# A1 SPIR-V GLSL.std.450 extended instruction opcode identity — 3 November 2026

## Scoped evidence

Client `raft-20261103T112510Z-a1ef930c`, branch `feature/android-native-port`, [exact source 3fa646ed1dca28071d2b65c6394f0003231362e6](https://github.com/alwansan/raf/commit/3fa646ed1dca28071d2b65c6394f0003231362e6). The earlier A1 arithmetic census showed the same *total* OpExtInst count in each authentic original/roundtrip FFT pair but did not identify public extended operation numbers. This new, separate CPU-only experiment decodes OpExtInstImport references and numeric OpExtInst instruction IDs in the public Khronos `GLSL.std.450` set. It never publishes original shader names, source, raw SPIR-V operands or binaries. Unknown extension sets are counted but never considered equivalent solely because their raw instruction numbers match.

## Code and negative controls

- New `scripts/probe_fft_spirv_extinst_profile.py` validates bounded SPIR-V wordstreams, import identity and numeric public GLSL.std.450 opcode histogram, without publishing import names; unknown/nonstandard references fail comparability and unresolved imports raise.
- `tests/test_probe_fft_spirv_extinst_profile.py`: 8 synthetic tests, including **same total OpExtInst but a different public opcode**, same public histogram but different operands (explicitly *not* mathematical proof), nonstandard import classification, mixed sources, missing imports, malformed/duplicate import and inconsistent counts.
- Private original pipeline `scripts/probe_authentic_fft_dxbc_translation.py` compares original SHA-pinned module against the privately roundtripped module. Existing CPU-only workflows were updated only to include this distinct test; Unity/APK workflows and native request files untouched.

## Exact source CI

- [Synthetic CI 41627854878](https://github.com/alwansan/raf/actions/runs/41627854878), job125889663239, **COMPLETED SUCCESS** on source `3fa646ed1dca28071d2b65c6394f0003231362e6`; all 8 new tests pass, along with the existing isolated FFT suite.
- [Authenticated three-owner 20-program private audit 41627854853](https://github.com/alwansan/raf/actions/runs/41627854853), job125889663438, **COMPLETED SUCCESS** on same source SHA; original LFS objects verified before any translation. No original SPIR-V was published.
- **20/20** original programs converted and validated Vulkan1.1; **20/20** bindings and workgroup signatures preserved; **20/20** public `GLSL.std.450` numeric opcode profiles matched the roundtrip exactly. Original and roundtrip each contained **105 classified extended instructions across all20** and **0 unclassified extended calls**.
- Existing arithmetic/SSA profile match remains **0/20**, typed-image declaration match **0/20**, original water resource contract **false**. Matching public instruction *types and counts* is not operand identity, floating-point equivalence, image-format interoperability, original Unity kernel identity, or physical GPU execution.

## Safe boundaries and handoff

Only source-only diagnostic Python and isolated workflows changed, no Unity assets, original shader bytes, .meta/GUID, .rgd, LEFT Mouse0/500ms, Xbox or UGUI, materials, LFS source, Release, native request, build or automations. CL raft-log/lf has the same four 2026-11-02 historical sessions and no new Android device acceptance. An independently launched full native run [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) on older SHA c7254f7d finished failure in the built-in shader restore job; A1 neither requested nor cancelled it, and this CPU result does not resolve it.

**Project NOT_READY, 0/3 complete immutable-candidate readiness reviews**. WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN. Next real experiment: operand/type/SSA def-use or CPU FFT numerical replay using authenticated actual shader data and exact resource formats; do not interpret histogram equality as semantic proof.
