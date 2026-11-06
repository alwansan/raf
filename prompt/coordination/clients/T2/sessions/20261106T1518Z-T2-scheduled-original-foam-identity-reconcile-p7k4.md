# T2 scheduled — original Foam identity reconciliation

- session_id: `20261106T1518Z-T2-scheduled-original-foam-identity-reconcile-p7k4`
- origin: `scheduled`
- base_sha: `71212a9a6f8c710b8a5064f5a3b48f0f190f1326`
- work_registration_commit: `bb73997dacc9c9d87bc1fbe8f8d5b17310b4688c`
- resumed_from_sessions: `20261106T1423Z-T2-scheduled-cecil-diagnostics-f6c1`, `20261106T1340Z-T2-chat-shader-stfld-source-a84d`
- status: `completed_evidence_reconciliation`

## Owner and current baseline

Read `docs/DEVICE_FEEDBACK_42058825739_AR.md` before priority selection, plus AGENTS, owner requirements, STATUS and T_TEAM operating instructions. Owner phone artifact 42058825739 demonstrated world entry/save/reopen, not water recovery. Original CL logs report 23884/39132 water-pass and 3850/6026 FFT-kernel errors in two different sessions. Keep attribution bounded to that phone artifact and logs. T3 owns independent fire/candle/smoke material investigation; T4 physical mouse; T5 Resolution. No touch layout changes.

## Verified supersession and negative original-source finding

The previous scheduled `blocked_compiler` checkpoint refers to historical CI [42224754004](https://github.com/alwansan/raf/actions/runs/42224754004), which **failed** on source `8094f937da92aa5357604f7dc3a2f3f57a1195e2` at Cecil compilation. The later T2 chat work is not blocked by that failure: [42229056366](https://github.com/alwansan/raf/actions/runs/42229056366) is **completed SUCCESS** on `50c7616ff5099f82d23279f7a0ec8c5ba5e598ba` (verified 2026-11-06 15:18 UTC). Its source-free controls and authenticated ZIP2 original managed/shader checks support a precise **negative**: the actual `Shader.Find` request used to populate the Shader field in the traced managed Material path **does not exactly match** the original serialized Foam Shader `m_Name`. The detailed result and privacy boundaries were already documented by the chat session `20261106T1340Z-T2-chat-shader-stfld-source-a84d` and its evidence memo. This run did not repeat private source acquisition or CI.

Therefore the confirmed source CB0 member-name-to-`Material.SetVector` path cannot be promoted to a *Foam-specific* material/upload proof. The same uniform name may be shared by another Shader. Neither the 11/11 older source-free checks nor the successful newer Cecil scan establish runtime Foam Material identity. The newer CI [42229565911](https://github.com/alwansan/raf/actions/runs/42229565911) is a successful evidence-index refresh, not a Unity render test. No new shader or game patch was justified.

## Independent decision and next action

Rejected action: fixing the obsolete CS0136/CS1929 compiler error on old source or re-running equivalent original ZIP2 experiment. This would collide with newer successful T2 chat work and consume CI without answering the remaining identity question.

Next distinct authenticated question: inspect original Foam Material shader references by PathID/GUID and original asset graph, privately compare against original Shader objects; only then trace actual Foam material CB0 value upload and verify CB member offsets, sampler mapping and ShaderLab binding. Keep names/digests/private IL and proprietary assets out of public reports. Coordinate with T3's Material/FX ownership before touching any shared asset parser. WATER-001 OPEN, NOT_READY 0/3; no new Unity/Android phone proof. No Actions launched, cancelled, or duplicated; no game, .meta, GUID, .rgd, Settings, FMOD, mouse, Resolution or touch files changed.

- branch HEAD before work: `71212a9a6f8c710b8a5064f5a3b48f0f190f1326`; after work registration: `bb73997dacc9c9d87bc1fbe8f8d5b17310b4688c`.
- work: `prompt/coordination/work/WATER-001/T2-20261106T1518Z-T2-scheduled-original-foam-identity-reconcile-p7k4.json`.
