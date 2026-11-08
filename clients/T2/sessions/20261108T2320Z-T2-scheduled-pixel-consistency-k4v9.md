# T2 scheduled — CASE02 RGBA evidence numeric consistency
session_id: 20261108T2320Z-T2-scheduled-pixel-consistency-k4v9
origin: scheduled
base_sha: 724d80cda6a249fedfa4096eebad0c6c8c68a96c
resumed_from: clients/T2/sessions/20261108T2120Z-T2-scheduled-gles-evidence-q6m2.md; clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md
issue_id: WATER-001 OPEN
owner_phone_baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/reopen on artifact 42058825739 is device-confirmed only for that build; water/FFT remains unresolved.
experiment_key: T2-CASE02-RGBA-NUMERIC-RELATION-20261109
scope: T2 synthetic GLES JSONL gate only, no Unity/ShaderLab/other workers' files.
work: work/experiments/20261108T2320Z-T2-scheduled-pixel-consistency-k4v9.md
result: Published numeric CASE02 four-channel RGBA parser and <=2 source-to-final readback comparison plus required output contrast. Added adversarial regression coverage. Previous gate only checked textual markers.
commits: bb29d1af2b2d603a6bcee2ab1b8414eca4572be3; 65dddd277c19f9e31eed1f79ea369c82dafc3efc; aa7b4f70c117a387fa489101948f56ae6d539def
verification: Published source reread; regex smoke-check locally with representative synthetic detail PASS. Full unittest and CL four-file gate not executed because runtime network DNS to github.com failed. No CI launched or cancelled.
limits: text self-consistency is not GPU pixel authenticity, original Foam pass1 CFG/CB0/samplers and Raft device water remain unproven.
next_step: execute Python unittest and CL four JSONL cases; original source pass1 CFG join and instance producer proof, then CB0/ShaderLab integration with T3; protect T5 shared mini and T4 physical mouse/Resolution assignments.
