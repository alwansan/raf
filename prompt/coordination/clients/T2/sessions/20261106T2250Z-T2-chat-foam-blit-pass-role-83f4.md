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

## Code checkpoint — 2026-11-06T22:52:40.660Z
- Code [dd92034a](https://github.com/alwansan/raf/commit/dd92034aaef9b61ad2170c768142398795eff154) published on only writable branch. Three isolated T2 files changed: Mono.Cecil original scanner, strict source-safe report validator, adversarial Python tests. Both pass-index role partitions must sum exactly and conserve original global role inventory when pass0+pass1 cover all explicit Blit sites.
- Checkpoint: workflow dispatch awaited after code commit; no run result yet. Input still immutable original ZIP2 shader owner + managed DLL with SHA verification, no source artifacts leaked; no Unity game asset/ShaderLab/.meta change, no other T-client file touch.
- Next: inspect exact SHA source-only run; fix any fail-closed synthetic/Cecil guard failures. Native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) independently in progress at last query, do not cancel/duplicate.

## Completed source-original CI and conservative attribution — 2026-11-06T23:00:57.041Z
- GitHub Actions [42308583977](https://github.com/alwansan/raf/actions/runs/42308583977) **SUCCESS** at final [code commit 4e5f4d24](https://github.com/alwansan/raf/commit/4e5f4d24e0049518928b0fe47db8adfa3b853db7): 65/65 strict Python safe-report tests +6/6 name controls + Mono.Cecil synthetic selftest PASS, original SHA-pinned ZIP2 shader-owner 115978112B and managed DLL 3211776B privately authenticated, source safe JSON attested.
- **Per exact Foam Material field-read site:** Pass 0: literal 0, direct typed RenderTexture source=1, direct typed RenderTexture destination=1; Pass 1: literal 1, source producer unknown=1, destination producer unknown=1. All other pass0/pass1 role categories zero. The same-site pairing is NEW and verified; cannot infer runtime resource object identity, allocation, content, CB0 host upload or Adreno pixels.
- Safe artifact `13547696649`, 1429 bytes, SHA256 `e4a31957a9637656dba391582f21a9513d1fc03786723694793731d23233c22f`; original private symbols, IL and shader bytes not emitted.
- Intermediate experiments RED and addressed: [42307890304](https://github.com/alwansan/raf/actions/runs/42307890304) C# positional record missing int; [42308039434](https://github.com/alwansan/raf/actions/runs/42308039434) same-pass repeated-site count missing; [42308240623](https://github.com/alwansan/raf/actions/runs/42308240623) and [42308461322](https://github.com/alwansan/raf/actions/runs/42308461322) synthetic pass-specific UNKNOWN enum mismatch, corrected with explicit negative regression. Final CI PASS; no acceptance gate weakened.
- Technical report: `docs/T2_ORIGINAL_FOAM_BLIT_RENDER_TEXTURE_ROLES_2026-11-07.md`; T1/T5 discussion: `prompt/coordination/discussions/WATER-001/20261106T2300Z-T2-chat-pass0-rt-pass1-unknown-to-T1-T5-83f4.md`.
- Native owner [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) still in_progress importing Unity at last T2 check, older immutable source; T2 did not stop/dispatch native, touch Unity assets/.meta GUIDs, or claim new XAPK. T2 vote unchanged `لا يحتاج`. WATER-001 OPEN, NOT_READY.
- status: completed; next_step: Trace source-original Pass1 indirect Texture/RenderTexture producer under bounded safe IL with no identity leaks; T5 authentic Unity importer/runtime and original CB0 host upload needed before phone pixels. No new native request while 42296450023 runs.
