# T2 — Original Foam one-hop nested Texture-return field provenance

- session_id: `20261109T2020Z-T2-chat-foam-onehop-return-r8c5`
- origin: `chat`
- base_sha: `746353c0f54f559154ec4f52dcba4229f49ab174`
- scope commitment BEFORE source edits: `prompt/coordination/work/WATER-001/20261109T2020Z-T2-chat-foam-onehop-return-r8c5.json`, commit `0c7d349845d2b7c1678acd2cb0e7e86bbf929294`
- resumed_from_sessions: `20261109T2002Z-T2-chat-foam-declared-field-flow-c9n4`, `20261109T1946Z-T2-chat-foam-equality-predicate-m4q9`
- issue_id: WATER-001 OPEN; full game NOT_READY 0/3
- experiment_key: `original-Foam-pass1-Cecil-one-hop-nested-texture-return-field-token-safe-20261109-v1`
- resource_key: `T2-original-FoamBlitOriginalProducers-Cecil-source-only`
- owned files: `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs`, `scripts/t2_foam_original_blit_report.py`, `tests/test_t2_foam_original_blit_report.py`, this session, own work/experiment/event, own safe report.
- Other scopes: T1 FFT, T3 shader/fire, T4 mouse, T5 Android shared mini / APK untouched; no Unity, private original IL/raw shader published; no XAPK/mini build triggered.

## Last verified original baseline

[CI42690309016](https://github.com/alwansan/raf/actions/runs/42690309016) SUCCESS, 19/19 Python, Cecil synthetic, SHA-pinned original ZIP2. Pass0 RenderTexture typed destination field but pass1 Texture-returning callee direct field relation `field_no_match_with_null`; source pass1 abstract return `value_mixed_with_explicit_null_literal`. Only absence of a *direct* same declared field return; not absence of indirect alias, same receiver or same heap RenderTexture.

## New one-hop original hypothesis and changes

Commit `99c1f1c40b978c92e67f558a1ef89dcd983c84b9` makes a separately labeled bounded *one-hop* nested Texture-return analysis of the pass1 managed original callee's own call result. Exactly one statically resolvable in-module nonvirtual or safely final callee may be inspected; nested cycles, EH/unsupported CIL, non-original modules and dynamic virtual dispatch are opaque. Every returned producer is tracked through prior CFG/local/stack joins rather than naive call presence. Positive evidence is at most matching **declared field token**, never actual instance/receiver/frame or pixel parity. Distinct public-safe labels are separately validated in strict Python report schema; tests include matching/different private synthetic field, recursive helper, and virtual method that must not count as positive.

Initial [CI42692810846](https://github.com/alwansan/raf/actions/runs/42692810846), source `99c1f1c40`, FAILED at Python regression: four historic direct-field positive fixtures still had the new one-hop field set to `field_pass0_destination_untraced`, which correctly violates the strict fail-closed consistency rule when the destination is traced. Actual original C# test and original data were *not run* in this failed job. Changed only the own test fixture at commit `0408e76db8950935b9eb02a7c11645f7442e8250` to mirror the direct positive relation into the one-hop relation, without weakening schema.

Current SHA-bound source-only [CI42692872122](https://github.com/alwansan/raf/actions/runs/42692872122) was **in_progress** on first observation; no manual rerun, no other team workflow cancellation.

## Handoff

Read finished CI's complete phases: 21 Python tests, `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`, original DLL=3211776 and Shader owner=115978112 SHA pin, purge, strict JSON validator and `T2_FOAM_CROSSPASS_ONEHOP_FIELD_RETURN_RELATION`. Do not call validated until source-original CI succeeds. If successful, compare onehop label to prior direct `field_no_match_with_null` (a positive only means declared token lineage through one nested callee and may have null/other branches). Document independent safe result, mark scope complete and send next-step receiver/heap alias gap to schedule. All game acceptance remains open; no device photo or new APK needed for source-only work.

## Independent synthetic-Cecil issue and corrected continuation

[CI42692872122](https://github.com/alwansan/raf/actions/runs/42692872122) from fixture correction `0408e76d`: all **21/21** strict Python tests passed but C# `--selftest` reported `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_BLOCKED`, before original source authentication. It is **not** an original Foam result.

Next commit `5fc56b532d41fb207cd9d703bcc100f0ac78c23d` handles in-memory synthetic `Mono.Cecil.MethodDefinition` directly (rather than relying on an original-assembly MethodReference resolver) and adds a tightly finite failure marker for only five new source-free synthetic cases. It never prints arbitrary exception messages, actual field names or tokens. Original managed references still undergo resolver and module-identity checks.

Automatic [CI42693196369](https://github.com/alwansan/raf/actions/runs/42693196369) source `5fc56b53` was observed **IN_PROGRESS** with Cecil selftest pending; platform adapter [CI42693196347](https://github.com/alwansan/raf/actions/runs/42693196347) separately auto-triggered. Verify final logs before drawing conclusions, then only if original succeeded archive safe original one-hop label. Never claim original data tested from a failing synthetic-only gate.
