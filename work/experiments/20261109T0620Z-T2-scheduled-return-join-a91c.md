# T2 WATER-001 — bounded return-alias investigation
session_id: 20261109T0620Z-T2-scheduled-return-join-a91c
origin: scheduled
baseline_sha: 854d91b3259e5f0e60389cbc5bee641cc5338fb3
issue: WATER-001 OPEN / NOT_READY
experiment_key: T2-FOAM-RETURN-ALIAS-20261109-0620
scope: android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs (read-only diagnosis in this cycle); this independent work file; clients/T2/sessions/20261109T0620Z-T2-scheduled-return-join-a91c.md
shared_resource: original ZIP2 authenticated CIL only if future experiment runs; no Unity/CI dispatched.
taken_over_from: work/experiments/20261109T0212Z-T2-chat-return-value-flow-n7x3.md; clients/T2/sessions/20261109T0520Z-T2-scheduled-ci-gate-confirm-6f2c.md

## Evidence and falsifiable finding
Owner phone run 42058825739 established world entry/save/re-entry, not water correctness. The original Foam CIL source-only CI42549568993 returned value_mixed_or_joined. Direct source inspection of current Program.cs shows ReachableReturnValueFlow joins two incoming stack/local category values with a == b ? a : mixed at each CFG node, and emits value_mixed_or_joined for differing return categories. This is an intentionally conservative category lattice, not proof of two different Texture instances. The current abstract state lacks receiver identity, argument identity, and field-token/instance pairing. Consequently even a uniform return category would not establish pass0 RenderTexture identity with pass1 Texture. Do not change ShaderLab on this evidence.

## Concrete next implementation acceptance
Introduce bounded path-sensitive return provenance preserving per-path origin tokens and receiver alias tokens, with stable synthetic fixture IDs and at most 128 IL instructions, 32 locals, 2048 state visits, 16 distinct path states per PC. Distinguish identical field token on same receiver from field token on different receivers; track call-return receiver and argument mapping across resolved nonvirtual methods; fail closed on virtual dispatch, loops exceeding budget, exception handlers, unsupported stack behavior, unknown call side effects and merges. Assert that distinct receivers do NOT unify even if field type and metadata token match. Only emit safe category labels and counts; no raw private identifiers. Confirm original ZIP2 source SHA and run isolated CI once after overlap check. Never equate category-level success to runtime object equality or device water pixels.

## Result
Verified source-level limitation and specified a discriminating regression test, without modifying the scanner or running a duplicate job. This is not an implemented fix or original-source proof. Next cycle should implement the receiver-distinction fixture first, then interpreter and private original scan; if T2 chat already owns Program.cs, choose separate fixture path and avoid concurrent edits.
