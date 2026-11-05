# T4 chat — original SaveAndLoad zero-argument RGD producer return sites

- session_id: 20261105T1713Z-T4-chat-original-rgd-return-sites-j7q4
- origin: chat
- status: completed
- base_sha: 456f48286a4d62a2a7b43ee35d83940f026e4bf9
- resumed_from_sessions: 20261105T1645Z-T4-chat-original-rgd-init-context-q6m2; 20261105T1640Z-T4-scheduled-r8k2
- work: prompt/coordination/work/LOCAL-005/T4-20261105T1713Z-T4-chat-original-rgd-return-sites-j7q4-original-rgd-return-sites.json
- experiment_key: T4-authentic-zip2-sha0a6f-SaveAndLoad-zeroarg-derived-RGD-factory-return-site-and-direct-constructor-census-v1
- resource_key: none (pinned original source, read-only CPU)

## Verified baseline
[CI42068520588](https://github.com/alwansan/raf/actions/runs/42068520588) SUCCESS32/32: exact owner-provided original ZIP2 DLL size 3,211,776B SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. SaveWorld's single derived-RGD local store is fed from zero-arg instance SaveAndLoad method with original compiled body; SaveUser's derived-RGD field has three writer sites. No original game RGD world save or device proof. T5 native [run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) remains IN_PROGRESS in Unity Editor import. Latest real game release is APK86, not newer LogRaft tags.

## Independent scope
Investigate genuine compiled method's lexical return-site count, immediate returned-value categories, class construction and branch/throw presence, without calling game methods or releasing private source. T4 scheduled 1640Z source-free JSONL overflow session continues separately and owns different files; no overlap. No T5 Unity job cancelled/restarted, no game source/assets/serializer/.meta/GUID touched. The returned value might be null or uninitialized even when no direct literal-null ret is present; static IL not path-sensitive. LOCAL-005 OPEN NOT_READY 0/3.

## Next
Implement minimal additive original IL metadata category report; test synthetic non-claim controls; verify CI with exact immutable source; report to T5.
## Verified close — 2026-11-05 17:18 UTC

- [FINAL CI42072718216](https://github.com/alwansan/raf/actions/runs/42072718216): COMPLETED SUCCESS, tested source b1203fb30fa91eab56ec0507e720574d7aa75ecf, 50/50 source-free synthetic safety controls, original SHA-locked DLL Mono.Cecil inspection, changed-source negative SHA rejected.
- Immutable source: owner ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385, original Assembly-CSharp.dll exactly 3,211,776B SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e. No private code, IL, field/method names, bytecode, RGD file or game payload published.
- Source-only new original SaveAndLoad world factory method body: one lexical return preceded directly by a derived-RGD-typed local load; two derived-RGD local slots; one direct derived-RGD construction site; one direct call returning derived RGD; 34 conditional branch instructions; 10 ldnull sites; no explicit throw/rethrow. These counts are not path-sensitive. They neither prove nor disprove non-null returned RGD or actual game Save/world durability.
- Code updated: android-port/Experiments/T4/OriginalRgdInitContext/Program.cs at a5dec4b734725969ece9ade9cc589bcb71d60883; strict validator scripts/t4_validate_original_rgd_init_context.py at 3cbee8c415d9ad289acc90ff422e70b439d8e7a7; tests/test_t4_validate_original_rgd_init_context.py at 5772262d51b36dec657a5520ca3407270215c025 then b1203fb30fa91eab56ec0507e720574d7aa75ecf. 18 additional safety controls increased 32 to 50; isolated source-only workflow reused without native Unity runs.
- Transitional CI42072414751, CI42072490701 and CI42072568029 failed because staged source/report/test mismatch. Last failed test was legacy unresolved-external factory acceptable under prior scope-only report; now exact original compiled body is mandatory and fixture correctly changed to fail closed. Not an original game crash or serializer failure.
- Complete report docs/T4_ORIGINAL_RGD_RETURN_SITES_2026-11-05.md, event prompt/coordination/B_TEAM/events/T4/20261105T1717Z-T4-original-RGD-factory-return-50pass.json, T5 handoff prompt/coordination/discussions/LOCAL-005/20261105T1717Z-T4-RGD-factory-return-shape-to-T5.md. Independent work record completed.
- T4 scheduled 1640Z JSONL overflow evidence work and owner files untouched. T5 native run42058825739 from e9c358eda01785b65e4eb14f18723da426635628 still in_progress Unity Editor import on latest verified check; no new signed APK/OBB/XAPK or owner phone same-world acceptance. No Unity/native job dispatch or cancellation by T4.
- Remaining: investigate how exact factory return local was assigned under 34 branches, consume T5 native delivery when actually produced, and verify offline playable world, genuine RGD save, full exit and same-world reopen. LOCAL-005 OPEN, NOT_READY 0/3. Original serializer/schema/.meta/GUID, local host, B50 Steam guards, audio, Settings preserved, touch deferred.
