# T2 — source-original four owner Material Shader external graph

- session_id: `20261106T1544Z-T2-chat-four-original-owners-pptr-6a71`
- origin: `chat`, status: `active`
- reservation base_sha: `40564c35f138061b7d28f23bd867f4e066882491`
- reservation commit: `0b6de39b2758f3b172383ac861f7068323f4276e` ([work](../../../work/WATER-001/T2-20261106T1544Z-T2-chat-four-original-owners-pptr-6a71.json)).
- resumed_from_sessions: `20261106T1520Z-T2-chat-foam-owner-shader-material-links-5e84` and latest scheduled `20261106T1518Z-T2-scheduled-original-foam-identity-reconcile-p7k4`.
- authentic previous [CI42243327311](https://github.com/alwansan/raf/actions/runs/42243327311) success: original sharedassets0 owner contains 58 Shader and 351 Material, zero local Material Shader PPtr `fileID=0,pathID=2420`, seven external pointer refs unresolved, and zero other owner Shader names matching a previously traced Shader.Find request. Only a one-owner result, NOT whole-game evidence.
- experiment_key: `original-ZIP2-15964-4-SHA-pinned-owner-MaterialShader-PPtr-external-file-identity-pathID2420-graph-v1`.
- Plan: stage only four already-pinned original owners via `scripts/w1_stage_zip2_owners.py` on independent CI. Extract Unity serialized external FileIdentifier table and Material.m_Shader PPtr; check `fileID-1` index and distinguish verified exact local object, external reference to Foam original owner by basename, and unsupported/ambiguous external pointers. Keep the seven external references' file-paths, GUIDs and private material names out of logs and code.
- No queued/in-progress branch Actions at reservation, no other T2 task on same new files; T1 FFT and T5 Integration past runs are separate. No game assets or native Unity/Adreno build touched.
- Required result: synthetic negative controls + original verified SHA + count-only output; if external table gives filename but not authenticated GUID target, do NOT elevate to actual Shader identity. WATER-001 stays OPEN.
- status at registration: scope reserved; no experiment result claimed.
