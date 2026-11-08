# T2 scheduled checkpoint — 20261108T1219Z-T2-scheduled-foam-il-chain-n6q3

- origin: scheduled
- issue: WATER-001 (OPEN); full readiness NOT_READY 0/3
- branch: feature/android-native-port
- owner phone baseline: 42058825739 / source e9c358eda01785b65e4eb14f18723da426635628. Owner reported world enter/save/exit/re-enter from artifact; Release publish failed. Device logs include 23,884 water-pass and 3,850 FFT errors in 220911-559. Do not infer rendering success.
- resumed_from_sessions: 20261108T0420Z-T2-scheduled-finite-json-7c2e; 20261108T0322Z-T2-scheduled-json-boundary-k7p2; prior T2 source ABI sessions in MEMORY.md; most recent reported pass provenance checkpoint in conversation (no validated new original IL).
- inspected: docs/DEVICE_FEEDBACK_42058825739_AR.md, AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/PROMPT_AR.md, OPERATING_MODEL_AR.md, CHAT_AND_SCHEDULE_AR.md, TRIAL_BUILD_READINESS.md, T2 state/MEMORY, scripts/t2_pass1_stack_provenance.py and t2_foam_pass_crosscheck.py.
- source snapshot: GitHub commit search returned 9b89f62772c2c61f6269fd2249f8560af1522892 among latest; NOT independently established as branch HEAD. Git clone failed: Could not resolve host github.com. No lease-based source edits attempted.
- scoped work: [T2 work](../../../../work/WATER-001/T2-20261108T1219Z-T2-scheduled-foam-il-chain-n6q3.json), created commit ab40355bc5e7d50486b08cea0a6b1af7ce3158c1.

## Engineering finding

The current `scripts/t2_pass1_stack_provenance.py` explicitly rejects `call`, `callvirt`, `ldfld`, `castclass`, branches and merges; it is a bounded straight-line *synthetic* stack model, not an original Mono.Cecil reader. Therefore it cannot prove which texture producer reaches either original Foam Blit or which CB0 member reaches Unity's material upload. The `t2_foam_pass_crosscheck.py` result is only an agreement of sanitized classifications; agreement on unknown cannot prove an original binding. Do not synthesize a ShaderLab pass from these data.

## Result / limitations

Published a non-overlapping work record and this session checkpoint. No original IL extraction, no shader edit, no Unity/Android test, no Actions request or cancellation, and no device success claimed. Current trial voting remains unchanged; no 5/5 consensus.

## Next executable experiment

Use pinned ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385 in isolated private CI scratch; validate assembly byte SHA, extract original Foam call graph and Blit call sites via pinned Mono.Cecil, compute branch-aware producer chains for source/destination and material CB0 upload, fail closed on unknown branch or alias, publish sanitized aggregate only. Compare T3's original material/texture link, then integrate authenticated ShaderLab after resource/render-state evidence. Avoid repeating already green synthetic JSON gates.
