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
