# T2 isolated session — 2026-11-05T12:18Z

- Identity: T2; status: paused_identity_conflict (another T2 CI run 42026068605 in_progress at baseline).
- baseline_sha: 312316aacd48ff7fe6576ae40d23ba518e75458d
- resumed_from_session: 20261105T0523Z-T2-stage-scope-isolated (conversation checkpoint; not asserting current shared state).
- taken_over_from: T2 earlier original Foam texture identity; B20 original CB evidence, B45 Blur evidence (historical only).
- Hypothesis: public SHA256 of low-domain original (m_Index,m_SamplerIndex) pairs can disclose private resource indices through enumeration; the source report still emits original_numeric_pair_digest_sha256.
- Source evidence: scripts/t2_foam_texture_identity.py at blob 056fece2512fd323194186a7a773a85f228c3102 includes original_numeric_pair_digest_sha256 in compare_private_names and persists audit rows through main().
- Repro (synthetic only): enumerate 16x16 numeric pairs; SHA256(JSON canonical [[3,2]]) uniquely recovered (3,2) in 256 attempts. This proves the digest is reversible in a small domain, not that original pairs were leaked or guessed.
- Engineering: prepared an independent recursive report sanitizer and three passing unit tests locally; isolated ZIP checkpoint T2_foam_digest_sanitizer_20261105.zip (not committed; no raw source). It strips original_numeric_pair_digest_sha256 and private fields without modifying count fields. Sanitizer is a temporary guard, not a substitute for removing digest at its producer.
- Rejected: bare SHA256 as a confidentiality control; unkeyed salted hash is also unsuitable when salt is public. Prefer removal from public report, or keyed HMAC only in restricted private comparison with no key in logs/artifacts.
- Next testable step: after concurrent T2 work settles, remove digest at source, add regression asserting absence from persisted JSON, run existing T2 tests and original SHA-pinned workflow only if required by new question.
- CI: no new action; T2 run https://github.com/alwansan/raf/actions/runs/42026068605 was in_progress at inspection. No Unity/device claim; WATER-001 OPEN.
- No modifications to game shader, .meta/GUID, audio, Settings, touch, native workflows or shared T2 state/MEMORY.
