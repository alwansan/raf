# GT — دورة ربط Mesh وMaterial Texture من ZIP2
- **session_id:** `GT-20261112-CHAT-03-original-mesh-texture`
- **origin:** `chat`
- **agent:** `GT`
- **branch writable:** `feature/android-native-port`
- **ZIP2 pin (read-only):** `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- **observed starting HEAD:** `037788e5ac134358874f9316c82ab7809ddaede3` (T3)
- **verified code commit:** `ea3c81bd60182a11719b7962a569865ce283bd62`
- **GitHub Actions:** [43120209212](https://github.com/alwansan/raf/actions/runs/43120209212) — **SUCCESS** (synthetic + 82 authenticated original owners)
- **aggregate artifact:** [13900107915](https://github.com/alwansan/raf/actions/runs/43120209212/artifacts/13900107915)
- **pinned report:** [20261112_original_mesh_texture_graph.json](../evidence/20261112_original_mesh_texture_graph.json)

## ما تم تنفيذه فعلياً

1. إضافة `scripts/gt_original_mesh_texture_graph.py` و`tests/test_gt_original_mesh_texture_graph.py`، وإضافة اختبارات وفحص UnityPy حقيقي إلى workflow GT المعزول.
2. قراءة جميع 82/82 Serialized owner بعد التحقق من SHA256 المصدر من ZIP2، دون Git LFS ودون رفع بايتات اللعبة داخل artifacts.
3. تدقيق **176,708** موضع `m_Mesh` ناتجاً عن **176,345 MeshFilter** و**363 SkinnedMeshRenderer**: **176,480 رابطاً غير فارغ**؛ **176,006** مرجعاً موثقاً إلى كائن Mesh من أصل Unity الحقيقي، و**474** مرجعاً إلى موارد Unity المدمجة (engine transport) يجب فحص export mapping الخاص بها بشكل مستقل؛ **228 null** أصلية. **4,328 كائن Mesh مختلفاً مستخدماً مباشرةً** من أصل 4,708.
4. تدقيق **10,246** خانة `m_TexEnvs` من **1,556 مادة**: **4,583** مرجعاً غير فارغ، جميعها وصلت إلى كائن Texture من صنف أصلي صحيح؛ **5,663 null** أصلية. **3,373 كائن Texture مختلفاً مستخدماً مباشرةً**، و10,246 UV transforms صريحة موثّقة البنية.
5. اختبارات رفض صلاحيات/هويات غير صحيحة: رابط يشير إلى صنف خاطئ، ملف خارجي مجهول، معرف خارجي خارج الجدول، PPtr بلا pathID، UV غير منتهٍ، duplicate property، حمولة مصدر محرفة.

## حدود الإثبات المهمة

- `all_mesh_verified=false` في أداة التدقيق **ليس فشل فحص أو نقصاً لأصل الـMesh**: توجد 474 مرجعية إلى `Library/unity default resources`/engine transport ولا تصنف ضمن Mesh objects في الملفات الـ82؛ سجّلها منفصلة ولم نخمن GUID.
- التكستشرات الأصلية غير الفارغة ضمن الملاك الـ82 كلها موثقة بالهوية، لكن لا دليل على تكستشرات export أو Android وعرض البكسلات.
- الأعداد تخص source reference graph؛ لم يثبت بعد `ExportedProject` أو `.meta/GUID` أو `.resS` والـGPU أو الـAPK.
- مصدر ZIP2 للقراءة فقط، الفرع `feature/android-native-port` للكتابة فقط. لا تعديل لمنظومة T5 للتجميع ولا تشغيل native XAPK/إلغاء وظائف T1–T5.

## دورة GT التالية

1. اجمع material + texture + mesh source maps من هذه الأدوات داخل **نفس مثيل AssetRipper ExportedProject**؛ استخدم same-instance trace و`.meta` GUID واحذر remap يخلق مواد فاتحة أو textures null خطأ.
2. اختَر مجموعة مرئية حقيقية عالية الاستعمال وقرر هل العلاج على export أو payload stream؛ استعد `.resS` اللازمة عن طريق `gt_zip2_payloads.py` مع SHA256 وبدون LFS.
3. اختبر اصلاح export أصلي صغير مع حفظ GUID، لا تستنتج نجاح GPU من تحليلات المصدر؛ تعاون مع T1/T2/T3/T5 على نقطة الدمج واحفظ تقريراً جديداً.
