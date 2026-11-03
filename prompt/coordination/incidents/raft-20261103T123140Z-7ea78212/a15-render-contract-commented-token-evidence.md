# A15 RENDER-002 — comment/string token pollution in render-contract source evidence

- **Author:** A15 raft-20261103T123140Z-7ea78212; **UTC:** 2026-11-03T15:07:26.991Z
- **Mechanism:** in-run `scripts/audit_render_input_contracts.py` counted `Pass {`, `CGPROGRAM/HLSLPROGRAM`, `Shader` headers and `#pragma kernel` in comments/quoted text; ignored `Pass /*comment*/ {`. Actual native preview41624581951 140-file histogram was produced by this tool, but no proof that original histogram was affected.
- **RED:** [CI41659903543](https://github.com/alwansan/raf/actions/runs/41659903543) deliberately **FAILED 5/6**, positive control passed, on synthetics after fixture escape correction.
- **Fix:** [d0680dbd](https://github.com/alwansan/raf/commit/d0680dbd16676c54fb7473f797c26f58e76c786e) reuses established ShaderLab comment/string lexer and identity reader; counts only source tokens outside masked regions.
- **GREEN:** [CI41660138192](https://github.com/alwansan/raf/actions/runs/41660138192) **SUCCESS 6/6 A15 +4/4 A9** on exact fixed SHA. No game shader or original resource modified.
- **Limit:** no original full-export input, compiler preprocessing, Unity pass/GPU execution, APK/device proof. Old [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) strict zero-match still unresolved. RENDER-002/WATER-001 OPEN, game NOT_READY, 0/3 full immutable readiness audits.
- **Status:** scoped diagnostic source flaw fixed for tested cases. No native requests, LFS, CL, releases or tasks touched.
