# T3 — 20261110T1328Z-T3-scheduled-source-byte-verify-r6n4
origin=scheduled
issue_id=RENDER-002
resumed_from_session=20261110T1226Z-T3-scheduled-ci-pair-identity-v2k7
base_sha=cda2904d6095a6bf822ab435f5ae66e4d5f42f6f
work=prompt/coordination/clients/T3/work/20261110T1328Z-T3-scheduled-source-byte-verify-r6n4.md

## Evidence
Owner feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: world/save/reentry confirmed on artifact 42058825739; white raft/hand, square smoke, lighting unresolved. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. T4 handles mouse; T5 handles resolution. Latest reviewed Actions includes successful T3 regression run 42799750403 on ef457271, predating identity tests e1bfd775. No native build dispatched.

## Actual source changes
Prior identity gate only checked the *format* of source_sha256. Added optional local SHA256 verification of BOTH private original and exported byte files before rendering comparison, streaming 1MiB chunks; mismatch raises source_digest_mismatch. CLI now accepts --original-source and --exported-source together or neither. When both are supplied, output source_digests_content_verified=true; without them false. Also fixed import compatibility for script and Python module invocation. Synthetic regressions cover verified match, tampered original, tampered export, and explicit format-only fallback. Source commits 2bcc36c313af5856a6c2ad689ec5f1bb86ce2be9, 40224ef2cd1bfebf338810070cae019d9d1e7e74, a4e0b09683017f2ce0ae65140b0faa4755022304.

## Limits
Tests added but not yet run on checked-out repository or CI; no claim of green tests. Byte verification proves the supplied summaries' digests match supplied local files, not that files originate from ZIP2 or are semantically the right material/pass. No original DXBC extraction, material fix, shader restoration, Unity compile or device proof. No raw game assets committed. RENDER-002 OPEN / NOT_READY 0/3.

## Next
Run python -m unittest discover -s tests -p test_t3_render_state_source_bytes.py -v on current branch; inspect result, then compare authenticated original ZIP2/export pair with material/shader/pass lineage. Preserve metadata and coordinate T2/T5 source extraction. No duplicate CI/native build.
