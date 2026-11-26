# المراجع الثابتة والأهداف السابقة

## مداخل المشروع

- clients/GT/OWNER_DIRECTIVE_RESTORE_FIRST_AR.md:الاستعادةأولاًوبوابات G0–G6؛الأنيميشنمؤجلبحسبتوجيهالمالكالأحدث.
- clients/GT/RESTORATION_PLAN.json و RESTORATION_PLAN_AR.md:الخطةوالسجل؛حقولتاريخيةلاتساويقبولاًحالياً.
- clients/GT/sessions/20261115-graphics-restoration/:الخطةوالفحوصوملاحظاتالعملالسابقة.
- clients/GT/METHOD_AR.md:المعايرةوأدواتالمختبروحدودتعميمها.
- docs/ZIP2_SOURCE_PROVIDER.md و scripts/gt_stage_serialized_owners.py:المصدرالمثبتوجمعالأجزاءوالتحقق.
- clients/GT/evidence/20261117_gt_post23_same_export_and_next6_cb_order_progress.json:آخر 688/98/37 ورفض NEXT6.
- clients/GT/evidence/20261120_gt_native_post23_and_next23b_integration.json و 20261120_gt_fft_utilities_original_topology.json و 20261120_gt_current_device_graphics_receipt.json و 20261121_gt_next23b_source_composition_verified.json.

## تشغيلات يجب عدم خلطها

| التشغيل | المعنى |
|---|---|
|[43929698985](https://github.com/alwansan/raf/actions/runs/43929698985)|SAME-EXPORT688/786 و 98Dummy/37GUID،لا pixel/runtimeproof|
|[44779897149](https://github.com/alwansan/raf/actions/runs/44779897149)|NEXT23b134stage source-only|
|[44781063594](https://github.com/alwansan/raf/actions/runs/44781063594)|2312routes نجحتثمفشل propertyflags|
|[44783011957](https://github.com/alwansan/raf/actions/runs/44783011957)|NEXT23bcomposition خاصكامل،لا Unity|
|[44781701884](https://github.com/alwansan/raf/actions/runs/44781701884)|FFTsource نجح،UnityDXC فشل errors1|
|[44783011963](https://github.com/alwansan/raf/actions/runs/44783011963)|NEXT6 لايزالمرفوضاً|
|[44053092399](https://github.com/alwansan/raf/actions/runs/44053092399)|بناء Native قديمناجح،ليسقبولبصريات|
|[45759923748](https://github.com/alwansan/raf/actions/runs/45759923748)|أولتجربةاصطناعيةفشلت|
|[45760345978](https://github.com/alwansan/raf/actions/runs/45760345978)|تجربةاصطناعيةفشلتقبلقبول pixels|
|[45760877767](https://github.com/alwansan/raf/actions/runs/45760877767)|UnityVulkan اصطناعي 120pixelsPASS فقط|

المصدر ZIP2:[15964ea8](https://github.com/alwansan/raf/tree/15964ea8f246b6e076ce26b60931ee2e1a9a2385).مصدر CL المحلل:[8db59a4](https://github.com/alwansan/CL/tree/8db59a417be025dd8194f202a6dd29aaa132d300)،جلسة LogRaft-20261120-194258-229.صور 12/13 نوفمبرتثبتالمشكلةالتاريخيةولاتثبتحالمرشحجديد.

## المراجع الخارجية للأدوات

- [UnityCsReference2021.3ShaderProperties](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Shaders/ShaderProperties.cs):PerRendererData2،NoScaleOffset4،HDR16؛الخصائصالأصليةحُفظتلااختُلقت.
- [UnityPy1.23.0](https://pypi.org/project/UnityPy/1.23.0/):رابط sdist وبصمتهفي toolchain/versions-and-checksums.json.
- [smol-v المثبت](https://github.com/aras-p/smol-v/tree/6303e979b59153ee7007fd14e06d3fed8687b64c).
- [AssetRipper المثبتتاريخياً](https://github.com/AssetRipper/AssetRipper/tree/036098ab525a3f9f693dc101edeb21faad4d32d8).
- [مختبرالرسومللقراءةفقط](https://github.com/alwansan/raf/blob/f933c4429803583d1ed5fa26e46bb0d3227f2027/prompt/graphics-lab/RESTORE_AR.md)،و[طريقة M00–M05](https://github.com/alwansan/raf/blob/1ca06009684047ef8156a939d4d2931326ad2cc7/gfxlab/PHASE_ONE_METHOD_HANDOFF_AR.md).المختبرمتشعبولايدمجتلقائياً،ولايُنسخقبولمعايرتهإلىكلاللعبة.

## تاريخ العمليات

caf77cf10:تشخيصالناروبوابة FFT؛6c071a414:دمجمسار post23؛c066f2997:تركيب NEXT23b؛ef321ee90:مصدر FFT ومحاولة Unity؛7e9925fdb:خصائص NEXT23b؛f3c8a2cda:آخر RESTORE عنالتجارب 26 نوفمبرقبلالتسليم.تحت history/نسخالمذكراتالكاملةبمافيهاأرقامتشغيلاتأقدموقراراتوإخفاقات؛لاينبغيحذفهاولااعتباركلنصقديمتعليماًحالياً.
