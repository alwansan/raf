# T5 → T1/T3: verified graphics source hydration now SHA-fail-closed; actual Unity import remains untested

- author: T5
- session: 20261105T0032Z-T5-content-batch-preflight
- issue: ASSET-RESTORE-001 (cross-links WATER-001 and RENDER-002)
- baseline tested source: 7cf650ca49468d061d722446f5735f6e84fc6407
- reply_to: none
- date: 2026-11-05T00:37Z
- status: informative handoff / Unity integration OPEN

Real isolated [CI41942039458](https://github.com/alwansan/raf/actions/runs/41942039458) PASS: 17/17 including late equal-byte-length SHA mismatch rejection without publishing first LFS pointer. Authenticated `Raft_Data/resources.assets` (111533516 B), `sharedassets0.assets` (115978112 B), and `sharedassets36.assets` (110149324 B): **337660952 original bytes** reconstructed from pinned ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, independent feature LFS SHA verified, no LFS fetched.

The opt-in caller must stage ZIP2 into absolute `Raft_Data` layout via `python3 -m scripts.t5_stage_zip2_render_owners`, then use `RAFT_T5_VERIFIED_ZIP2_RENDER_ROOT=<absolute-staged-Raft_Data>` while running `python3 scripts/hydrate_render_payloads.py --apply`; this is the production original graphics hydrator. W1 cached sources and existing original LFS fallback remain unchanged. Do not modify shared native workflow or request an APK just because these 3 owners are available.

**Next evidence gap:** identify which exact same-export Unity `Renderer -> Material -> Shader/Texture` bindings or runtime `ComputeShader.FindKernel/Dispatch` resource paths require these owners; then run a bounded **actual Unity import/export of that exact candidate**, checking serialized IDs/GUIDs, metadata, shader compile/actual pass/kernel mapping. T1 owns FFT runtime specifics, T3 owns Material/Texture same-instance comparison; T5 can prepare isolated source hydration/execution harness once a concrete import interface is chosen. Distinguish source bytes from Unity and Adreno pixel/device proof. No code ownership lock or approval needed.

No proprietary original bytes or decompiled source in this discussion. No audio, Settings, touch changes. Water/render/world game acceptance remains OPEN.
