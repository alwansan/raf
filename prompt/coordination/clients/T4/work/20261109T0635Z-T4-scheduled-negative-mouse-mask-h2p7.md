# T4 INPUT-005 — strict physical mouse masks
session_id: 20261109T0635Z-T4-scheduled-h2p7
origin: scheduled
base_head: abe098d9763965d5bcd9a6ba79a6590246e154df
scope: scripts/t4_analyze_mouse_lab_routes.py; scripts/t4_test_negative_mouse_masks.py; own session file only.
Hypothesis: negative Android source/buttonState/actionButton values in untrusted JSONL pass bitmask checks and create false physical-mouse button evidence. Reject negative values without changing legitimate Android callbacks. No Unity/game, keyboard, .rgd, Settings, touch, T5 UI or Resolution changes.
Experiment: INPUT-005-T4-NEGATIVE-MASK-20261109. Shared resources: none; source-only. No duplicate CI.
Evidence: owner 42058825739 world save/reopen success, mouse captured click unproven. Previous T4 route/flag tests published, execution pending. T5 owns shared mini APK.
