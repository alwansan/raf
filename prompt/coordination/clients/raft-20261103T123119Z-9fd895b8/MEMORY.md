# A14 — coordinated session

- Username: `raft-20261103T123119Z-9fd895b8`
- Session ID: `A14-20261103T123119Z-71377153`; client_label: `A14`.
- Started: 2026-11-03T12:31:19.959Z UTC; baseline branch HEAD `aae8cc2070126449fa05049a669235a144309101`.
- Branch/write scope: `feature/android-native-port` only. CL and main/zip/Unity-Editor read-only.

## Verified intake

- Original native preview [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) is COMPLETED FAILURE on `c7254f7d22b9803c995edca0d5c373d28cfb9ff9`; reconstruct job `125878883840`, step `Restore exact-name Unity 2021.3.45f2 built-in material and particle programs with original GUIDs` stopped before Unity with zero exported identity matches. Vendor archive reported 198 SHA-verified shader identities; zero matching original export is not proof of an empty/complete export.
- Existing read-only coverage probe examined 107 local files (24 empty, 83 parseable non-vendor, zero vendor), explicitly **not proven** as complete build-run export. No retry or substitution warranted.
- Peer completed work reviewed: A9 lexical ShaderLab header fix; A6 commented include fix; A3 symlink path guard; independent coverage probe. Source fixes do not close RENDER-002/WATER-001/FFT-FORMAT-009.
- At observation: current native preview failed; queued/in_progress Actions queries both returned zero; no newer verified Raft native game APK; last game delivery APK80. Current project readiness NOT_READY/0-of-3 full immutable candidate reviews.

## Session boundary

Owner stated A14-specific task will follow this introductory message. Pending that task, no source, workflow, shader, meta/GUID, LFS, native request, Unity/APK/OBB/XAPK, Release or schedule is changed. Do not duplicate a peer's completed probe. Any later engineering needs re-read of HEAD, Actions and relevant peer scopes and a concrete plan before execution.

## Restore point

Read `prompt/coordination/README.md`, `UNIFIED_PROMPT_AR.md`, `TEMPLATES.md` and current owner instructions; read A14 state and work plan; obtain the exact A14 task, then recheck live HEAD and execute scoped CPU-only work using expected SHA lease and isolated tests. Keep project NOT_READY until all actual prebuild gates and three independent full reviews pass.

## Continuation 2026-11-03T14:59:06.565Z

- Live HEAD `b6a962018e06513d5cf408e646751f161f0e00ca`, native41624581951 unchanged old failure. New A11/A13 source-scope audits and A15 addition rollback are complete; W1 real DXBC/depth pass experiments are distinct. Current active A14 scope is external built-in backup write integrity, not a claim about missing original matches.
- Scoped discussion: `prompt/coordination/discussions/RENDER-002/20261103T145906Z-raft-20261103T123119Z-9fd895b8-backup-scope.md` and plan `prompt/coordination/work/RENDER-002/raft-20261103T123119Z-9fd895b8-backup-integrity.json`.
- Intended red-green: inject late/partial backup write failure, verify no backup residue or original shader/meta mutation; run existing peer checks on green.

## Completed A14 red-green backup I/O subtask — 2026-11-03T15:09:57.595Z

- Red [41659753191](https://github.com/alwansan/raf/actions/runs/41659753191): 2 intentionally failed residual-backup assertions and 2 positive checks passed; original fixture source/.meta unchanged.
- Fix [8dcca858](https://github.com/alwansan/raf/commit/8dcca858d2ae0646d5fb1a48fbdb2ab51a2909dc): immediately remove newly created partial external shader backup when a copy fails; pre-existing backup dirs not modified, no change to identity matching/zero-match strict gate.
- Green [41660203887](https://github.com/alwansan/raf/actions/runs/41660203887) 4/4 SUCCESS; [A3 41660203946](https://github.com/alwansan/raf/actions/runs/41660203946), [A9 41660203931](https://github.com/alwansan/raf/actions/runs/41660203931), [A15 41660204010](https://github.com/alwansan/raf/actions/runs/41660204010), [official vendor 41660204069](https://github.com/alwansan/raf/actions/runs/41660204069) all SUCCESS on exact same fix SHA. Two aggregate A14 artifacts verified.
- Records: `prompt/coordination/work/RENDER-002/raft-20261103T123119Z-9fd895b8-backup-integrity.json`, `prompt/coordination/experiments/raft-20261103T123119Z-9fd895b8/a14-partial-backup-write-redgreen.json`, `docs/A14_BUILTIN_BACKUP_WRITE_RECOVERY_2026-11-03.md`.
- Scoped task COMPLETED, no Unity/APK/LFS/request/release/schedule/CL changes; original full export provenance unresolved. RENDER-002/WATER-001/FFT-FORMAT-009 OPEN, NOT_READY, 0/3 immutable candidate reviews. Do not reuse this completed A14 identity in a concurrent session without checking activity and new session_id.
