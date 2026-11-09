# T2 — SHA-original Foam pass1 return-value flow across CIL branches

**2026-11-09** · **Issue:** `WATER-001` OPEN · **Worker:** T2 · **Origin:** chat. This report is a bounded original-managed-IL diagnostic, **not** Unity/Android water rendering acceptance.

## Previous baseline

At [CI42548419872](https://github.com/alwansan/raf/actions/runs/42548419872), the actual SHA-original Foam pass1 Texture-returning managed callee was classified as `cfg_mixed_syntactic_return_predecessors`. That predecessor classification did **not** track values carried through locals, stack or CFG joins. Original source material metadata already proved a pass0 `RenderTexture typed_field` and pass1 `Texture typed_call_result` through bounded source CIL, but neither runtime object identity nor pass0-destination-to-pass1-source alias.

## New experiment and safeguards

The T2-only file `android-port/Experiments/T2/FoamBlitOriginalProducers/Program.cs` now contains a bounded forward abstract evaluation of CIL stack and local **source categories** across direct/conditional/switch branches, typed field loads, call/newobj return signatures, stores, copy/pop and path joins. Its state lattice merges conflicting origins into `mixed`, it rejects unsupported control-flow/opcode semantics, exceptional regions, malformed jumps, stack underflow or unequal stack-height joins, and caps instruction count, local slots, stack depth and iteration budget. Non-final virtual dispatch remains untraced; nested calls and receiver identity are deliberately opaque.

The classifier **never** promotes a static field category into a unique field token, heap object, matching RenderTexture, non-null texture, correct shader binding or GPU pixel parity. Distinct fields of identical static categories are indistinguishable in this intentionally restricted model.

Synthetic Cecil selftests exercise same-category local propagation over two branches, contradictory return values, a shared-return stack join, detached jumps, exceptional regions and nested-call outputs that must remain untraced. No source-original method/field names, raw instructions, material, shader bytecode or original assets are emitted from the private runner. The existing strict safe JSON flags continue to require `original_crosspass_destination_to_source_identity_proven=false`.

## Authenticated CI result

- **Workflow:** [CI42549568993](https://github.com/alwansan/raf/actions/runs/42549568993), source commit `4c8af56a580264df92a98375a7fd30ae87a10a21`, job `128941879761`; **COMPLETED SUCCESS**.
- Regression: **17/17** Python tests PASS, Mono.Cecil synthetic selftest PASS, original source authentication/purge and bounded artifact upload PASS.
- Original data: exact ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, SHA-verified original 3,211,776-byte managed assembly and 115,978,112-byte original Shader owner. No LFS smudge, no raw private artifact.
- Actual original safe stdout:

```text
T2_FOAM_PASS0_BACKTRACE RenderTexture typed_field static_type_only_no_instance_proof steps=6 void_calls=0
T2_FOAM_PASS1_BACKTRACE Texture typed_call_result static_type_only_no_instance_proof steps=21 void_calls=1
T2_FOAM_PASS1_CALLEE_BODY_FAMILY original_method_branch_flow
T2_FOAM_PASS1_CALLEE_CFG_TOPOLOGY cfg_mixed_syntactic_return_predecessors
T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_or_joined
```

**Interpretation:** The more precise source-original forward abstract interpretation still does not reduce all reachable pass1 return paths to one public abstract producer category. `mixed_or_joined` can mean distinct abstract categories across returns **or** incompatible branch values at a return join. It does **not** prove that two distinct textures necessarily occur at runtime or that any original path fails.

## Open engineering questions

1. Resolve the exact **original runtime** receiver, field and allocation/alias lineage within the private runner: static categories are not heap identities; exceptions/virtual dynamics must stay unknown.
2. Establish pass0 destination and pass1 source refer to the same actual texture object on the relevant frame and lifecycle, not only matching types.
3. Verify original Foam CB0 uploads, sampler/texture relationships and ShaderLab pass wiring.
4. Compile original integrated Unity assets/shaders, compare actual pixels on Adreno730 and close WATER-001 only after device evidence.

The real owner phone Mini r2 [CL/test shared session](https://github.com/alwansan/CL/tree/main/test/shared-20261108-230157-466487336) passed T2 synthetic GLES FBO controls; this does not confirm original Raft water. No new Mini APK (T2 NO_BUILD) or full Raft XAPK requested. Audio, settings, mouse, original assets and other T clients' source were untouched.

## تحديث لاحق موثّق — 9 نوفمبر 2026 (19:18 UTC)، T2

آخر دليل مُثبت بعد نتيجة `value_mixed_or_joined` التاريخية: [CI42680030121](https://github.com/alwansan/raf/actions/runs/42680030121) أعاد تصنيف مصدر تمريرة Foam الثانية إلى `value_mixed_with_explicit_null_literal` بعدما صارت أداة CIL تحتفظ بفئات المنتج على الفروع وعند نقاط الجمع. تشير الفئة إلى ظهور `ldnull` في مسار إرجاع *محافظ*، ولا تثبت تنفيذ المسار على الهاتف.

نفّذت تجربة مستقلة تُميز الشروط العددية الثابتة `ldc.i4=0` و`ldc.i4!=0` عند `brtrue`/`brfalse`؛ المسار المستحيل تحت الشرط الثابت يُستبعد بينما تظل جميع فروع الوسائط والاستدعاءات والشروط المجهولة محتملة. أنشأت selftests لثابت 0/غير صفر، وللشرط المجهول، ولـ shared-return phi. التعديل [`cc4e2519`](https://github.com/alwansan/raf/commit/cc4e2519c35506c4a4a134b2428ee65c11269928) واجتاز [CI42681948189](https://github.com/alwansan/raf/actions/runs/42681948189) **SUCCESS**، بما فيه 17 اختبار Python وMono.Cecil synthetic selftest والمصدر الأصلي SHA-pinned (DLL بحجم 3,211,776 بايت وShader owner بحجم 115,978,112 بايت) وتنظيف المصدر الخاص.

**النتيجة الأصلية بقيت `value_mixed_with_explicit_null_literal`.** ولذلك فإن الفئة السابقة لا تختفي بإزالة الفروع التي يستحيل الوصول إليها بمجرد شرط CIL عددي ثابت؛ لكن تحليلًا محافظًا لمُدخل مجهول قد يشمل مسارًا لا يحدث في حالة تشغيل معينة. كذلك `ldnull` قد يكون إرجاعًا مقصودًا أو اختياريًا في تصميم اللعبة، وليس خطأً بمفرده. لا تستنتج أن `null` هو سبب الخطأ المائي أو أن مصدر pass1 يساوي وجهة pass0. لا توجد شهادة على مخرجات ShaderLab/CB0 أو بكسلات الماء على Android. `WATER-001` ما زال **OPEN**.

نقطة الاستكمال المعلّمة: `prompt/coordination/clients/T2/sessions/20261109T1916Z-T2-chat-foam-constant-branch-p8v6.md`.

## Original follow-up — 2026-11-09 19:49 UTC: exact equality control

Registered isolated T2 work before source edits at `prompt/coordination/work/WATER-001/20261109T1946Z-T2-chat-foam-equality-predicate-m4q9.json`. Commit [5b9adfbc](https://github.com/alwansan/raf/commit/5b9adfbc82160f1e8bc6a00713577e7fb3549ed4) extends the bounded Mono.Cecil predicate evaluator, with sound *known-constant-only* folding for `ceq`, `beq[.s]`, and `bne.un[.s]`. Exact zero/zero and null/null are equal; a known integer zero and a known nonzero are unequal. Crucial negative control: two abstract `nonzero` families (e.g. 1 vs 2) are **not** treated as equal. Joined/unrecognized values still explore both successors.

The original-data workflow [42686782993](https://github.com/alwansan/raf/actions/runs/42686782993) on exact source `5b9adfbc82160f1e8bc6a00713577e7fb3549ed4` completed **SUCCESS**; 17/17 source-free privacy Python tests, C# Mono.Cecil synthetic selftests, source owner/dll authentication, private scratch purge and safe publishing all passed. Log evidence: `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`, `T2_FOAM_BLIT_SOURCE_SHA_PASS original_dll_bytes=3211776 owner_bytes=115978112 lfs=false`, `T2_CECIL_ORIGINAL_BLIT_SAFE_RESULT_READY private_content_not_printed=true`.

Authentic original classification remains unchanged after this independently guarded comparison semantics:

```text
T2_FOAM_PASS0_BACKTRACE RenderTexture typed_field static_type_only_no_instance_proof steps=6 void_calls=0
T2_FOAM_PASS1_BACKTRACE Texture typed_call_result static_type_only_no_instance_proof steps=21 void_calls=1
T2_FOAM_PASS0_CALLEE_RETURN_VALUE_FLOW not_call_return_source
T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_with_explicit_null_literal
```

Separately triggered Android platform adapter [42686783004](https://github.com/alwansan/raf/actions/runs/42686783004) completed **SUCCESS**; it does not render authentic Foam pixels. A safe original-CIL return-family classification is not proof of actual Android `null`, same-frame source/destination heap identity, Foam ShaderLab installation, proper CB0 upload, or water rendering. `WATER-001` stays **OPEN / NOT_READY 0/3**. Next genuinely different original-source question: prove or reject pass0-destination ↔ pass1-source runtime object continuity under matched receiver, state and frame; be explicit when the available static evidence cannot decide. No full XAPK or Mini request.

## SHA-original crosspass declared field audit — 2026-11-09 20:13 UTC

T2 registered the separate `20261109T2002Z-T2-chat-foam-declared-field-flow-c9n4` work before implementation. C# Mono.Cecil now traces the authenticated original Foam Blit **pass0 destination** stack slot (depth2) independently of the **pass1 source** (depth3), then compares the pass0 destination's original *declared field token* privately with the possible field-origin return values of the original pass1 managed callee, across bounded CIL stack/local CFG joins. The real field token is never logged or published. A field equality would still not prove same receiver, frame, intervening writes, RenderTexture heap instance or Android pixels.

Initial source commit `c780271d7689e2b0ce8327183b590aef864db3b0` produced [CI42689721185](https://github.com/alwansan/raf/actions/runs/42689721185) **FAILURE** at the strict report-schema step: the additional safe keys were not yet allowed, so that run is not treated as verified. Follow-up atomic source commit [6f09eddc](https://github.com/alwansan/raf/commit/6f09eddcf788050035a767d21999c75a6ebebdc1) added Python schema safety and source-free synthetic C# tests for exact same/different original declared field token, direct null return, guarded field/null returns, and reading/discarding a field without returning it. Also fixed false comparison of separate Cecil fixture fields whose metadata RID is 0.

Verified [CI42690309016](https://github.com/alwansan/raf/actions/runs/42690309016) **COMPLETED SUCCESS** on `6f09eddc`: **19/19** Python tests, `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`, original ZIP2 assembly 3,211,776 bytes and shader owner 115,978,112 bytes authenticated, private scratch purge and safe artifact publication. Genuine original output:

```text
T2_FOAM_PASS0_BACKTRACE RenderTexture typed_field static_type_only_no_instance_proof steps=6 void_calls=0
T2_FOAM_PASS1_BACKTRACE Texture typed_call_result static_type_only_no_instance_proof steps=21 void_calls=1
T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_with_explicit_null_literal
T2_FOAM_CROSSPASS_DECLARED_FIELD_RETURN_RELATION field_no_match_with_null
```

**Negative structural result:** within the analyzed original pass1 callee return paths, a value directly loaded from the exact same DECLARED field token as the pass0 destination was **not** found; an explicit null-family path remains conservatively reachable. This does **not** refute indirect aliases via other fields, receivers, nested getters, allocation or same-frame runtime state. The null path is not proven to execute. Separate [platform CI42690309050](https://github.com/alwansan/raf/actions/runs/42690309050) SUCCESS is CPU/offline smoke only. Original Foam ShaderLab/CB0 and Adreno730 water pixels remain **unverified**, WATER-001 **OPEN / NOT_READY 0/3**. Next distinct engineering step: original managed caller/receiver and indirect alias path, not more duplicate direct token checks.

## T2 one-hop nested Texture callee test — 2026-11-09 20:31 UTC

Previous SHA-original direct pass0 destination → pass1 callee return-field audit `field_no_match_with_null` left nested helper return origins opaque. T2 reserved independent chat session `20261109T2020Z-T2-chat-foam-onehop-return-r8c5` BEFORE source edits. The updated Cecil check follows **at most one** original in-module, statically resolved, nonvirtual/final nested Texture-returning callee, tracking its own return value through the already bounded CFG+stack+local interpreter. Unknown/virtual, original external, exceptional, recursive and unsupported paths remain opaque and cannot be promoted to matching field evidence. Exact declared field token matches, if found, remain weaker than actual receiver/heap/frame identity.

Code commits [99c1f1c4](https://github.com/alwansan/raf/commit/99c1f1c40b978c92e67f558a1ef89dcd983c84b9), `0408e76d`, `5fc56b53`, and final [b61e2acf](https://github.com/alwansan/raf/commit/b61e2acf1bae1ea09e2f7bbece07e2f971dd2701) touched only T2 original-source analyser, strict source-free report validator, and regression tests; no protected original IL/field/token, raw asset or private data was published. The two intermediate attempts [CI42692810846](https://github.com/alwansan/raf/actions/runs/42692810846) and [CI42692872122](https://github.com/alwansan/raf/actions/runs/42692872122) failed on synthetic-only fixtures; [CI42693196369](https://github.com/alwansan/raf/actions/runs/42693196369) also failed synthetic recursion negative-control. Those failures did **not** execute the original stage; the fixture issues were fixed without relaxing the positive original evidence gate.

The final SHA-pinned [CI42693501006](https://github.com/alwansan/raf/actions/runs/42693501006), job `129419155294`, **COMPLETED SUCCESS**. Strict report Python **21/21 PASS**; source-free Mono.Cecil `T2_CECIL_ORIGINAL_BLIT_SYNTHETIC_PASS`; original ZIP2 SHA authenticated using 3,211,776-byte `Assembly-CSharp.dll` and 115,978,112-byte original Shader owner; private source purged before publishing safe finite results. Original stdout:

```text
T2_FOAM_PASS0_BACKTRACE RenderTexture typed_field static_type_only_no_instance_proof steps=6 void_calls=0
T2_FOAM_PASS1_BACKTRACE Texture typed_call_result static_type_only_no_instance_proof steps=21 void_calls=1
T2_FOAM_PASS1_CALLEE_RETURN_VALUE_FLOW value_mixed_with_explicit_null_literal
T2_FOAM_CROSSPASS_DECLARED_FIELD_RETURN_RELATION field_no_match_with_null
T2_FOAM_CROSSPASS_ONEHOP_FIELD_RETURN_RELATION field_no_match_with_null
```

**Bounded negative result:** allowing one statically resolvable nested Texture helper does not reveal any *new directly linked same declared field token* in the original pass1 source return. This is **not a complete proof of no indirect alias**: deeper nesting, different fields referring to one heap RenderTexture, receiver identity, runtime predicate selection and frame/lifecycle continuity remain unresolved. No Unity ShaderLab binding, CB0, Adreno 730 water pixels or device parity were tested. `WATER-001` **OPEN / NOT_READY 0/3**; no Mini/full game XAPK requested. Next T2 original-source hypothesis should examine receiver and object alias lineage without repeating a one-hop source-free test unless inputs differ.

## T2 — SHA-original Foam pass0 RenderTexture declared-field managed CIL writer footprint (2026-11-09)

Chat session `20261109T2040Z-T2-chat-foam-writer-census-z4m7` / `origin=chat` reserved its T2-only work scope before editing (commit `7410282dc45bb9d9b7e0afabf6303d697a19ccf5`). The precise question differs from prior direct and one-hop pass1 return provenance: *which managed methods contain CIL field-store opcodes to the exact declared field that supplies the pass0 Blit destination? Do the two Foam Blit calls occupy the same managed method, and is the destination field written in the pass1 Blit method?*

Implementation:
- C# Mono.Cecil (commit `a3a63adc197271cc798de3c7a0bbe06bf3617ecf`) scans the SHA-original 3,211,776-byte `Assembly-CSharp.dll` privately for exact declared `stfld`/`stsfld` references matching the original pass0 destination's already resolved `FieldDefinition`; classifies store count **zero/one/multiple**, method placement relative to the **pass0** Blit, and relative pass0/pass1 method co-location. A one-store "adjacent predecessor" is only an opcode family, not a proven right-hand-side value.
- A follow-up (commit `57b8f10be4f91af7b37b0b8eeec73c7e9b775b0c`) additionally scans the unique original **pass1** Blit managed method for the exact field store and classifies only literal CIL instruction order (before/after/both/none). The source-free privacy report's schema and adversarial fixtures were extended; malformed/private tags, mutually impossible store counts and fictitious crosspass heap identity remain rejected.
- First follow-up [CI42696515826](https://github.com/alwansan/raf/actions/runs/42696515826) failed in a new synthetic Python negative fixture because a pre-existing return-field consistency guard correctly fired earlier than the expected later guard; the source-original stage was not executed. Fixed the *test input only* at `fbe24922a60b895f88fd1ef0e4a2ed15a67a6a2d`.

Two **completed successful SHA-original** runs:
- [CI42695789057](https://github.com/alwansan/raf/actions/runs/42695789057), source `a3a63adc`, job `129427157145`: **24/24** Python tests, C# Cecil synthetic PASS; original assembly and shader owner `115978112` bytes SHA-authenticated; private scratch purged, safe report only.
- [CI42696649931](https://github.com/alwansan/raf/actions/runs/42696649931), source `fbe24922`, job `129430174641`: **26/26** Python, C# Cecil synthetic PASS, original ZIP2 authentication and private scratch purge PASS.

**Original structural evidence** (finite-safe stdout, no field names/tokens or private IL):
```text
T2_FOAM_PASS0_DEST_FIELD_CIL_STORE_CLASS multiple_resolved_direct_stores
T2_FOAM_PASS0_DEST_FIELD_CIL_STORE_PLACEMENT stores_only_in_other_methods
T2_FOAM_PASS0_DEST_FIELD_SINGLE_STORE_ADJACENT store_predecessor_not_unique
T2_FOAM_PASS0_PASS1_BLIT_LEXICAL_RELATION blit_sites_in_distinct_methods
T2_FOAM_PASS0_DEST_FIELD_WRITES_VS_PASS1_BLIT_IL pass1_method_no_direct_field_store
```

**Interpretation:** SHA-authenticated managed code contains **multiple resolved direct field store opcodes** to the same *declared pass0 RenderTexture destination field*. All recognized CIL stores are in **other managed methods than pass0 Blit**. The Foam pass1 Blit resides in a different managed method, and that pass1 method contains **no direct CIL store opcode to the exact pass0 destination field**. Thus observed explicit managed CIL field writes occur outside *both* Foam pass Blit methods. It does **not** prove when or whether writes execute, resource allocation identity, initialization order, equality of receivers/fields' stored objects, indirect aliases through other fields/getters, native/reflection writes, explicit null branch execution, ShaderLab/CB0 binding or Android GPU pixels. No original content changed and no full XAPK/mini APK requested by T2.

Suggested next distinct original-source investigation: the actual **writer methods' RHS expression/receiver object** and any unique CIL call edges feeding them from the two Foam paths, privately and with conservative abstract alias tracking. Keep exact symbol names/tokens/IL inside authenticated runner; release only finite source-safe categories, avoid asserting a runtime execution path without on-device evidence. Overall `WATER-001` remains **OPEN / NOT_READY 0/3**.
