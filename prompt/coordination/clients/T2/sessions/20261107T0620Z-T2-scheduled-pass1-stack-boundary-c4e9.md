# T2 — bounded synthetic pass-1 producer model

- session_id: 20261107T0620Z-T2-scheduled-pass1-stack-boundary-c4e9
- origin: scheduled
- baseline HEAD: bed4ca38d9313ed238b815a7090e8b184253e904
- owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; device world entry/save/reopen confirmed from 42058825739 artifact, release publication failed. Water pass and FFT errors persist.
- restored: docs/T2_FOAM_PASS_ROLE_AUTHENTIC_2026-11-07.md, 20261107T0519Z-T2-scheduled-pass1-producer-a91f.md, chat 20261107T2227Z-T2-chat-blit-texture-role-6c52.md; old state/MEMORY are historical.
- live actions first page: 42333961072 T3 success; 42308583977 T2 original success; 42308935364 summary failure. No duplicate CI or native build initiated.
- scope: prompt/coordination/work/WATER-001/20261107T0620Z-T2-scheduled-pass1-stack-boundary-c4e9.json published before code at 855cbeb75b81c1aab22046f010bc90be38f7ef32.
- new code: scripts/t2_pass1_stack_provenance.py at c9978a319cf860797233afa607ef4f20840b5df2; tests/test_t2_pass1_stack_provenance.py at 5e6eb1dd7f1ed00fd9a8928b2ac3eae26636f966.
- implementation: bounded straight-line abstract stack interpreter for explicit typed ldarg, ldnull, dup, stloc/ldloc, pop. Rejects unknown ops, branches, field aliases, calls, uninitialized locals, malformed shape and excessive budget. Keeps origin label distinct from type. Twelve source-free synthetic test cases authored; **not yet executed by CI**. No original game bytes or IL published.
- boundary: this model does not parse authentic Mono.Cecil IL or resolve pass1. Authentic pass0 RenderTexture -> RenderTexture; pass1 UNKNOWN -> UNKNOWN. WATER-001 OPEN. No shader, Unity scene, GUID, .rgd, Settings, audio, touch or native request changed.
- next: execute synthetic tests, review with chat-owned analyzer for nonoverlapping adapter, then apply to pinned authentic IL in private CI with branch/exception-handler rejection and sanitized report. Coordinate T3 graphics; no new APK trial vote absent integrated shader.
