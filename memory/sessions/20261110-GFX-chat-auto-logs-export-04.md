# GFX-LAB — 20261110-GFX-chat-auto-logs-export-04

- session_id: `20261110-GFX-chat-auto-logs-export-04`; origin: `chat`; resumed_from: `20261110-GFX-chat-material-delta-03`
- base_sha: `a134108fac5f59e503aab388969abbb9720b2e66`
- source SHA: `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- status: `IMPLEMENTING`
- user destination: `/storage/emulated/0/Download/Games/cl/test/g/`

## Scope and acceptance
After user 16 photos/13 COPY LOG lacked individual channel and sampling changes, implement automatic per-state snapshots and every Unity log including full stack traces. Store all historical sessions in app persistentDataPath and compress into ZIP with one button. Android >=29 scoped MediaStore.Downloads sets RELATIVE_PATH=Download/Games/cl/test/g/. On failure keep private ZIP, show error (no fake external export success). No Android root/unsafe MANAGE_EXTERNAL_STORAGE permission. Signed Android Unity2021.3 GLES3 APK to be built separately in GFX-LAB branch.

## Negative controls
Original Shader48 shader NOT restored; Standard/ChannelProbe diagnostic only. Original source private inside GitHub runner. No T-Team/production branch edits. Device owner must independently confirm external ZIP path and file contents after installing resulting APK; Unity compile and emulator cannot guarantee actual MIUI filesystem behavior. Continue deeper Shader48 source investigations as independent scope, closure gates in gfxlab/SHADER48_MODEL_PHASE_CLOSURE_AR.md.

## Runs and results
Pending.
