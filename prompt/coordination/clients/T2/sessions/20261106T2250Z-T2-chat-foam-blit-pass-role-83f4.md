# T2 — original Foam pass-specific source/RenderTexture role attribution

- session_id: 20261106T2250Z-T2-chat-foam-blit-pass-role-83f4
- origin: chat; status: active; issue_id: WATER-001
- base_sha: 44938b3eab546ec9744bd721f27bf2e91684b9c0; created_at: 2026-11-06T22:50:31.000Z
- resumed_from_sessions: 20261107T2227Z-T2-chat-blit-texture-role-6c52, 20261106T2218Z-T2-scheduled-blit-pass-provenance-q8f3
- earlier verified originals: https://github.com/alwansan/raf/actions/runs/42303756960 (Blit pass0=1, pass1=1); https://github.com/alwansan/raf/actions/runs/42305522855 (source typed RenderTexture=1, destination typed RenderTexture=1, one unknown each, not correlated).
- scheduled T2 20261106T2218Z-T2-scheduled-blit-pass-provenance-q8f3 completed scope-independent reconciliation; no active T2 scheduled file overlap seen.
- native owner https://github.com/alwansan/raf/actions/runs/42296450023 still in_progress on older immutable source in Unity import; do not cancel or dispatch another.
- experiment_key: T2-original-ZIP2SHA-Foam-two-GraphicsBlit-perpass-source-destination-pairing-v1
- scope: source-only T2-owned scanner + strict validator + synthetic tests; no original Unity shader bytes/IL/private names published, no changes to assets, .meta, GUIDs, Unity workflows, other teams.
- hypothesis: one-to-one pass literal 0/1 and source/destination categories can be attributed *within the exact same authenticated managed Material field-read site*.
- negative controls: fail closed on multiple Blits from one field read, mixed/indirect pass selectors, impossible role partitions and invented pass/source counts.
- next_step: implement, run original SHA pinned source-only GitHub Actions, document counts and unresolved real resource ownership.
