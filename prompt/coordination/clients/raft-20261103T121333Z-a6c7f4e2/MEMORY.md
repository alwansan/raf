# A6 — RENDER-002 comment-only include scanner, 2026-11-03

Resumed from A6 identity raft-20261103T100042Z-afcedabb with new independent session. Live initial HEAD 98fa7380811d7251b011b158e6a50318c5186763. Writability strictly feature/android-native-port; CL read only; no Unity/APK/OBB/XAPK, native request, releases, LFS or automations.

Read owner files prompt/README, CONTINUE_RAFT_AR, STATUS, docs/CURRENT_OWNER_REQUIREMENTS, AGENTS, coordination README, readiness, A9 shader state, current restore_builtin_shaders and test source. A9 shader identity work is completed and verified with Actions 41629545330 / 41629545455, source d159f348e06af597e04507ae19ddda5590265e9f. A6 scope is strictly the independent quoted include matcher rewrite(); do not replace A9 exported_shader_identity() nor loosen zero built-in identity match blocker.

Independent local prior evidence: the original rewrite() mistakenly treats #include present in ShaderLab comments as a required file. Prior A6 synthetic red tests (10 tests, two errors), followed by a local patch against the earlier verified A9 source (10/10 passed). Patch /mnt/data/A6_shader_include_comment_guard.patch and evidence report are ephemeral conversation artifacts; only repo records persist. Revalidate against latest HEAD and run same-source targeted CPU CI before completion.

Last real game native 41624581951 failed at no authenticated exported built-in identity matched, pre-Unity; that is NOT repaired by this include parser scope. Overall NOT_READY, 0/3 immutable candidate reviews. No claims about missing GPU/water shaders.

## Completed A6 include-only correction — 2026-11-03T12:13:25.402Z

- Registered independent A6 client state/work/experiment before code changes. A9 exported ShaderLab identity fix already complete; different production function `rewrite()` selected deliberately.
- Reproduced false mandatory `#include` inside commented line/block in synthetic cases; pre-patch local tests had 2 failures (10 total). The local A6 patch had already demonstrated 10/10 green; after confirming live script/test SHA and A9 completion, published [source fa4647359f07b0734e6013dade930b9b010bc1f6](https://github.com/alwansan/raf/commit/fa4647359f07b0734e6013dade930b9b010bc1f6) with expected-SHA nonforce update, exactly two files (+40/-3): restorer and tests.
- [Built-in no-LFS CPU Actions 41633638783](https://github.com/alwansan/raf/actions/runs/41633638783) COMPLETED SUCCESS at exact source SHA fa4647359f07b0734e6013dade930b9b010bc1f6: 10/10 Python unit tests; authentic SHA256-pinned Unity 2021.3.45f2 ZIP yielded 198 official shader identities; five controlled shaders and 29 includes restored while .meta untouched.
- [A9 same-source CPU Actions 41633638754](https://github.com/alwansan/raf/actions/runs/41633638754) COMPLETED SUCCESS with 4/4 A9 lexer fixtures and new 10/10 underlying shader tests. No overlap or overwrite of A9 declaration parser.
- [A6 report](../../../../docs/A6_BUILTIN_SHADER_INCLUDE_COMMENTS_2026-11-03.md). No full Unity/native, device, APK/OBB/XAPK, releases, LFS, original assets/ShaderLab programs, scheduled tasks or CL modification by A6.
- The distinct original game no-match from [native 41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) is NOT fixed or re-tested; zero-match fail-closed remains. RENDER-002 / WATER-001 / FFT-FORMAT-009 still OPEN, game NOT_READY, 0/3.
