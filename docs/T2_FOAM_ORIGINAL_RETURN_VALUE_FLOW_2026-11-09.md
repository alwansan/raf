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
