# T3 resumed independent session — 20261105T0028Z-T3-externaltex-7af2

Identity T3, generation T-2026-11-05. Resumed_from_session: `20261104T2354Z-T3-render-harness` (state shows paused). Worktree branch only feature/android-native-port. Baseline HEAD seen `6f899a2d2bd03cf74d7f0d8628e09dc59a08811a`.

## Identity coordination
At resume, active real T3 action [41941363661](https://github.com/alwansan/raf/actions/runs/41941363661) on `6940ccf0161a3ea4a52c083702692de74c0c64be` was running B43 same-instance original Material keyword/disabled-pass comparison. Assume another T3 work continuation is possible: **do not overwrite shared clients/T3/state.json or MEMORY.md**; record this isolated session and experiment, do not modify ongoing same T3 workflow or cancel its job. Original session B05/B44 actual export results 41939404454/41940350604 remain accepted on bounded sharedassets6 only.

## Current inherited facts
Selected original owner ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385` `sharedassets6.assets` 6607272B SHA256 `0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632`; 41 Materials, 227 TexEnv and UV slots: 89 exact same-owner Texture pointers, 113 source nulls, **25 source-external pointer targets remain unverified** in actual same-instance export. Source RGBA 150/150 matched. No Android pixels, no new Raft game APK; latest tagged game APK86. CL/main is `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29`. T5 asset hydration 41940032540 succeeded; preserve other T runs. This session handles only 25 cross-owner Texture bindings and avoids B43 keyword overlap.

## Plan before engineering
1. Implement exact original external `m_FileID`→`source_file.externals` provider mapping with ZIP2 filename+SHA pinned manifest. Do not guess an owner by basename alone if ambiguous, and never trust bare `m_PathID`.
2. Reuse authenticated selected original Materials and B02/W1 same-process exported texture traces. If external provider(s) staged, prove original referenced target is actually Texture2D and compare mapped export tuple exact GUID/fileID/type to actual exported material `m_TexEnvs` pointer. Report only counts, never source IDs, names, GUIDs, private paths.
3. Add regression controls (wrong owner, path collision, mismatched GUID, absent provider/target, null controls, UV unchanged). Use isolated T3 external-only workflow with no concurrent cancellation, SHA pins/timeout. Add files under `scripts/t3_external_texture_*.py`, `tests/test_t3_external_texture_*.py`, and `.github/workflows/raft-t3-external-texenv-export.yml`; do not modify current T3 B43 workflow.
4. If unable to stage authentic external provider in bounded budget, record exact unresolved categories without claiming validation. Keep `RENDER-002` OPEN, audio/Settings and deferred touch unchanged.

## Initial run audit
Latest observed HEAD `6f899a2d2bd03cf74d7f0d8628e09dc59a08811a`; active: T5 41941373300 graphics staging, T3 41941363661 B43, T2 41941354379 Foam. No queued jobs found. No cancellations.
