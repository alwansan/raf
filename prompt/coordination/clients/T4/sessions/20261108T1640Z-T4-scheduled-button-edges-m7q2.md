# T4 scheduled — mouse button edge evidence, 2026-11-08 16:40 UTC

- session_id: `20261108T1640Z-T4-scheduled-button-edges-m7q2`
- origin: `scheduled`; worker: T4; issue: INPUT-005.
- starting HEAD: `1ed64d0394ddc1b063067431468cbc5b8a537197`.
- resumed_from: `20261108T1540Z-T4-chat-mini-lab-c6p4`, `20261108T1536Z-T4-scheduled-route-analyzer-n8q4`.
- independent scope: `prompt/coordination/work/INPUT-005/T4-20261108T1640Z-T4-scheduled-button-edges-m7q2.json`, reservation `08d4ecb4`.
- implementation `b44bbb8c`: source-only route analyzer now exposes `button_presses_observed` and `button_releases_observed` separately from legacy `buttons_observed` (which includes held-state bits on movement). Only explicit `ACTION_BUTTON_PRESS/RELEASE` or `ACTION_DOWN/UP` with nonzero `actionButton` count as edges. This conservative criterion deliberately does not infer an edge when `actionButton=0`.
- tests `70c90a75`: two regression cases covering held button during movement versus actual press/release, and ambiguous `ACTION_DOWN` with zero `actionButton`. Source tests have **not** yet been executed in CI; no device acceptance claim.
- Owner phone evidence: artifact 42058825739 successfully entered, saved and reopened world. Newer 2026-11-08 feedback says captured camera motion works, but left/right/middle and scroll fail in full game. CL summary does not expose mouse callbacks.
- Independent mini APK: [42496622364](https://github.com/alwansan/raf/actions/runs/42496622364) SUCCESS; artifact 13623563385, APK SHA256 `a5a42b89642c75946f7d3fd5e46fab83b1f16ee800cbd7c2056a7ab74f3e2849`, device untested. No new APK/Unity/CI run requested.
- Current gate: Android 15 ON/OFF exported JSONL and corresponding full Raft input evidence needed to distinguish Android dispatch from Unity bridge. Analyzer output cannot prove game Mouse0/1/2 or scroll. Preserve camera pointer capture, keyboard, original .rgd, audio, Settings; T5 owns three UI buttons and Resolution.
- Next: run `python3 -m unittest tests.test_t4_analyze_mouse_lab_routes` on source and use T4-01..09 phone logs to compare edge callbacks across capture phases. No changes to shared host or other workers.
