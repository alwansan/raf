# A1 resumed – SPIR-V image operation coverage

- Session a1-20261103T104800Z-c9d8612a, 2026-11-03T10:48:31.736Z; resumed_from raft-20261103T100100Z-a1c46e79 (paused, parser collision repair completed).
- Live base 802e82fc599822a328057d7da7aee05b045605ad; protected branches main/zip/Unity-Editor untouched; CL read-only.
- Read owner/prompt/STATUS/AGENTS and coordination requirements; previous A1 synthetic CI 41616248165 and SHA-pinned original 41616248166 SUCCESS, but no actual shader equivalence; WATER-001 remains open.
- Other WATER work raft-20261103T103610Z-4e91b2cd (original caller precision; paused) touches probe_fft_caller_policy.py, not image-flow parser. Prior A1 was paused; no evidence of current concurrent edit to image-flow parser. Read WATER-001 plan/discussions before working.
- Focus: check omissions in sampled image/gather resource-use accounting against Khronos SPIR-V grammar; synthetic only, no proprietary shader bytes or GPU execution.
- Next: add regression fixture first, then narrow fail-closed/complete tracing behavior, run local tests and only then source commit. Stay NOT_READY/0-of-3.
