# WATER-001 — Foam pass1 original-producer decision gate
session_id: 20261108T1119Z-T2-scheduled-pass1-original-chain-m6r8
origin: scheduled
baseline_sha: 3cc8f4052ea925fd22781995d4e004d96d4b2b4c
experiment_key: foam-pass1-original-il-producer-destination-chain-sha-authenticated-no-raw-il
status: BLOCKED_ON_ORIGINAL_PRODUCER_TRACE (not a rendering failure diagnosis)

## Evidence reviewed
- Owner 2026-11-05 device report: artifact run 42058825739 enters/saves/re-enters world; 220911-559 reports 23,884 water pass and 3,850 FFT kernel errors. Package publication failed. Neither outcome proves Foam pixel correctness.
- Source-only CI 42454485052: PASS for synthetic report validation; does not establish original IL producer identity.
- scripts/t2_foam_pass_crosscheck.py reconciles independent aggregate classifications; it does not expose texture instance identity or write/read chain.
- scripts/t2_pass1_stack_provenance.py explicitly accepts a *synthetic* bounded instruction sequence, and rejects call/callvirt, ldfld, branches and aliasing. It cannot consume original Mono.Cecil instruction bodies and cannot prove the two Blit operands.
- Current original report schema allows source/destination = unknown. Matching unknown values in two summaries is not a proof of resource binding.

## Decisive next experiment (private original input, no raw IL publication)
1. Pin original ZIP2 source digest and managed assembly digest, and tool version; read only private original assembly. Reject digest mismatch.
2. Find exactly the two typed Graphics.Blit(source, destination, material, pass) callsites for Foam, with pass literal 0 and 1. Reject if cardinality or signature differs.
3. At each callsite, walk *actual* Mono.Cecil evaluation-stack producers backwards with explicit stack effects, following ldloc/stloc, ldfld/stfld and call return values across blocks. Reject unsupported branch merge, unknown alias, unknown receiver, ambiguous producer.
4. Emit ONLY a sanitized per-pass result with typed source/destination role, producer class (field/local/call/unknown), stable non-reversible category, confidence=proved/unknown, assembly authentication boolean, and aggregate counts. Do not emit original names, IDs, instruction offsets, hashes of short private strings, IL or raw asset bytes.
5. Independently compare the resulting categories with existing crosscheck aggregates. A pair of matching `unknown` roles remains BLOCKED, never promoted to authentic binding.
6. Before ShaderLab integration require independently authenticated pass order, CB0 member layout/offsets, textures/samplers, render target formats, blend/ZTest/ZWrite/cull, material Shader.Find/constructor lineage and Unity material-to-shader binding. Then Unity compilation and phone pixel verification are separate gates.

## Current result and limits
No original IL def-use trace executed this cycle; no original private assets fetched. This is a bounded negative finding about *current verifier capability*, not a claim that original source lacks a producer. No shader, .meta, GUID, .rgd, Settings, audio or T3 work changed. Do not request redundant native build.