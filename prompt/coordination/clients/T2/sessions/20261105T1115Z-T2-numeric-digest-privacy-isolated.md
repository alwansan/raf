# T2 isolated security/ABI checkpoint — 2026-11-05T11:15Z

session_id: 20261105T1115Z-T2-numeric-digest-privacy-isolated
resumed_from_session: 20261105T0023Z-T2-foam-texture-identity (state.json; later independent sessions recorded in prior history)
status: paused_identity_conflict
baseline_sha: cb773b1bbdf567e7de6ca0e8f08a1fe64cc8dfc2
taken_over_from: B20/B25 Foam numeric interface, T2 original texture identity tests; do not attribute predecessors' work to this session.

## Hypothesis and decisive reproducible local test
The publicly reported SHA256 of sorted low-range (m_Index,m_SamplerIndex) pairs in scripts/t2_foam_texture_identity.py is not a privacy-preserving commitment. Since each integer is bounded by 65535, a small number of pairs can be recovered by enumerating candidates. Synthetic proof with a single pair (3,2): SHA256(json.dumps([(3,2)],separators=(',',':')).encode()) = 11b8fdac1a63a8bac69ae8bb2e7d45da5233eee87403861f14c17e9e6d9c0f6c. Enumerating both indices in range(16) recovers exactly (3,2). No actual game indices used or exposed.

## Decision
Reject the hypothesis that a plain SHA256 digest guarantees numeric index confidentiality. Preserve only count/distinct and non-reversible source asset SHA; do not publish pair digest in public reports or logs. If cross-run equality is necessary, compute private keyed HMAC using secret key unavailable to public artifacts, or keep comparison wholly in private scratch. Existing digest may already have leaked limited original numeric data; avoid copying it further. This is a local synthetic proof, not source/Unity/device evidence.

## Collision/coordination
A distinct T2-authored HEAD commit cb773b1 (11:15:44Z) was observed concurrently, and state.json is stale relative to prior T2 sessions. Do not overwrite shared state/MEMORY or edit T2 code while its other session may be active. No Actions cancelled, no Unity launched, no changes to game shaders/audio/Settings/touch. Next step: owner T2 active session should remove digest from public safe-report schema, add adversarial privacy regression, then verify original audit and publication path with SHA lease. WATER-001 OPEN / NOT_READY.
