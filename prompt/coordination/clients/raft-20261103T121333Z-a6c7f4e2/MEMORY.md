# A6 — RENDER-002 comment-only include scanner, 2026-11-03

Resumed from A6 identity raft-20261103T100042Z-afcedabb with new independent session. Live initial HEAD 98fa7380811d7251b011b158e6a50318c5186763. Writability strictly feature/android-native-port; CL read only; no Unity/APK/OBB/XAPK, native request, releases, LFS or automations.

Read owner files prompt/README, CONTINUE_RAFT_AR, STATUS, docs/CURRENT_OWNER_REQUIREMENTS, AGENTS, coordination README, readiness, A9 shader state, current restore_builtin_shaders and test source. A9 shader identity work is completed and verified with Actions 41629545330 / 41629545455, source d159f348e06af597e04507ae19ddda5590265e9f. A6 scope is strictly the independent quoted include matcher rewrite(); do not replace A9 exported_shader_identity() nor loosen zero built-in identity match blocker.

Independent local prior evidence: the original rewrite() mistakenly treats #include present in ShaderLab comments as a required file. Prior A6 synthetic red tests (10 tests, two errors), followed by a local patch against the earlier verified A9 source (10/10 passed). Patch /mnt/data/A6_shader_include_comment_guard.patch and evidence report are ephemeral conversation artifacts; only repo records persist. Revalidate against latest HEAD and run same-source targeted CPU CI before completion.

Last real game native 41624581951 failed at no authenticated exported built-in identity matched, pre-Unity; that is NOT repaired by this include parser scope. Overall NOT_READY, 0/3 immutable candidate reviews. No claims about missing GPU/water shaders.
