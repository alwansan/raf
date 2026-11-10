# T3 scope — original smoke shader provenance
session_id: 20261110T0230Z-T3-scheduled-original-map-handoff-n4q7
origin: scheduled
issue_id: RENDER-002
base_sha: 144a7b9ccba569035af60112f92d7d7b9f8c895d
status: active
intended_files: this work file; prompt/coordination/clients/T3/sessions/20261110T0230Z-T3-scheduled-original-map-handoff-n4q7.md
experiment_key: original-smoke34-sha15964-dxbc-ps-readmask-to-spv-location-instruction-provenance-v1
resource_key: none (read-only original ZIP2 and prior safe aggregate results)
taken_over_from: T3 chat 20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7; T3 scheduled 20261110T0130Z-T3-scheduled-provenance-ci-pass-r8v5

## Question
The 22 actually read DXBC PS lanes vs 28 reflected SPIR-V lanes are not a conversion defect by themselves. Identify whether a private instruction-level dataflow map can be authenticated without exposing original shader bytes; only then validate semantic->Location mapping. A mere location index coincidence (7/7 original, 5/7 roundtrip) is not evidence. This is separate from T4 physical mouse and T5 resolution and mini APK ownership.

## Evidence and bounds
Original private source run 42692895633: 2 permutations, 22/28 used/declared; source-only provenance regression 42728727179 PASS 14/14. No GPU pixel parity, smoke square material attribution, or ShaderLab replacement verified. Owner phone 42058825739 world save/reentry confirmed; preserve that baseline. No Unity/full APK or duplicate Actions. No changes to game resources, .meta, GUID, .rgd, sound or Settings.

## Completion criteria
Either prove an instruction-derived mapping from exact pinned original bytes and verify it privately, or explicitly classify missing provenance and propose a non-fabricated experiment. Keep RENDER-002 OPEN, NOT_READY 0/3.
