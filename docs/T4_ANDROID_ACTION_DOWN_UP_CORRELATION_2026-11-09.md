# T4 INPUT-005 — Android `ACTION_DOWN/UP` and explicit button edges in real owner CL

**Date:** 2026-11-09 UTC · **Worker:** T4 · **Origin:** chat · **Session:** `20261109T0144Z-T4-chat-downup-correlation-n6q2` · **Scope:** source-only diagnostics; **INPUT-005 OPEN**.

## Immutable evidence
- Read-only phone upload in `alwansan/CL` commit `4680f5dc26127938e7696f932b2d9a80dc703937`.
- Exact raw trace: `test/shared-20261108-223228-464718661/events-20261108-223341-464791801.jsonl`, Git blob `7c337320a1593ff8d9f9fd63e55ec30ed62cd202`.
- Exact summary: `test/shared-20261108-223228-464718661/summary-20261108-223228-464718661.json`, blob `6d702c231aa95386ace9fe85b25e244a6ce8bf8c`.
- Device Android 15, POCO F5 Pro, unified Mini `0.2.9-shared` source `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8b`. This trace is **not** captured Unity gameplay input and is **not** Mini v0.2.13 evidence.

## Original callback-level finding
After deduplicating matching View/Activity events (ignoring per-View coordinate changes), 413 physical mouse callback records yield 373 distinct Android event signatures (40 duplicate callback records). The unique route stream has:
- `ACTION_DOWN` **13** and `ACTION_UP` **13**, all with `actionButton=0`;
- `ACTION_BUTTON_PRESS` **13** and `ACTION_BUTTON_RELEASE` **13**, explicit `actionButton=1` (left);
- all **13** implicit down transitions are timestamp/source/capture-matched to an explicit left press; all **13** implicit up transitions match an explicit left release;
- additional clicks inferred from the implicit records: **0**, unmatched ambiguous down/up in this one trace: **0**;
- 55 distinct vertical scroll events, **0 captured=true**, **0 capture_request ON/OFF**, no measured right/middle/horizontal wheel attempts.

A representative click contains `ACTION_HOVER_EXIT` + `ACTION_DOWN(buttonState=1,actionButton=0)` + `ACTION_BUTTON_PRESS(actionButton=1)` at Android `eventTime=326202353`, and both release and up at `326202556`. Thus treating both down and explicit press as separate clicks would double count physical actions. Conversely, ignoring down/up transitions could leave a useful *candidate* unreported if a future captured device emits no explicit button event.

## Change and assertion boundary
`scripts/t4_verify_cl_shared_mouse_evidence.py` now exposes `implicit_down_up_correlation`:
`actionbutton_zero`, `matched_to_explicit_same_eventtime`, `unpaired_ambiguous_not_click_proof`, `additional_clicks_inferred=0`, and `unity_delivery_proven=false`. Correlation requires exact eventTime, physical source, capture flag, unique explicit edge and consistent state; absent/mismatched timestamps or sources remain ambiguous, NEVER synthesized into clicks. Legacy logs do **not** include physical device ID, so this is evidence of same-stream timestamp correlation, not cryptographic device/gesture identity. Android captured callback presence changes the limitations sentence, but cannot turn Unity or Raft acceptance true.

`tests/test_t4_verify_cl_shared_mouse_evidence.py` adds 4 regressions (same-clock explicit pair, unrelated time, captured mismatch, missing time/bad state) and an assertion that captured telemetry must not be described as absent. Existing authentic Git blob/SHA/provenance guards remain intact.

## CI
- Source and genuine pinned CL trace: [42547259000](https://github.com/alwansan/raf/actions/runs/42547259000) SUCCESS — **13/13 Python controls**, original 413→373 callbacks, 13/13 paired down/up and zero extra clicks.
- Follow-up dynamic limitation source: [42547355733](https://github.com/alwansan/raf/actions/runs/42547355733) SUCCESS; final post-assertion source/test [42547368125](https://github.com/alwansan/raf/actions/runs/42547368125) pending verification at report creation.
- No full Unity game build, shared Mini APK, signed Raft Android test, REA decompilation, owner CL modification or changes to camera/touch/.rgd/Settings/audio.

## Next authoritative test
On T5's shared single Mini, owner opens **T4-02 blue INPUT PAD**, taps **Capture ON**, then tries actual LEFT/RIGHT/MIDDLE and vertical/horizontal wheel with USB/Bluetooth physical mouse and exports `Download/Games/cl/test/shared-.../` to CL/test. T4 compares `route=captured,captured=true`, source and event times under capture lease, then compares actual **same signed game SHA** Unity Legacy Mouse0/1/2 and `Mouse ScrollWheel` consumption with preserved camera motion. Only a game device trial could verify INPUT-005; do not rebuild Mini for this source-only analyzer.
