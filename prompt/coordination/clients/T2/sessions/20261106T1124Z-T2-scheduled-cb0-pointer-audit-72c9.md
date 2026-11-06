# T2 scheduled — CB0 pointer SSA fail-closed audit

- session_id: `20261106T1124Z-T2-scheduled-cb0-pointer-audit-72c9`; origin: `scheduled`; base_sha: `5944e6fa217dab94c87441cde2fd56a4439bd796`.
- resumed_from_sessions: `20261106T103459Z-T2-chat-cb0-index-48bd`, `20261106T101538Z-T2-scheduled-uploadtrace-6c8f`.
- Scope registered first: [work](../../../work/WATER-001/T2-20261106T1124Z-T2-scheduled-cb0-pointer-audit-72c9.json) at `bed8e5ca875b685b0f90ac52cf54d15a4f45c7c4`. Chat session `20261106T110527Z-T2-chat-cb0-managed-namelinks-f2e1` works on managed-name evidence, not this parser.
- Owner 2026-11-05 phone report is authoritative: run 42058825739 world entry/save/re-entry from Artifact; delivery publishing failed; WATER-001 and effects remain open. Original CB0 2-pass compiled access evidence CI 42204938466 was SUCCESS, but Unity upload and actual Android water remain unverified.
- Hypothesis: synthetic SPIR-V pointer result ID redefinition could silently overwrite the tracked CB0 pointer provenance in `OpCopyObject`, `OpPhi`, `OpSelect`, and `OpPtrAccessChain`. Original access-chain already rejected duplicate IDs.
- Changed parser `scripts/t2_foam_private_cb0_index_access.py`: strict in-bound nonduplicate SSA pointer result for four tracked operations, fail-closed with `duplicate_or_invalid_private_pointer_id`. Commit [50cda520](https://github.com/alwansan/raf/commit/50cda520b5768bb730fafcca61eb41c10bf18d7d).
- Added five source-free adversarial inputs in `tests/test_t2_foam_private_cb0_index_access.py`, commit [74fe4f77](https://github.com/alwansan/raf/commit/74fe4f77ce9d47f08edc93a191989a6bff04b34e). No private original source/program/name/indices published.
- Validation: tests not yet executed; container GitHub DNS lookup failed, so no local repository checkout. Do not claim PASS. Inspect current Actions before considering one targeted validation, avoid duplicate active jobs. No Unity or device build initiated.
- Next: run this test module and original private Foam compile workflow only if the new parser changes original outcomes or tests show a gap. Confirm real stage SPIR-V still passes; source-only validation cannot establish CB0 host upload or water pixels. WATER-001 OPEN; no .meta/GUID/.rgd/audio/Settings/input changes.

## CI checkpoint
- Existing automatic [run 42209039138](https://github.com/alwansan/raf/actions/runs/42209039138) on test SHA `74fe4f77ce9d47f08edc93a191989a6bff04b34e` was **in_progress** at last read; no manual dispatch, cancellation, or duplicate requested. Scope work is `waiting_ci` at commit `5fd248256d4975bdcfc957e21feceeb9b198c0d4`.
- The run validates source and fixtures only; keep actual original CB0 upload and Android water status unknown.
