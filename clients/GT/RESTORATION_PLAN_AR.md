# GT — PASS G1/G2 same-route vertex/UV byte binding | 27 نوفمبر 2026

رأس البدء de21c5ef6f9cc4bcc4dda3a4c0eb4cc1d2f59335 مطابق، لا checkout محلي أو فرق متاح؛ لا وصول DNS محلي إلى GitHub، استخدم connector وActions. [23fe335](https://github.com/alwansan/raf/commit/23fe335acaf8b557cafaf2eb095d8311d299262f) أضاف scripts/gt_mesh_vertex_payload.py وربط V2 CLI بالـMesh owner/PathID ثم actual GUID/anchor في نفس Renderer/MeshFilter/SubMesh/Material/Shader/TexEnv route. provider full SHA/size وrange digest في نفس sequential read، once per provider للمجموعة، block memory فقط. legacy source_geometry يلغي cached verification ويقرأ owner bytes المثبتة نفسها؛ rehash لكل stream call في legacy، أداء production لم يختبر، لم نغيّر compressed/bindpose comparison. V2 يرفض compressed أو layout غير مثبت، يدعم contiguous single interleaved stream مع float32 XYZ وUV0؛ لا decoded values أو GPU. V1 API يبقى identity-only ولا يدعي bytes.

[00e969d](https://github.com/alwansan/raf/commit/00e969dbf71412f0ad8cf10f5acb38491a35b63a) workflow-only activation. [Actions 45947525967](https://github.com/alwansan/raf/actions/runs/45947525967) success؛ job 140335539245، guard [45947525970](https://github.com/alwansan/raf/actions/runs/45947525970) success. **60/60 tests** = 15 new byte/range +7 legacy geometry +21 route +17 B03. Public pinned nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8 .NET9 compiled؛ generated fixture source records actual 120 inline vertex bytes قبل export، one Mesh referenced by two Renderers، 9 actual collections،13 actual native YAML docs،2 scenes،2 complete byte-bound Renderer routes،4 complete SubMesh routes. 11 negative controls؛ الجديدة UV أو XYZ same-size bytes drift في actual Mesh YAML رفضت كلا المسارين مع unchanged descriptors/indices، 15 unit tests تغطي same-size provider mutation بعد النجاح، equal-length swapped stream range، inline/stream، missing/out-of-bounds، compressed/multistream، one-read overlapping ranges عبر blocks، legacy no cached trust. لا أصل أو binary source حقيقي؛ source stream tests parser-injected authored metadata، actual C# export inline only. لا raster/Android/GPU جديد ولا إصلاح مثبت للأبيض أو النار.

الأرشيف الخام clients/GT/sessions/20261127-vertex-payload-route-binding/actual-run-45947525967.zip، 5016 bytes SHA256 8b601146b3ab01bfe6826720a713b5d571c5c60cb267c262e21a45b8fba042bc، blob ed58915b47865897d6648e5ebd7b3749c32955c2؛ CRC/size/SHA verified locally و9 member hashes؛ artifact 15175331956. evidence.json يحفظ counts/bounds/steps/compiled hashes. لا تعتمد على sandbox أو artifact المؤقت. Generated YAML fixture disposable؛ يعاد إنشاؤه من نفس pinned workflow/code. لم تتغير أرقام census التاريخية: 688/786 non-dummy و98 dummy و37 GUID.

**التالي G1-G2-material-scalar-color-same-route-value-binding:** أعد استعمال B22.normalize وB44.normalize_colors لربط exact binary32 RGBA/float وint values داخل نفس V2 route، missing/extra/wrong-type/value controls، لا خلط shader property bytes مع Unity color-space أو GPU. لا تكرر export/Unity الرسم السابق بلا غرض إثبات جديد. A3 blocked حتى مصدر أصلي مأذون مثبت؛ G0–G6 مفتوحة؛ لا أصل/LFS أو هاتف جزئي أو XAPK. CL/المختبر قراءة فقط، BLACK خارج النطاق، animation مؤجل. فرع الكتابة الوحيد feature/android-native-port بلا force push، راجع HEAD وActions أولاً.

---

# GT — actual authored scene YAML route join | 27 نوفمبر 2026

رأس البدء e2eb41dbb25635bfd61aaa087b24fddf150de999 مطابق؛ لا checkout محلي ولا تعديل محلي؛ الأرشيفات السابقة محفوظة. ed643c637366c1ae66dfef5680d03f7cff3cd3b6 أضاف actual public scene route witness: tools/synthetic_material_alpha/RaftAuthoredSceneRouteWitness.cs + scripts/gt_authored_scene_route_witness.py؛ شدد scripts/gt_renderer_submesh_routes.py لعدم قبول Renderer/GameObject أو MeshFilter/GameObject خارج نفس document، يتطلب local PPtr في الاتجاهين، native serialized type2، وأدرج native .texture2D/.texture3D/.texture2DArray suffix case-insensitive. 3 negative unit tests جديدة. Public pinned nowl-it/AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8 .NET9، typed generated objects وexplicit export collections، ليست production auto-selection أو original binary source. مصدر مستقل قبل التصدير من actual generated PPtrs/vertex descriptors/index ranges وexternal dependency tables. مشهدان، PathID متساوٍ في owner مختلف للخامات وللـRenderer مع dependency order مختلف، hidden components=2. Native shader/texture identity فقط لا program/pixel proof.

[45946688897](https://github.com/alwansan/raf/actions/runs/45946688897) فشل compile CS1061/CS0266 بسبب C# Distinct inferred object لا IPPtr؛ 38 regression tests نجحت، لم يحدث export. guard [45946688780](https://github.com/alwansan/raf/actions/runs/45946688780) success. 0caf15f6a892549bdcc09d055b349a96be1ec65f صحح explicit Distinct<IPPtr>. حفظ فشل البناء الخام clients/GT/sessions/20261127-actual-authored-scene-routes/failed-build-45946688897.zip (3431 bytes SHA256 3307811851bcce07faa76406610ecce02f106f95f424b31d75e83dcc3c5ab8ab blob 42db56a11e5bbdfc18a9bf7c9b05f5c70baf8382)، initial-build-failure.json. a630e5855fe9373d27a8876a7391835e35b2e4e8 أطلق [45946854653](https://github.com/alwansan/raf/actions/runs/45946854653) success، job 140333416363، guard [45946854501](https://github.com/alwansan/raf/actions/runs/45946854501) success. 38/38 tests (21 ordered-route،17 B03)، **9 actual export collections،13 actual native YAML documents،2 scenes،2 complete Renderer routes،4 ordered SubMesh/Material/Shader/TexEnv links**. 9 negative controls مرفوضة: swap valid materials في actual scene YAML، wrong foreign scene GO، same-document nonlocal reference، stripped Renderer، swapped dependency table same PathIDs، unscoped type0، wrong serialized type3، nonexportable، hidden source census not promoted. 2 hidden renderers ليست baseline؛ عند إضافتها يبقى census unproven، لا ادعاء full coverage. Actual source objects generated لا serialized original reader. C# actual YAML export executed، لا Unity أو Android؛ vertex payload/UV samples وshader program/color/scalar/GPU غير مثبتة في هذه الدفعة. أرشيف clients/GT/sessions/20261127-actual-authored-scene-routes/actual-run-45946854653.zip (3771 bytes SHA256 f87979a8a236de3092292909a2339f54d2c84d645f594af53940c47e9b446d25 blob 7335605c22dfcd00bf800aa51c5f4cb29eb27a81) verified CRC/size/hash/members. يحفظ aggregate receipts/logs فقط، fixture generated YAML/trace المؤلفة كانت disposable، قابلة لإعادة الإنشاء من نفس pinned code/workflow. evidence.json يحفظ النتيجتين.

**التالي G1-G2-mesh-vertex-payload-same-route-byte-binding:** ربط vertex/UV payload الفعلي بنفس Renderer route. gt_verify_original_mesh_export.py source_geometry يحقق provider ثم seek/read منفصل ويعيد استعمال cached verification؛ استخدم same-read SHA/size/range binding، وcounterfactual same-size mutation أو swapped stream range أو UV bytes drift مع نفس descriptors/indices. لا تخلط isolated geometry counts التاريخية 4708/4708 مع route coverage. عند الحاجة أعد actual public export لإثبات payload جديد لا تكرر الرسم/compile السابق بلا سبب. A3 blocked حتى مصدر أصلي مأذون مثبت؛ G0–G6 مفتوحة، الأبيض والنار لم يثبت إصلاحهما في اللعبة. census historical 688/786 non-dummy و98 dummy و37 GUID دون تحديث بلا census جديد. لا اقتناء أصل/LFS، لا هاتف جزئي أو XAPK، CL/المختبر قراءة فقط، BLACK خارج النطاق، animation مؤجل. فرع الكتابة الوحيد feature/android-native-port بلا force push، تحقق HEAD وActions أولاً.

---

# GT — compiled public component capture + actual authored SubMesh Vulkan | 27 نوفمبر 2026

رأس البدء d32b9392ec7563328a15e05d498c68054d2766a1 مطابق؛ no local checkout، محفوظات سابقة سليمة. public compiler [45944521571](https://github.com/alwansan/raf/actions/runs/45944521571) success كما في clients/GT/sessions/20261127-public-renderer-pointer-witness/evidence.json؛ 8 component global/local/cross-scene pointers، hidden=2، same instance، .NET9 public pinned tool. لا scene YAML export أصلي أو حتى actual authored serialized scene YAML في public witness؛ source generated objects لا original source.

21ed9c7a148c71dad9832d321b01cafd1c727ebb أضاف C# SyntheticSubmeshRouteValidation، شيدرين AuthoredRouteA/B (RGB vs BGR)، PNGs 4x2 خطية غير متناظرة، persistent Mesh A/decoy + Material A/B + imported texture A/B؛ 2 submeshes 3+5 columns، 8 vertices/UV0، explicit baseVertices 0/4 or 4/0. 4e1b28de9c9caa0ef81dad5e5967a9487516604d شغّل Unity [45944786101](https://github.com/alwansan/raf/actions/runs/45944786101)؛ job 140326878133، guard 45944786181 success، 13 oracle tests نجحت، render step success وraw OBSERVED 10 cases، لكن **verifier FAILED numeric_vector_mismatch**. السبب Python oracle اعتبر ShaderLab Color tint linear بينما Unity 2021.3 Linear project يرسل sRGB Color بعد linearization (الـPNG importer non-sRGB فلا تحويل ثاني). مرجع رسمي https://docs.unity3d.com/2021.3/Documentation/Manual/SL-PropertiesInPrograms.html#color-spaces-and-colorvector-shader-data . لا تغيير raw أو shader أو probe أو threshold. أرشيف failure/raw clients/GT/sessions/20261127-authored-submesh-vulkan/actual-raster-run-45944786101.zip (6410 bytes SHA256 b5d7400fa34948d2fe472945aa6331e1bc47b659f1d3990e5d2d5b044e44d391 blob 614b6b194daaea67e98b33ac2f8f1f844f0c4fab)، raw receipt SHA256 74076d174a9b9e9c41316dcf00688fed29cd5bb32a76ee05ea96eccc80b227b1، CRC/size/hash verified. 37da2c1ee64bfa256018da5a5aa1cffc5b22b080 أصلح equation باستعمال piecewise sRGB EOTF على tint RGB فقط، وأضف literal white/linear texture expected وnegative gamma test. 0bade38ed8d4d68271571add9d4396f06b64d111 شغّل CPU-only replay [45945368677](https://github.com/alwansan/raf/actions/runs/45945368677) success، job 140328724542، guard [45945368595](https://github.com/alwansan/raf/actions/runs/45945368595) success. **15/15 oracle tests، 320/320 Vulkan RGBA pixels +16/16 imported RGBA8 pixels من نفس التشغيل الفعلي، 10 cases و8 counterfactuals، max error 7.804148227652519e-08، tolerance .008، restored baseline verified**. swapped materials وreversed mesh routes لهما نفس pixels ولكن actual mesh/indices/material identities مختلفة، فلا يمكن استنتاج السبب من الصورة فقط. white/null texture كلاهما ينتج linear tint؛ wrong shader/valid texture/UV/tint drift مميزة. Unity 2021.3.45f2 Linux Vulkan llvmpipe software. لا rerender. أرشيف replay clients/GT/sessions/20261127-authored-submesh-vulkan/actual-replay-run-45945368677.zip (2280 bytes SHA256 9625cfebaae29f0bb3f8c24bd657e27f731725f9685e71f8aed528ae22580254 blob 911aa48bd3881f05e00131df75192c9dd0502303) verified CRC/size/hash/members، evidence clients/GT/sessions/20261127-authored-submesh-vulkan/evidence.json وinitial-raster-evidence.json.

**التالي G1-G2-actual-exported-scene-route-join:** وصل public capture الحقيقي إلى actual authored SceneExportCollection YAML export والـPython ordered-route gate، باختبارات cross-owner same PathID وhidden/stripped وwrong document/ordered valid-but-wrong slots. لا تكرر public build أو raster الناجح بلا سبب جديد. إن تعذر export المؤلف، اختبر collection contract/cross-owner بأدلة مؤلفة وصرح بالعائق. لا source original أو Android أو إثبات إصلاح الأبيض والنار. A3 blocked حتى المصدر الأصلي المأذون مثبت؛ G0–G6 مفتوحة. census historical 688/786 non-dummy و98 dummy و37 GUID لا تحديث دون census فعلي. لا أصل/LFS أو هاتف جزئي أو XAPK، CL/المختبر قراءة فقط، BLACK خارج النطاق، animation مؤجل. اكتب فقط feature/android-native-port بلا force push، تحقق HEAD وActions أولاً.

---

# GT — public exporter compiled component witness | 27 نوفمبر 2026

رأس البدء d32b9392ec7563328a15e05d498c68054d2766a1 مطابق؛ لا checkout محلي قديم ولا تعديل محلي. الأرشيفات السابقة محفوظة. راجعنا public pinned AssetRipperCLI@036098ab525a3f9f693dc101edeb21faad4d32d8: SceneExportCollection.cs blob 798fc97810f49033d1eb9f671aa92179e3519a3f يعيد GUID/anchor/type2 إذا isLocal=false؛ MetaPtr.cs blob 4e5bf10743b3d7cb484dcfb45d31d0560bd2706f محلي GUID zero لكن AssetType.Serialized=2 ويكتب YAML fileID فقط. ProjectAssetContainer.cs blob d16c044c5a5f061f90afa07fe1314c9a399bbf60 يحدد local بحسب CurrentCollection. GameObjectHierarchyObject.cs blob 6f5020d6e3be2276055777f221114c1160f4c0f1 يستبعد HiddenAssets من ExportableAssets؛ Prefab source reviewed فقط لا runtime proof. 56fdc662167e3d15cb1aef4eb46a56e904a975f6 شدد optional component capture إلى collection.Exportable وExportableAssets وأبقى W1 helper الأصلي pinned دون تعديل. 3c1c97c43f7a3101027c23bd0310a3421fc4b4dd شغل public-only .NET9 build وactual compiled Capture على مشهدين مؤلفين من generated objects. [45944521571](https://github.com/alwansan/raf/actions/runs/45944521571) success، job 140326056156، guard [45944521622](https://github.com/alwansan/raf/actions/runs/45944521622) success. 8 component rows و8 global/8 local/8 cross-scene pointers صحيحة، hidden components مستبعدة 2، تساوي source PathID في owner مختلف ليس هوية، same instance material/mesh/component traces، رفض missing mesh trace. لا original serialized reader/actual scene YAML export أو Unity أو prefab runtime. الخام clients/GT/sessions/20261127-public-renderer-pointer-witness/actual-run-45944521571.zip (1398 bytes SHA256 a46a9ae25a67e0d72025ae447fdcf1970324c3f3c765431e5ab8acd7f81c59fd blob 6e2be73b7afd80f85b2c9aea26fad1922178b0c6) verified CRC/size/hash/members. دليل clients/GT/sessions/20261127-public-renderer-pointer-witness/evidence.json.

21ed9c7a148c71dad9832d321b01cafd1c727ebb جهز authored Vulkan 10 cases لمجسم غير متناظر 3+5 columns، 2 Mesh assets/2 Materials/2 PNG و2 shader programs وUV0 وbaseVertex، 8 counterfactuals وrestored baseline. oracle مستقل Python يقارن 16 imported RGBA8 +320 raster، ويثبت أن reversed mesh routes وswapped materials قد ينتجان نفس pixels لكن binding مختلف؛ لا claim real raster قبل النتيجة. 4e1b28de9c9caa0ef81dad5e5967a9487516604d أطلق [45944786101](https://github.com/alwansan/raf/actions/runs/45944786101)، job 140326878133، guard [45944786181](https://github.com/alwansan/raf/actions/runs/45944786181) success؛ عند آخر check stage/tests وactivation budget ناجحة وDocker Vulkan image in progress. **راجع التشغيل الموجود أولاً دون تكراره**. لا مصدر أصلي أو XAPK. A3 blocked، G0–G6 مفتوحة. الأبيض والنار لم يثبت إصلاحهما في اللعبة. لا هاتف جزئي، CL/المختبر قراءة فقط، BLACK خارج النطاق، animation مؤجل، write branch feature/android-native-port وحده.

---

# GT — G1/G2 ordered renderer submesh material routes | 27 نوفمبر 2026

رأس البدء 1d1a65446ceac3a7a114b1d706aabb0a518a565b مطابق؛ لا checkout محلي قديم ولا تغييرات محلية؛ محفوظات الدفعات السابقة سليمة ولم تمس. أدلة 20261114_gt_full_mesh_export_verified.json التاريخية تثبت 4708/4708 geometry من 82 owners و23 streams لكنها لا تثبت renderer bindings. B03 الهيكلي يتحقق من وجود Material دون ترتيب source slots. تمت مراجعة gt_original_mesh_texture_graph وgt_mesh_restoration_priority وgt_verify_original_mesh_export وB03 وB22/B44 وT3. 

0426fceda2eb6e3da15c5f05d5e709706e07bcc0 أضاف scripts/gt_renderer_submesh_routes.py وopt-in --renderer-lineage في scripts/patch_export_lineage.py، يحافظ على pinned shared RaftExportLineage.cs دون تعديل. private component trace (1/23/33/137) يستخدم نفس instance للـMaterial/Shader/Texture وmesh trace فقط عندما يتوفر RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE وmeshPath. Compose source-only verified؛ C# hook لم يُترجم/يشغل بعد. فاحص source يأخذ bytes المطابقة لحجم/SHA وفق manifest checkout المثبت، ويقارن GameObject membership وMeshFilter أو SkinnedMeshRenderer direct mesh، triangle-list ordered submesh ranges وinline index buffer SHA/actual index bounds وUV0 descriptors، renderer material array بالترتيب، identity للـMaterial/Shader/TexEnv وUV transform. يرفض cross-document/mixed-instance/duplicate/null/builtin/unknown target غير المثبت، لا يختلق policy لعدد مواد غير مطابق لعدد submeshes. لا إثبات vertex samples أو shader program/color/scalars أو GPU. scope محدود selected owners وtriangle lists/inline indices؛ لا يغلق G1/G2. source serialized parser injected metadata في المؤلفات.

f8ca88b72d8dfcb43214dfab232c14bf21fef916 أضاف negative control يثبت أن swapped valid materials يمر عبر B03 القديم لكن يفشل الفاحص الجديد. c104da00d10844505b0e39753a163263f2c40882 شغل CPU [45943552013](https://github.com/alwansan/raf/actions/runs/45943552013)، 13/14 pass، فشل test_uv_transform_drift لأن source/export fixture يشتركان nested dict، لا ادعاء نجاح. 62e0e1c7136461759fe3f5cfa3274dd557e4f0c1 فصل deepcopy وأثبت invariant للمصدر. 9576c4dd4034ac927609976bd3086633f56f5bef منع native .asset wrong-class من image-import fallback وأكد SkinnedMeshRenderer وwrong GameObject وactual byte snapshot/SHA drift قبل parser. d99a05446e2ee33c0165863b1e985b00e898e982 شغّل [45943682655](https://github.com/alwansan/raf/actions/runs/45943682655) success، job 140323418684، guard [45943682730](https://github.com/alwansan/raf/actions/runs/45943682730) success، جميع 48 tests (18 new route،17 B03،7 mesh export،6 B02). Actual authored YAML وPNG؛ PNG metadata/identity فقط لا raster. 

حفظ الخام الناجح clients/GT/sessions/20261127-white-renderer-submesh-routes/actual-run-45943682655.zip (2777 bytes SHA256 f0e6b764a48a3a92ff7e80a41fef621f7ee36390cf79c7efd9429abb066caeec blob 381818858a15fd8391734dc8af5fceefaf490517) والخام الفاشل clients/GT/sessions/20261127-white-renderer-submesh-routes/failed-run-45943552013.zip (755 bytes SHA256 9f5f500c7e64e58ac839e39883b1585e55985e86f199ab2ef70d5cb54c17d61c blob d4cb7d1c234a79576a6701e7959c9d5d399d0b9d)؛ CRC/size/hash/عضويات محلياً. evidence.json يحفظ كلا التشغيلين وأسباب الفشل والتصحيح. لا إعادة Unity أو مصدر أصلي أو APK.

**التالي G1-G2-white-renderer-submesh-runtime-witness:** تحقق من opt-in C# hook على public pinned AssetRipper compile فقط بلا أصول، وتأكد من semantics لمراجع Scene components (لا ترقي type0 غير مقيد). ثم authored Unity Vulkan raster للـsubmesh routing مع PNG/Material مستقل وnegative controls swapped/wrong mesh/white texture/UV. لا تكرر الاختبارات الناجحة بلا سبب. A3 معلق لمصدر مأذون مثبت؛ G0–G6 كلها مفتوحة؛ 688/786 non-dummy و98 dummy و37 GUID historical فقط بلا census جديد. الأبيض والنار لم يثبت إصلاحهما على اللعبة. لا اقتناء أصل/LFS، لا هاتف جزئي أو XAPK. CL/المختبر قراءة فقط، BLACK خارج النطاق، الأنيميشن مؤجل. فرع الكتابة الوحيد feature/android-native-port، لا force push، تحقق HEAD وActions أولاً.

---

# GT — نجاح G5 byte-bound top mip وdocument-scoped local | 27 نوفمبر 2026

رأس البدء 3d82da96361faa7f35c45437ff85fa49dbd7912c مطابق؛ لا checkout محلي قديم، الأرشيفات السابقة محفوظة. 09f075f2cd3e27c611b54b1ad0494e8a4f977cdb [skip ci] أضاف gt_particle108_source_pixel_parity.py وربطه بـgt_particle108_export_alpha_diagnostic.py؛ ec5b54df974c12071f901bfda753f82f79531494 شغّل CPU فقط. [45942540652](https://github.com/alwansan/raf/actions/runs/45942540652) success، job 140319862869، guard [45942540566](https://github.com/alwansan/raf/actions/runs/45942540566) success. 53 tests (19 byte/pixel، 13 imported-alpha oracle، 11 provenance، 10 legacy). أعيد التحقق من الأرشيف الخام لـ45941449651 بنفس SHA للـreceipt و192 imported+192 raster؛ تصحيح reason نجح دون إعادة Unity؛ max RGBA8=0، max raster=0.0006205881014575976.

مسار source top mip يقرأ owner bytes كاملة وفق pin، يرسل نفس bytes إلى parser، يثبت manifest Git blob، يقرأ SHA256/size لكامل provider ويقتطع offset/range في نفس القراءة لا seek لاحق. adapter يمرر explicit payload إلى UnityPy 1.23.0 دون ResourceReader ضمني. يرفض missing/drift/manifest substitution/out-of-bounds/inline+stream/traversal/stripped mips. مقارنة decoded RGBA8 / 8-bit PNG top-left بلا resize أو flip للتسوية أو color transform. اختبار decoder وPNG حقيقي على RGBA32 مؤلف؛ serialized owner parser injected metadata وليس ملف Unity serialized أصلي. لا إثبات لصيغ الأصل المضغوطة أو اتجاه/ألوان أصل اللعبة. لا كشف private IDs/pixels. الأرشيف clients/GT/sessions/20261127-particle108-byte-pixel-parity/actual-run-45942540652.zip (4270 bytes، SHA256 af2d1953c6e73236a0df424eb07eac2c42aa873c3c12b3376c5dd00a12a2881d)، blob e5b901f08387373e65b90b4690cd165269baa09c؛ CRC/size/SHA وعضويات الأرشيف محققة محلياً. دليل clients/GT/sessions/20261127-particle108-byte-pixel-parity/evidence.json.

0f75b8f1cb72eb2f87009bda4a537e8390a0f962 [skip ci] شدد الفرق بين alpha تغير عند الإحداثيات وnet nonopaque population loss؛ الصورة المقلوبة ذات histogram مطابق ليست alpha loss. أكد مسار صورتين خارجيتين مع actual payload decoder، inline وstream، exact vs flipped. ربط إثبات Type0 في Particle108 بجرد وثيقة B05: global class28 trace، exportable True، نفس document GUID/anchor، class28 غير stripped، وكل slots المحلية في نفس الوثيقة، وحساب تعداد slots يطابق original targets. لا يعده صورة مستقلة أو pixel proof؛ الحالة الأصلية historical nonzero Type0 ما زالت pending. [45942715208](https://github.com/alwansan/raf/actions/runs/45942715208) success، job 140320396919، head ff72bf62344db3426aacd056c8d5b59d67374efc، guard [45942715270](https://github.com/alwansan/raf/actions/runs/45942715270) success. 46 tests (20 pixel، 16 provenance، 10 legacy) منها 6 جديدة وregression للوظائف المتغيرة؛ لا replay مكرر ولا Unity. الأرشيف clients/GT/sessions/20261127-particle108-local-net-loss/actual-run-45942715208.zip (2775 bytes، SHA256 5d7386415688c93d8195cecd5fa06fcbb401be956ac8d2e7f9457197a72f70c4)، blob 2d0ea85f0082c5edefd4453ccfce6cc6bbf895f2؛ CRC/size/SHA/عضويات محققة محلياً، clients/GT/sessions/20261127-particle108-local-net-loss/evidence.json.

**التالي G1-G2-white-renderer-submesh-material-provenance:** عد إلى أولوية الأبيض عبر ربط Mesh submesh/UV وRenderer.m_Materials المرتبة إلى نفس trace للـMaterial/Shader/TexEnv؛ اقرأ gt_original_mesh_texture_graph وgt_verify_original_mesh_export وgt_mesh_restoration_priority وB03 وB22/B44 وأدلتها أولاً. اختر عيباً حقيقياً، واختبره بمؤلفات غير متناظرة؛ لا تعد اختبارات G5 الناجحة بلا سبب. source parity الحالي diagnostic فقط؛ لا أصل أو Android أو إصلاح بصري فعلي. A3 معلق لحين إثبات المصدر المأذون؛ G0–G6 مفتوحة، census التاريخي 688/786 non-dummy و98 dummy و37 GUID دون تحديث بلا census فعلي. لا اقتناء أصول/LFS، لا هاتف جزئي أو XAPK. CL/المختبر قراءة فقط، BLACK خارج النطاق، الأنيميشن مؤجل. فرع الكتابة الوحيد feature/android-native-port، لا force push، تحقق HEAD وActions أولاً.

---

# GT — نجاح G5 TextureImporter Vulkan وB05 document scope | 27 نوفمبر 2026

رأس البدء e501998a2128a894ecaff80b7987db0f15033536 مطابق، لا checkout قديم محلي؛ كل الأرشيفات السابقة محفوظة. 91923a9f74ba32934a273c5497b1c9fb19e03ce8 أضاف اختبار PNG مؤلف، 265f639ccb4136c020ac262e7f799e803418ab76 شغل Unity فقط. [45941449651](https://github.com/alwansan/raf/actions/runs/45941449651) ناجح، job 140316463895، guard [45941449640](https://github.com/alwansan/raf/actions/runs/45941449640) ناجح. Unity 2021.3.45f2 Linux Vulkan llvmpipe (software)، 5 reimports على نفس PNG/GUID/Material، 8 حالات، 192 قراءة RGBA8 مطابقة تماماً و192 raster RGBA محققة، max error 0.0006205881014575976، 12 oracle tests و7 اختلافات عن FromInput linear. FromInput alpha8=[255,0,128,255,64,0]؛ None=[255,255,255,255,255,255]؛ FromGrayScale=[0,64,128,192,255,32]؛ sRGB غير alpha، وضوابط wrong blend/white/null binding/missing tint. التغيير في RGB بسبب sRGB لا alpha؛ لا Android hardware أو أصل. PNG bytes ثابتة قبل/بعد. الأرشيف الخام clients/GT/sessions/20261127-imported-alpha-vulkan/actual-run-45941449651.zip (4985 bytes، SHA256 9711df98d2dee6a28fb4d943027377059106f0c16f408391855df32edf8c431e)، blob 5143ce0954c843a809471a03d2c90176d3987bd1. CRC/size/hash ومقارنة raw receipt SHA والتحقق الحسابي المستقل محلياً لكل 192+192 قراءة ناجحة. عيب تسمية في verified.json: reason=Unity_receipt_missing رغم PASS وraw OBSERVED؛ حفظنا الخام كما هو، صححنا reason للنجاح في verifier وأضافنا regression (لم يشغل بعد، replay source-only هو أول التالي). لا إعادة Unity لازمة لتصحيح الوصف.

ccf28b3af40c191ad6da21fc56c404fac33217ca [skip ci] أصلح B05 وfull 82-owner wrapper، ثم ee8c0cc55ab83cc888bbe452bc0f39bd04ecfccd شغل CPU source-only. [45941656489](https://github.com/alwansan/raf/actions/runs/45941656489) ناجح، job 140317118772، guard [45941656623](https://github.com/alwansan/raf/actions/runs/45941656623) ناجح. 60 اختباراً (31 B05 منها 11 جديدة، 8 full-export، 11 Particle108 provenance، 10 alpha). Type0 trace triple متطابق لا يكفي؛ تحقق من GUID الوثيقة الفعلي وanchor/class/root غير stripped وexportable True. يرفض duplicate GUID أو anchor داخل وثائق المواد، wrong class/target، ولا يقبل غياب الجرد. ملفات YAML مؤلفة حقيقية، قراء المصدر محاكَون. الأرشيف clients/GT/sessions/20261127-b05-local-texture-documents/actual-run-45941656489.zip (3372 bytes، SHA256 5464c7312507a5c8ea699000602f37a613f69bf1f22447678fc13f248369533c)، blob 63f84da0d06f7d6f47423182cd0520cc784852ea، CRC/size/SHA محلياً. لا تشغيل بوابة الأصل أو إثبات بصريات اللعبة.

**التالي G5-Particle108-source-alpha-pixel-parity:** أعد تحقق الإيصال المحفوظ source-only بعد إصلاح reason، ثم ربط SHA/size/range لكل stream/provider بالبايتات التي يقرأها decoder؛ قارن بكسلات alpha للصور الخارجية الموثقة بمرجع المصدر على عينات مؤلفة مع ضوابط اختلاف موضع البكسل رغم histogram مطابق. إثبات local Type0 فقط عند توافر وثيقة/anchor/class فعلي. لا تعِد raster أو اختباراً ناجحاً دون علة. A3 معلق لحين إثبات المصدر الأصلي المأذون؛ G0–G6 مفتوحة، لا إصلاح مؤكد للأبيض أو النار، لا اقتناء أصل/LFS، لا هاتف أو XAPK. CL/المختبر قراءة فقط، BLACK خارج النطاق، الأنيميشن مؤجل. census التاريخي 688/786 non-dummy و98 dummy و37 GUID لم يتغير. فرع الكتابة الوحيد feature/android-native-port، لا force push، لا فقد محلي. تحقق HEAD وActions أولاً.

---

# GT — نجاح G5 alpha/Texture2D provenance | 27 نوفمبر 2026

رأس البدء fb9bb71d2bb3e6e8c8784ae6f0548bafffe01aaf مطابق للرأس الحي؛ G4 وG5 السابقان ناجحان ولا تشغيل متعارض. دفعة a5eff59cd7c651ff32f0f59dc88b3ff0e291e541 [skip ci] أصلحت مسار gt_particle108_export_alpha_diagnostic.py، ثم f1f69e21cb2b867e014121e3c45ee4bb3145f3b3 شغّل الفحص المؤلف فقط. [45940660052](https://github.com/alwansan/raf/actions/runs/45940660052) success، job 140313961151؛ الحارس [45940660054](https://github.com/alwansan/raf/actions/runs/45940660054) success، بقية jobs skipped. 70 اختباراً ناجحاً (11 اختبار تكامل جديد لملفات Material YAML/PNG حقيقية مؤلفة، 10 Particle108 legacy، 20 B05، 29 B46 texture integrity). فقط قراء المصدر محاكَون؛ الفاحص والـYAML والـPIL فعليون. لا Unity/Android أو أصل.

أصبح الفاحص يحفظ كل صف Texture2D28 من trace بدلاً من إسقاط المطابقة كلها عند Type0 أو غياب صف؛ يرفض تناقض fileID/GUID/type ويقيد external Texture2D image بـ2800000 وGUID صالح غير محجوز، ويرفض importer array. لا يحسب PPtr inferred كـexact ولا يثبت Type0 محلياً ولو تطابق الثلاثي غير المقيد بالوثيقة. يفصل status الكامل عن missing trace وعن local partial، ويحفظ عدادات UV والـalphaSource none/input/grayscale كمؤشرات خطر للصور غير المعتمة لا نتائج Unity. يرفض trace JSON duplicate keys وMaterial document collision وتباين PPtr؛ لا تعديل Material أو texture. لا ادعاء إصلاح النار أو الأبيض في اللعبة.

الأرشيف الخام clients/GT/sessions/20261127-particle108-alpha-provenance/actual-run-45940660052.zip (3399 bytes، SHA256 f22a640b1e8fa23cffa73da984d846887a4717af7c7dd598be0eed055c999f64)؛ blob 8262c39fca5d0a0c0c91864bc2c72b9c5fc0fe93. تحقق محلي CRC والحجم والبصمة وكل سجلات الاختبار وreport.json؛ manifest clients/GT/sessions/20261127-particle108-alpha-provenance/evidence.json. لا إعادة اختبار Unity محلياً، لا checkout سابق؛ أرشيفات الدفعات القديمة موجودة. لا اقتناء أصول أو LFS، ولا APK/XAPK.

**التالي G5-imported-alpha-vulkan-pixels:** الاختبار السابق SyntheticMaterialAlphaValidation.cs يستعمل Texture2D.SetPixels لا TextureImporter من PNG. نفّذ تجربة Unity Vulkan Linux مؤلفة واحدة على alphaSource None/FromInput/FromGrayScale مع نفس PNG وMaterial، وافصل قناة alpha المستوردة عن tint وblend وsRGB/mips. سجل readback RGBA وضوابط wrong blend/white/fallback؛ oracle مستقل. لا تعتبره إثبات Android أو أصل Particle108. إذا تعذرت Unity انتقل إلى B05 document-local pointer scope ومقارنة source/export على مؤلفات. لا تعد الدفعات الناجحة بلا سبب. A3 معلق لمصدر مأذون مثبت؛ G0–G6 مفتوحة. أولوية الأبيض والنار مستمرة، census التاريخي 688/786 non-dummy، 98 dummy، 37 GUID دون تحديث بلا census جديد. CL/المختبر قراءة فقط، BLACK خارج النطاق، الأنيميشن مؤجل، لا هاتف جزئي أو XAPK قبل G0–G6. تحقق HEAD وActions عند Continue.

---

# GT — نقطة الاستئناف الأحدث | 27 نوفمبر 2026

## GT — نتيجة G4 FFT receipt v2 | 27 نوفمبر 2026

[45938699002](https://github.com/alwansan/raf/actions/runs/45938699002) ناجح؛ job 140307767792، رأس a6f76b425ef02dddf8885412b3c864a354ca46fd، وحارس [45938699019](https://github.com/alwansan/raf/actions/runs/45938699019) ناجح. نجح منتج C# الفعلي في Unity 2021.3.45f2 Android Vulkan AssetBundle مؤلف فقط (hlslcc)، 7 ممرات و7 blobs و14 وحدة SPIR-V فريدة محققة، 21 مرجع FS، صفر keywords فعالة وأربعة Stereo غير نشطة. 22 regression و3 selftests و14 ترجمة/تحقق خارجي و2 تحوير إحداثيات مرفوضة. رفضت 7 ضوابط إيصال: تبديل المصدر/إيصال المصدر/الحزمة مع نفس الحجم، إصدار قديم، حجم خاطئ، تغيير بايتات إيصال Unity مع نفس المعنى، محاولة قبول المؤلف كأصل. تحقق محلي من CRC والحجم والبصمات والتزامات الإيصال؛ لا إعادة Unity محلية. الأرشيف الخام clients/GT/sessions/20261127-fft-receipt-provenance/actual-run-45938699002.zip (13229 bytes، SHA256 9228d97107ed3d70c77b81156370dfefe51ea431c5e88a11b6324fd57281d9fb)، ومراجعة clients/GT/sessions/20261127-fft-receipt-provenance/evidence.json. تغيرت بوابة الأصل في الكود؛ اختبار المثبت استخدم decoder mock، لا تشغيل أو قبول أصل فعلي، لا حل مثبت لخطأ FFT الأصلي، الإيصال اتساق لا توقيع.

## GT — نتيجة G5 Particle108 resource census | 27 نوفمبر 2026

[45938971358](https://github.com/alwansan/raf/actions/runs/45938971358) ناجح؛ job 140308763652، رأس 7a42c79f4fdad26e1231ccd7b01e8c8c6005ad43، وحارس [45938971386](https://github.com/alwansan/raf/actions/runs/45938971386) ناجح. ربط rebind_stage بفاحص التصريحات الصارم المشترك مع حفظ annotations ورفض التصريحات غير المدعومة حتى مع samplers سليمة. 50 اختباراً ناجحاً (37 Particle108 +10 resource +3 depth)، 7 glslang و7 spirv-val و7 normalizations فعلية. تطابق SPIR-V stripped للثلاث حالات bare/space0/comment قبل/بعد الربط. 6 ضوابط مرفوضة، بينها زوج مورد خاطئ صالح للترجمة، space1، texture غير مسجل، descriptor array، فئة خاطئة، slot مكرر. الأرشيف الخام clients/GT/sessions/20261127-particle108-resource-census/actual-run-45938971358.zip (3042 bytes، SHA256 308b44f7731087a60872f340b207cc5e0894c49401f618c4e27d097ea6fd5115)؛ تحقق محلي من CRC والحجم والبصمة وقراءة تقرير المترجم وسجلات الاختبار، clients/GT/sessions/20261127-particle108-resource-census/evidence.json. لا DXBC/RDEF أصلي فعلي، لا Unity/Android pixels ولا إصلاح مثبت للنار أو الأبيض في اللعبة.

**التالي:** G5-Particle108-material-alpha-provenance — مراجعة أصل alpha/texture pointers/blend للنار وParticle108، وخاصة local type-0، وتكافؤ الموارد والمواد البيضاء؛ إصلاح عيب ملموس واختبار falsification مؤلف. لا تكرر الاختبارات الناجحة بلا سبب جديد. A3 معلق حتى إثبات تصريح المصدر الأصلي؛ G0–G6 مفتوحة؛ الأرقام التاريخية 688/786 non-dummy، 98 dummy، 37 GUID لا تتغير بلا census فعلي. لا XAPK أو اختبار هاتف جزئي؛ لا اقتناء أصل أو LFS؛ CL والمختبر قراءة فقط، BLACK خارج النطاق، الأنيميشن مؤجل. لا checkout قديم محلي؛ أرشيفا الجلسة السابقة محفوظان ولم يتغيرا. جميع التعديلات على feature/android-native-port، لا force push. تحقق من HEAD وActions أولاً عند الاستئناف.

---

## GT — G4 مرشح ربط إيصال FFT v2 | 27 نوفمبر 2026

رأس البدء 108898104496277005f559c11d9524089433f65b مطابق للرأس الحي، وActions45937731362 و45937731347 ناجحان. لا checkout قديم محلي؛ أرشيفا الأدلة السابقان باقيان. أضيف عقد source/Unity/bundle raw bytes وSHA256 وحجم المصدر والحزمة. منتج Unity يحسب البصمات قبل/بعد البناء ويشترط عدم تغير المصدر والإيصال. verifier الأصل يفك البايتات المتطابقة ويستخدم عقد Stereo المغلق وspirv-val لكل module، دون فرض شكل Sample/Fetch المؤلف على الأصل. source recovery يثبت Normal وempty routes، والمثبت يعيد فك الحزمة الفعلية ويطابق الإيصال الكامل قبل تعديل أي ملف. واجهة المثبت الجديدة تتطلب --bundle و--smolv-decoder؛ الإيصالات القديمة وحدها مرفوضة. هذا عقد اتساق، لا توقيع أو إثبات ملكية. لا أصل أو APK. **مرشح بانتظار اختبار فعلي**؛ لا ادعاء نجاح C# أو أصل. نحتاج اختبار مصدر مؤلف واحد للمنتج الجديد (ليس تكرار مقارنة المترجم) وفحوص regression، ثم حفظ النتيجة. A3 ما زال معلقاً. G0–G6 مفتوحة، لا هاتف/XAPK؛ أولوية الأبيض والنار، CL/المختبر قراءة، BLACK خارج النطاق.


---

## GT — نجاح بوابة FFT المؤلفة | 27 نوفمبر 2026

التشغيل [45937731362](https://github.com/alwansan/raf/actions/runs/45937731362) على d7a692d682c7e94510cbca5b9a46c2b771d233a8 اكتمل success، job 140304710592؛ حارس runner [45937731347](https://github.com/alwansan/raf/actions/runs/45937731347) ناجح. أعيد استخدام الحزمتين المؤلفتين المثبتتين فقط، من دون Unity جديد أو أصول لعبة. سبعة ممرات Normal وسبعة blobs و14 وحدة SPIR-V فريدة سليمة لكل حزمة (28 إجمالاً) و21 مرجع VS و21 FS لكل حزمة. أربع أسماء Stereo غير نشطة وflags صفر؛ جميع lanes الفعلية فارغة. 12 ضابطاً سلبياً لكل حزمة (24)، تشمل تغيير الحزمة والإيصال والمصدر مع بقاء الحجم، اسم مجهول، flags غير صفر، ثلاث lanes نشطة، غياب VS أو FS الفعلية، وتحوير إحداثيات Sample/Fetch في SPIR-V حقيقي؛ رفضت أربعة تحويرات بالمحقق. لم تتغير بوابة الأصل ولم يثبت حل خطأ FFT الأصلي.

الأرشيف الخام `clients/GT/sessions/20261127-fft-bundle-gate/actual-run-45937731362.zip` (3929 bytes، SHA256 eaed24f33f8f862a233a5612510aabaac0d9de17c77bbdaae948f4e5af7cde0b)؛ عضو gate.json (44100 bytes، SHA256 91e32402fa41ee6c9c259b66a6b49085db810c95f1ae3aa0be89fe36cee9caff). تحقق محلي من CRC والحجم والبصمات ومطابقة كل مراجع المراحل والوحدات لإعادة الفك 45936590347؛ لا ادعاء إعادة ترجمة محلية. حفظ الأرشيف في Git يمنع فقدانه بانتهاء artifact. بيانات الجلسة: clients/GT/sessions/20261127-fft-bundle-gate/evidence.json.

العمل التالي G4-FFT-original-receipt-provenance: مراجعة أظهرت أن FFTUtilitiesShaderValidation.cs ينتج candidateSha256 بلا بصمة وحجم الحزمة؛ gt_verify_921_shader_bundle.py يتحقق من candidate hash ونماذج التنفيذ دون تحقق spirv-val لكل الوحدات؛ gt_install_fft_utilities_original.py يربط ادعاءات الإيصالات بالمصدر لكن لا يربط bytes للحزمة والإيصال الفعليين. تقوية سلسلة الإيصالات الأصلية دون تخفيف الحواجز، وفصل عقد الممرات العام عن نمط Sample/Fetch المؤلف. A3 معلق لمصدر مأذون مثبت؛ لا جلب أصل، وإن تعذر انتقل إلى G5 النار والجسيمات أو المواد البيضاء. كل G0–G6 مفتوحة؛ لا هاتف أو XAPK.

## GT — G4 مرشح بوابة FFT المغلقة | 27 نوفمبر 2026

رأس البدء a6b97f5ab6ab2640f5fce24cfc368346d986f6e6 مطابق للرأس الحي، [مرجع المالك المثبت](https://github.com/alwansan/raf/blob/1a78eb2764d39550f59e2948ae5ed89033c8ab73/clients/GT/RESTORE_AR.md). [Replay45936590347](https://github.com/alwansan/raf/actions/runs/45936590347) ناجح، ليس قبول البوابة. البيئة الجديدة بلا checkout سابق ولا git network ولا Unity/spirv-val محلي؛ لا ملفات محلية حذفت، ولا إمكانية تدقيق غير المنشور من الجلسة القديمة.

مرشح scripts/gt_fft_bundle_gate.py يفصل أسماء Stereo الأربعة وflags صفر عن فهارس legacy/global/local الفعلية، يرفض أي اسم مجهول أو lane نشط قبل فلترة المراحل، ويشترط سبعة Pass Normal وVS/FS وspirv-val لكل وحدة مفكوكة وSHA/bytes. tools/synthetic_material_alpha/fft_bundle_gate_probe.py يقيد المدخلات بالأرشيفين المؤلفين المثبتين، يربط source/receipt/bundle، ويختبر مجهول/flags/active lanes/غياب المرحلة/تغيير نفس الحجم وحقن wrong coordinate في البرامج الفعلية. **مرشح ينتظر CI المعزول، لا نجاح جديد.** لم يتغير gate/installer الأصلي، ولا إثبات مصدر أصلي مأذون أو إصلاح خطأ FFT التاريخي.

عند Continue: تحقق من HEAD وActions ثم شغّل CPU-only على الأرشيفين دون Unity جديد، احفظ الإيصال والضوابط. إذا فشل أصلح السبب دون تليين العقد. A3 مشروط بمصدر مأذون؛ بعدها أقرب G4/G5 منتج. G0–G6 مفتوحة؛ 688/786 و98 Dummy/37GUID تاريخية. لا ZIP2 أو أصول أصلية أو XAPK أو هاتف؛ CL/المختبر قراءة فقط، BLACK خارج النطاق، الأنيميشن مؤجل، أولوية الأبيض والنار.


---

## GT — G4: نتيجة تشخيص FFT Utilities والبوابة الفعلية | 27 نوفمبر 2026

راجعنا [الفشل التاريخي44781701884](https://github.com/alwansan/raf/actions/runs/44781701884)، job136445781719، وتقرير الأنواع القديم (6 sample float و0 integer في الأصل/roundtrip) وإيصال HLSLcc المحلي الذي لا يثبت Unity. فحص أنماط سجل الفشل أعاد تشخيص Expected Coordinate to be float scalar or vector مرة واحدة في gt_fs_main، بلا رقم pass موثوق؛ لم نحتفظ بمحتوى خاص. لا جلب ZIP2 أو أصول اللعبة أو برامجها. أُنشئت 7 ممرات مؤلفة: 6 Sample/SampleLevel (float، swizzle، bitcast، signed/unsigned numeric conversion) وLoad واحد integer. استدعينا attach_programs وcompiler_control من كود الإنتاج عبر AST المحدود، وفرق المرشحين 7 pragma فقط. لم نغيّر تعبيرات الأصل أو gate الإنتاج.

[المقارنة45935871773](https://github.com/alwansan/raf/actions/runs/45935871773) على الرأس 5b6f8f21627269d946aa549cd7055384914cdf82: **failure في النتيجة الكلية**، لأن الفاحص strict zero_keywords رفض جدول الأسماء بعد نجاح مرحلتي Unity2021.3.45f2 Android Vulkan AssetBundle (DXC pragma / HLSLcc-default، job140298837257 و140299709457، 7Pass، 1 SVC، errors0، bundle حقيقي). لا ندعي attestation مستقل لمسار المترجم الداخلي من اسم الوضع. CPU: 14 glslang/val لكل وضع (28 إجمالاً)، الإيصال متطابق بالبايت. تبديل operand لنوع إحداثيات خاطئ عمداً أعاد رسالة Sample التاريخية ورفض Fetch float؛ أربع عمليات رفض إجمالاً. **لم يعاود Unity نفسه إنتاج خطأ الإحداثيات في العينتين**. لا تحويل شامل، لا إصلاح مؤكد للسبب الأصلي. [الإيصالات الخام](sessions/20261127-fft-coordinate-diagnostic/cpu.json)، [DXC](sessions/20261127-fft-coordinate-diagnostic/dxc-unity.json)، [HLSLcc](sessions/20261127-fft-coordinate-diagnostic/hlslcc-unity.json)، [مراجعة الأرشيفين](sessions/20261127-fft-coordinate-diagnostic/artifact-review.json). بصمات ZIP والأعضاء وCRC متحققة محلياً؛ جسم الشيدر مطابق بعد إزالة pragma.

[Replay45936590347 SUCCESS](https://github.com/alwansan/raf/actions/runs/45936590347)، job140301098539، على الرأس `e79e09151def7abe680b03dc230cdff9ff41b27e`، CPU-only، قرأ فقط الأرشيفين المؤلفين artifact15171100631 و15170637402 ببصمتيهما. لا Unity جديد. UnityPy1.23.0 وSMOL-V وspirv-val Vulkan1.1 وspirv-dis فكوا **14 module فريداً لكل حزمة (28 مجموع العدّين)** و7Pass VS/FS في كل وضع؛ 21 fragment reference لكل وضع، صفر invalid module وصفر wrong image family. كل الممرات في الوضعين لها empty route pair، ولا أي keyword indices مستخدمة في أي lane. في جدول الأسماء المتسلسل توجد 4 أسماء Stereo: STEREO_INSTANCING_ON، UNITY_SINGLE_PASS_STEREO، STEREO_MULTIVIEW_ON، STEREO_CUBEMAP_RENDER_ON؛ flags=[0,0,0,0]، used=[]، جميع route_keys=[[]]. لذلك شرط جدول الأسماء الفارغ الحالي يرفض هاتين الحزمتين رغم صلاحية البرامج وعدم استعمال أي اسم. لا تعميم لهذا إلى الأصل أو السماح لأي اسم غير معروف/مستخدم؛ البوابة الأصلية بقيت دون تغيير. هذا كشف خلل محدد في شرط قبول الحزم المؤلفة، **ليس إصلاح FFT الأصلي**.

[أرشيف التشخيص الكامل المحفوظ](sessions/20261127-fft-coordinate-diagnostic/actual-replay-45936590347.zip) حجمه3561B SHA256 `5bd5ce19f2cf64bc16ee09cd2b8f2434c7b92c1317f54de076eef3db6a93f95e`، العضو diagnostic.json (63206B) SHA256 `9eafaf0a84a04a85183b0b4a53396be2fd7ffa8fa4f7d95894f5c0bfb92b9a21`. تحقق CRC وبصمات الحزمتين ومطابقة كل صف/موديول محلياً، لم نعد فك الحزمة أو ترجمتها محلياً. أرشيفا الحزمتين الخام موجودان في Actions إلى 11 ديسمبر، الإيصالات والبصمات وأدوات التوليد والفحص والأرشيف التشخيصي مثبتة في Git لاستعادة النتائج وإعادة بناء العينة بعد انتهاء المرفقات. حارس runner45935871899 و45936590335 ناجحان. 131 ملفاً محلياً سابقاً بقيت مطابقة؛ لا clone كامل.

| البند | الحالة |
|---|---|
| A1/A2 وG2 | نتائج مؤلفة موثقة فقط |
| A3 | معلق على مصدر أصلي مأذون |
| G4 تشخيص الإحداثيات | مكتمل في النطاق المؤلف، لم يُعد إنتاج خطأ Unity الأصلي |
| G4 تقوية بوابة FFT | التالي النشط، ضوابط أسماء غير مستخدمة وSPIR-V وارتباط الإيصال |
| بقية G0–G6/A4/A5 | مفتوحة |
| A6 XAPK | محظور حتى الدمج الكامل |

**عند Continue:** البند النشط G4-FFT-bundle-gate. قوِّ البوابة بشكل محدود ومغلق عند الغموض: افصل أسماء Stereo الأربعة المعروفة غير المستخدمة عن المسارات الفعلية ذات indices فارغة، مع إثبات مصدر مأذون/طوبولوجيا، وإثبات أسماء/flags، والتحقق الفعلي لكل SPIR-V مفكوك والتزام SHA/bytes للإيصال والحزمة. اختبر على الحزمتين الموجودتين وضوابط unknown/active keyword، missing stage، نفس الحجم مع بايت مختلف، wrong coordinate. لا تُخفف البوابة الأصلية أو تغيرها بلا الأدلة والضوابط، ولا تعتبر التشخيص إصلاحاً للخطأ التاريخي. بعد ذلك انتقل إلى أقرب إصلاح G4/G5 أو A3 عند مصدر مأذون؛ لا تعيد Unity المؤلف نفسه بلا سبب. جرد 688/786 Custom و98 Dummy/37GUID تاريخي دون تغيير. G0–G6 مفتوحة، لا بكسلات لعبة/Android، لا XAPK ولا هاتف جزئي، الأنيميشن مؤجل، CL والمختبر للقراءة فقط، BLACK خارج النطاق.

---

## GT — G2: نجاح مسار metadata إلى Unity/Vulkan بالبكسلات المؤلفة | 27 نوفمبر 2026

[Run45934006734 SUCCESS](https://github.com/alwansan/raf/actions/runs/45934006734) على الرأس المثبت `e867b31791ca00c58108ce2d3ea3933aee5234a2`، job140292902788. تحقق جديد فعلي: أُعيد فك ParameterBlob مؤلف واستخدام stage_parameter_records وrebind وتطبيع التسجيلات ودمج VS/FS؛ 14 glslang compile و14 spirv-val Vulkan1.1 و10 spirv-opt، أربع مقارنات قبل/بعد إعادة الربط. **ناتج combined.hlsl الفعلي (596B)**، نفسه من bare وspace0، غُلّف في ShaderLab بدون تغيير جسمه. SHA256 الشيدر 1087B: `bbac74071676cec0867db4d3dfab35c9107475f36e6de8babab129c0c093c473`. 18/18 اختبارات CI (10 موارد +3 depth +5 oracle). لا مصادر لعبة، فحوص CB/mesh/varying غير المتعلقة بالموارد بقيت ببدائل معلنة. تعديل resource_register_probe.py أضاف source_factory وcombined_out اختياريين، بقي المسار الافتراضي السابق.

Unity **2021.3.45f2 Linux/Vulkan Linear llvmpipe** استورد الشيدر الفعلي، وربط _MainTex مع sampler_MainTex عبر Material API مع _OldTex decoy. ثماني حالات 4×4، **128 بكسلاً و512 RGBA بأقصى خطأ0**. علامة R تعتمد على Vertex SampleLevel مستقلة، وG/B/A على Fragment Sample، مع straight-alpha فوق خلفية ثابتة. تحقق Point/Bilinear وClamp/Repeat وتبديل A/B ثم A دون بقايا من B، وwhite/decoy substitutes صريحة. ألفا صفر تحفظ الخلفية، والجزئية تمزجها، والكاملة تعرض المصدر. سبع مقارنات رقمية مع نتائج خاطئة (أصغر قيمة لأقصى فصل0.09375)، وليست سبع حقن عطل في المحرك. ليست تجربة فقدان texture أصلي أو قبول إصلاح النار أو المجسمات البيضاء في اللعبة.

[الأرشيف الفعلي الكامل](sessions/20261127-resource-pixels/actual-run-45934006734.zip) (4911B، SHA256 `f4c4fdd5a55d9745017ada7fcf6a8a34ec41b02d79bed80df3a65bd2e4271624`)، [إعادة الحساب](sessions/20261127-resource-pixels/artifact-review.json)، [أداة الإعادة](sessions/20261127-resource-pixels/review_resource_pixels.py)، [جلسة التنفيذ](sessions/20261127-resource-pixels/README_AR.md). طابقنا بصمة GitHub وCRC والأعضاء الستة، وأعدنا حساب جميع البكسلات من الإيصال الخام، وتطابق التقرير مع runner. 2514 سطر log فُحصت بأنماط C# errors وshader errors وTraceback فكانت العدادات0 (لا ادعاء شمول كل أخطاء/تحذيرات). فحص runner guard45934006683 ناجح، أوضاع الاختبار الأربعة الأخرى skipped عمداً. 26 ملفاً محلياً سابقاً بقيت مطابقة. لا Unity أو glslang محلياً، لا clone كامل؛ الاختبار التنفيذي كان Actions، والإعادة المحلية رقمية فقط.

| البند | الحالة |
|---|---|
| A1/A2 | مكتملان ضمن الحزمة والبكسلات المؤلفة فقط |
| A3 | معلق على مصدر مأذون |
| G2 metadata/ربط الموارد | مكتمل ضمن compiler + Unity Linux/Vulkan المؤلف |
| G4 FFT Utilities | البند التالي النشط؛ عزل خطأ الإحداثيات وإصلاح محدد عند ثبوته |
| A4/A5 وبقية G0–G6 | مفتوحة؛ الدمج الأصلي غير مثبت |
| A6 | XAPK محظور قبل إغلاق الاستعادة والدمج |

**عند Continue:** راجع الرأس وActions والبصمات. اكتملت بوابة G2 المؤلفة من metadata إلى البكسلات؛ **لا تكررها بلا سبب**. A3 الأصلي ما زال معلقاً على مصدر مأذون مثبت. انتقل إلى G4/FFT Utilities: اقرأ الحالة الأحدث لـHLSLcc/DXC والأدلة، اعزل خطأ gt_fs_main التاريخي Expected Coordinate to be float scalar or vector (44781701884) على HLSL/SPIR-V مؤلف، ميّز Sample/SampleLevel عن Load، واختبر بالمترجم الحقيقي وUnity ضمن التفويض. لا تحويل شامل للأنواع ولا ادعاء إصلاح الأصل إذا لم يُعد إنتاج الخطأ. إذا تعذر، وثق السبب واختر أقرب إصلاح مأذون من G4/G5. لا تخمّن kernel6. تابع A3/الدفعات العشر عند توفر مصدر مأذون، وكل G0–G6 قبل XAPK. الجرد التاريخي 688/786 Custom و98 Dummy/37GUID دون تغيير. لا قبول لعبة/Android، لا هاتف جزئي، الأنيميشن مؤجل. CL والمختبر للقراءة فقط، BLACK خارج العمل.

---

## GT — دمج إصلاح G2 للموارد وتحقق فعلي من SPIR-V | 27 نوفمبر 2026

A1 وA2 تبقيان ناجحتين في نطاقهما المؤلف. راجعنا A3 وملفات ZIP2 وقرار المالك: وثائق النقل والبصمة لا تثبت وحدها حقوق استعمال الأصول الأصلية. **لم نجلب الأصل**، وA3 يبقى مشروطاً بمصدر مأذون. اتبعنا الخطة بالانتقال إلى إصلاح G2 فعلي في الكود المشترك، لا إعادة اختبار route0.

أضيف `scripts/gt_resource_register_contract.py` وربط بأربعة ملفات إنتاج: `w1_rebind_depth_resources.py` و`gt_original_921_resource_rebind.py` و`gt_original_921_all_variants.py` و`gt_original_921_shaderlab.py`. يدعم register العادي وspace0 ويحفظ مجموعات RESOURCE الأربع، ويرفض nonzero spaces والتكرارات الملتبسة. يمنع dict overwrite الصامت داخل كل metadata lane ويحتفظ بأولوية variant على common. تُحفظ أرقام التسجيل المترجمة عند إعادة الأسماء ثم تُزال في تطبيع Unity؛ لا تخمين من ترتيب descriptor. القارئ محدود بنصوص HLSL المترجمة، لا descriptor arrays أو UAV أو macro-expanded HLSL.

[Run45932314286 SUCCESS](https://github.com/alwansan/raf/actions/runs/45932314286) على الرأس `a02b194c82abab1344101f2efaabf5a600a3fb48`، job140287488334. 10/10 اختبارات جديدة +3/3 legacy depth، **14 ترجمة glslang فعلية و14 تحقق spirv-val Vulkan1.1 و10 spirv-opt** (تشمل حالة رفض برنامج مختلف). أربع مقارنات موجبة قبل/بعد إعادة أسماء Texture/Sampler متطابقة بعد strip-debug، وملف HLSL المدمج VS/FS للصيغتين مطابق بالبايت (501B) وبرنامجا المرحلتين متطابقان بالبصمات. فُك ParameterBlob مؤلف حجمه72B بالقارئ الفعلي واستُدعيت stage_parameter_records كاملة لمسار الموارد، مع بدائل اختبار معلنة لفحوص CB/mesh/varying خارج النطاق. رُفضت نسخة SPIR-V صحيحة لكنها تغير sampling، ورفض حالتا space1/missing sampler. **لا Unity أو بكسلات Android جديدة**.

[التشغيل الأول45932233741](https://github.com/alwansan/raf/actions/runs/45932233741) فشل عند جمع tool version في stdout (النسخة طبعت إلى stderr)، لا إيصال نهائي؛ حفظنا الفشل ولم نحسبه نجاحاً. أُصلح التسجيل فقط ثم نجح التشغيل الثاني. فحص توافق runner45932233934 نجح. لا أصل/أسرار/تنشيط Unity/حزمة؛ الاختبار CPU معزول. [الأرشيف الخام](sessions/20261127-resource-register/actual-run-45932314286.zip) (2029B، SHA256 a7fe89aa4875ba343f2afb72642214d094f1cbcb34a3cae65dc979e0cd37a95f) و[إعادة الفحص](sessions/20261127-resource-register/artifact-review.json) و[جلسة التنفيذ](sessions/20261127-resource-register/README_AR.md). تحقق CRC والأعضاء الثلاثة وتطابق الإيصال، لم تُعد الترجمة محلياً. لا clone كامل؛ جرد 17 ملفاً من A2 والأرشيف الخامس المحلي بقي مطابقاً. لا اعتماد على sandbox.

| البند | الحالة |
|---|---|
| A1 | مكتمل للحزمة المؤلفة فقط |
| A2 | مكتمل لبكسلات Linux/Vulkan المؤلفة فقط |
| A3 | معلق على إثبات توفر مصدر مأذون |
| G2 — إصلاح تسجيلات الموارد | مكتمل لبوابة metadata/SPIR-V المؤلفة؛ اختبار Unity عبر المسار الجديد التالي |
| A4/A5 | استعادة المواد وبقية G0–G6 مفتوحة |
| A6 | لا XAPK قبل إغلاق الاستعادة والدمج |

**عند Continue:** افحص HEAD وActions والبصمات. A3 لا يزال معلقاً حتى توفر مصدر أصلي مأذون مثبت؛ لا تخمّن نطاق الكلمات أو تستنتجه من العينة. إن لم يتوفر، أكمل G2 بتجربة Unity Vulkan فعلية تمرر shader مولداً من مسار metadata/rebind الجديد وتتحقق من اختيار Texture/Sampler باسم المادة وقراءة البكسلات، لا تكرر fixture ألفا القديم دون مسار الدمج الجديد. بعد ذلك انتقل إلى أقرب إصلاح من G4/FFT/Foam/Depth أو G5 المتاح، ثم استعادة المواد الأصلية والدفعات العشر عند توفر المصادر المأذونة. لا قبول للأبيض أو النار حتى اللعبة الفعلية، ولا تغيير في الجرد التاريخي 688/786 Custom و98 Dummy/37GUID. G0–G6 مفتوحة، الأنيميشن مؤجل، CL والمختبر للقراءة فقط، BLACK خارج العمل، لا XAPK ولا هاتف جزئي. خطة الحالة الآلية وذاكرة GT محدثتان.

---

## GT — A2 مكتملة ضمن الاختبار المؤلف الفعلي | 27 نوفمبر 2026

تفويض المالك المستمر لاستخدام GitHub Actions محفوظ؛ لا تتوقف عند غياب Unity المحلي. [تشغيل 45931001072 SUCCESS](https://github.com/alwansan/raf/actions/runs/45931001072) على الرأس المثبت `50332d816ac2bc5a8f92e84a0991f9bffde6a0a8`، job 140283349151، Unity 2021.3.45f2 Linux/Vulkan Linear، llvmpipe. شغّلنا مرشح strict_engine_router في شيدر مؤلف من أربعة مسارات (Global وLocal)، ومادتين. **15 حالة، 360 بكسلاً، 1440 مركبة RGBA، أقصى خطأ 0**. المجموعة الفارغة route3، وroute0 يحتوي الكلمتين. لاحظنا فعلياً كل المسارات الأربعة، علامة Vertex في R وعلامة Fragment في G وعلامة المادة في B؛ global_overridable=true وlocal_overridable=false. تفعيل الاسم المحلي ككلمة Global لا يفعّله في المادة الثانية، وتغيير local أو material-global لا يسرب إلى المادة الأخرى. خمس مقارنات بمسارات خاطئة، أصغر فصل 0.125؛ ليست خمس عمليات حقن عطل في المحرك.

[جلسة الدفعة](sessions/20261127-keyword-pixels/README_AR.md)، [الأرشيف الفعلي المحفوظ داخل Git](sessions/20261127-keyword-pixels/actual-run-45931001072.zip)، [إعادة الحساب](sessions/20261127-keyword-pixels/artifact-review.json)، [الأدلة](sessions/20261127-keyword-pixels/evidence.json). SHA256 ZIP `e302694238bf4a5f95d904904ae169adbd840894124c1b6eda245811a8f2867b`، 3191 بايت، CRC والأعضاء الثلاثة صحيحة. أعدنا حساب كل البكسلات محلياً من إيصال Unity الخام وطابق الناتج إيصال runner، لا اعتماد على رابط مؤقت. 5/5 اختبارات المصدر محلياً وCI؛ فحص cpp لأربع علامات منفصل. فحص أنماط محددة في 2425 سطر log أعطى 0 C# errors و0 shader errors و0 wrong-route exceptions؛ لا تعميم لمسح كل التحذيرات. فحص توافق runner 45931001106 ناجح. وضعا alpha وnext23b-receipt skipped عمداً، لا تكرار أو إلغاء.

**النطاق:** قبول A1 السابق للحزمة المؤلفة Android Vulkan منفصل عن A2 الجديد لرسم Linux Vulkan المؤلف؛ لم يثبت اختيار كلمات أو برامج اللعبة الأصلية ولا بكسلات Android أو إصلاح الأبيض/النار. جرد SAME-EXPORT التاريخي 688/786 Custom و98 Dummy/37GUID دون تغيير، G0–G6 مفتوحة. لا XAPK ولا هاتف جزئي. CL والمختبر للقراءة فقط، BLACK خارج العمل. الأنيميشن مؤجل. لا أصول أصلية جُلبت ولا أسرار أو تراخيص نُشرت.

| البند | الحالة الحية | شرط القبول |
|---|---|---|
| A1 | مكتمل للحزمة المؤلفة فقط | 45929964298 |
| A2 | مكتمل لبكسلات Linux/Vulkan المؤلفة فقط | 45931001072 + إعادة حساب 360 pixel |
| A3 | التالي النشط، مشروط بمصدر مأذون | أصل الكلمات/النطاق والممرات والبرامج واختيار runtime، ثم SAME-EXPORT |
| A4 | مفتوح | الدفعات العشر وجرد فعلي جديد بلا Dummy |
| A5 | مفتوح | إغلاق G0–G6 والدمج الكامل |
| A6 | محظور حتى A5 | XAPK النهائي المتحقق ثم اختبار نهائي |

**عند Continue:** A3 هي البند التالي: تحقق من الرأس وActions والبصمات، ثم من وجود بيانات NEXT23b مأذونة فعلاً وإثبات scope/PassType والـlattice وارتباط VS/FS من دليل مستقل. لا تستنتج النطاق الأصلي من A2 أو تفترض أن إذن Actions يجيز أصولاً أخرى. استخدم Actions المعزول ضمن التفويض؛ إن لم تتوفر بيانات المصدر المأذون، سجل العائق المحدد وانتقل لأقرب عمل أصلي/مؤلف منتج من G0–G6 بدل تكرار البوابة الاصطناعية. ثم إثبات ربط المواد وGUID وSAME-EXPORT وتعميم الدفعات العشر؛ تابع الماء وFFT/Foam/Depth والمجسمات والنار والموارد وبقية G0–G6، لا XAPK قبل الاستعادة والدمج. خطة الحالة الآلية وذاكرة المشروع محدثتان.

---

## توجيه المالك الحي — 27 نوفمبر 2026: استخدام GitHub Actions والاستمرار بالخطة

**أذن المالك باستعمال GitHub Actions لأي تجربة لازمة ضمن RAFT، وطلب حفظ التفويض في الذاكرة وتحديث الخطة ومتابعتها باستمرار.** في كل استئناف تحقق من الرأس وActions، نفّذ أقرب خطوة منتجة من الخطة، استخدم التجارب الفعلية المأذونة عند غياب Unity المحلي، لا تكرر أو تلغِ تشغيلات قائمة، واحفظ الأدلة والنتائج والعوائق. التفويض لا يجيز تجاوز حقوق الأصول أو التراخيص أو كشف أسرار. الكتابة فقط على feature/android-native-port، CL والمختبر للقراءة فقط، BLACK خارج النطاق، لا LFS أو أصول غير مصرّح بها. الأنيميشن مؤجل، لا اختبار هاتف جزئي أو XAPK قبل إغلاق G0–G6 ودمجها فعلاً.

### أحدث نتيجة متحققة

[Actions45929964298 SUCCESS](https://github.com/alwansan/raf/actions/runs/45929964298) على الرأس المثبت `1fd0565f8f7cb926a5d9143f3216e88ba31c70b5`، job 140280068547: Unity **2021.3.45f2** نفذ مرشح C# فعلياً، checkpoint=verified وإيصال schema2، صفر Shader errors، 4Pass، 1156 route مسجلة، Android Vulkan AssetBundle حجمه 48,712 بايت. UnityPy 1.23.0 فك الحزمة الفعلية على runner، وفاحص VS/FS وSMOL-V/SPIR-V تحقق من [512,4,128,512] لكل مرحلة، 4 وسوم و27 flag متغيراً، ورفض تبديل الحزمة بنفس الحجم وملف الكلمات. لا دليل أن كل برنامج يختار بكسله وقت التشغيل ولا إثبات scope/مواد اللعبة. فحصنا 2166 سطر سجل نهائي بأنماط الأخطاء المعينة وكانت جميع عداداتها صفر؛ لا ادعاء مسح لكل الأخطاء المحتملة.

نزّلنا artifact 15168725743 وتحقّقنا من SHA256 `8014480263c86c25f589950052a0abce81a0a473165e9633a73dce6b9575ee1c` وCRC و8 أعضاء، وتطابقت ملفات الشيدر/الكلمات/المصدر المؤلف المحلية بالبايت. أعدنا محلياً فحص إيصال البايتات وعقد المصدر على الناتج الفعلي؛ لم نعد فك UnityPy/SPIR-V محلياً. [الإيصال الخام](sessions/20261127-actions-execution-plan/gt-next23b-unity-safe.json) و[البوابة الكاملة](sessions/20261127-actions-execution-plan/full-verified.json) و[بصمات الأرشيف](sessions/20261127-actions-execution-plan/artifact-review.json) و[جلسة التنفيذ](sessions/20261127-actions-execution-plan/README_AR.md). الأرشيف المؤلف في Actions ينتهي 11 ديسمبر؛ الإيصالات الخام وأداة التوليد والتحقق مثبتة في المستودع لإعادة التشغيل دون sandbox. فحص CPP المحلي المستقل للشيدر المؤلف نفسه: 1156 اختياراً/2312 علامة VS/FS، المجموعة الفارغة ليست route0.

### ترتيب التنفيذ الحي

| المرحلة | الحالة | شرط الانتقال |
|---|---|---|
| A1 Unity NEXT23b مؤلف | **مكتملة ضمن الحزمة المؤلفة فقط** | run45929964298، الإيصال والحزمة وفحص VS/FS وسجل نهائي |
| A2 اختيار route وقت التشغيل | **الخطوة التالية النشطة** | Unity Vulkan material/global/local keyword pixel readback مع empty route غير 0 وضوابط إيجابية وسلبية |
| A3 NEXT23b الأصلي | معلق على المصدر المأذون | scope/PassType/VS-FS ثم Unity/GUID/SAME-EXPORT |
| A4 الدفعات العشر/المواد البيضاء والنار | مفتوح | اختيار أصلي مثبت وجرد فعلي جديد بلا Dummy بديل |
| A5 G0–G6 | مفتوحة | الاستعادة والدمج الكامل لكل البصريات |
| A6 XAPK النهائي | محظور قبل A5 | الحزمة الكاملة الموثقة والمتحققة ثم تجربة نهائية |

آخر SAME-EXPORT تاريخي 688/786 Custom و98 Dummy/37 GUID. لا زيادة من نجاح حزمة مؤلفة. لا XAPK جديد. خطة الحالة الآلية في current_handoff؛ النصوص التالية تاريخية، والوقف السابق تجاوزه تفويض المالك الجديد.

---

> **نقطة التسليم الشاملة — 26 نوفمبر 2026:** ابدأ من [رسالة الاستعادة](RESTORE_AR.md) و[حزمة الأدوات والنتائج والخطة](sessions/20261126-complete-handoff/README_AR.md). السجل أدناه تاريخي؛ الاستعادة الكاملة وruntime keywords وUnity/GUID/device ما زالت غير مكتملة. طلب هذه الجلسة هو الحفظ والنشر فقط.

# GT — الخطة الحيّة لاستعادة رسوميات Raft Android

## تنفيذ الخطة الحالي

ابدأ من [تسليم استعادة الرسوم](sessions/20261115-graphics-restoration/) و[نقطة الاستعادة](RESTORE_AR.md). أحدث [حالة وفحوص](sessions/20261115-graphics-restoration/02-STATUS_AND_TESTS_AR.md) و[خطة استكمال](sessions/20261115-graphics-restoration/01-PLAN_AR.md) تحدد ما نُشر وما بقي، وتقدّم على الحالة التاريخية أدناه.

## ملحق Chat-33 — بيانات Keywords/Properties المصدرية مكتملة الجرد لا الربط

[CI43358489426 SUCCESS](https://github.com/alwansan/raf/actions/runs/43358489426): 74 original VS/FS variant records، 27 Keyword names/flags، 14 فهرس Keyword مستخدم ومتحقق ضمن نطاق الأسماء، 35 Shader Properties، player bucket واحد، مع بقاء ترجمة 58/58 صحيحة. أصل بيانات ParsedForm والـPass States محفوظ مؤقتاً فقط وملف المشروع لم يتغير. **ما زال P05 مفتوحاً** حتى يثبت Original ShaderLab الكامل وربط التهيئة/الـCB0/الـSampler والـGUID. **P04 770 Dummy ما زال مفتوحاً**، ثم الموارد الباقية إلى G0–G6 قبل XAPK.

---

## GT Chat-33 — 58/58 Shader48 برامج أصلية مستعادة إلى مرحلة HLSL/Vulkan المصدرية

نجاح فعلي [CI43357332292](https://github.com/alwansan/raf/actions/runs/43357332292): المصدر SHA ZIP2، 6 مشاهد، 4 Shader owner، **4 Pass/33 paired VS-FS variants/8 unmatched VS/58 distinct DXBC**؛ 58/58 أصلية صالحة Vulkan1.1، و58/58 HLSL recovered، و58/58 round-trip Vulkan1.1. كتبنا أدوات إعادة الاستعادة الآمنة وأُجري الاختبار الحقيقي؛ **المرحلة المصدرية مكتملة لهذه العائلة فقط**. لم يُنجز Full Original ShaderLab/Keyword/CB0/Sampler/Renderer GUID restore ولم يُقلَّص تعداد 770 Material Dummy الإنتاجي بعد، ولا يوجد Unity Editor/Android pixel proof. **التالي P05→P04:** تجميع ShaderLab بأربع Passes وجميع variants، تثبيت original-same-export GUID دون لمس .meta، توثيق خصائص Keyword/Sampler/CB0 ثم إعادة الفحص لمستندات الـ770، بعدها معالجة بقية الـ165 Shader والماء وFFT والموارد وصولاً إلى G0–G6. **XAPK مؤجل حتى اكتمال الاستعادة والدمج**. [جلسة Chat33](sessions/20261113-GT-original-921-complete-source-variant-stage-chat-33.md).

---

## GT Chat-32 — جرد ZIP2 الأعلى أثراً والمهمة التالية استعادة Shader48 كاملاً

اتفاق المالك: **جميع الموارد تستعاد وتُدمج قبل أي XAPK تجريبي شامل**. نُفذ [CI43354787983 SUCCESS](https://github.com/alwansan/raf/actions/runs/43354787983) لتحديد أولويات P04/P05 من source SHA فعلي: 17 Shader48 Dummy من أصل 21 Shader48 في 6 مشاهد، تؤثر في 1373 من أصل 1633 Renderer Material slot؛ **الأعلى يستخدم 921 خانة**. هذا لا يمثل 770 مستند مادة (جرد أكبر) ولا 770 شيدراً مختلفاً ولا draw calls. أصلحت GT أدوات الربط SHA W1/B02/B21 [CI43354701952 SUCCESS](https://github.com/alwansan/raf/actions/runs/43354701952) وأنشأت قائمة خاصة تتضمن Source→Export GUID لا تخرج من runner. **الهدف الفعلي التالي:** استعادة الشيدر الأعلى بكل بياناته الأصلية (4 Passes و33 زوج Variant متطابقاً و8 Vertex variants غير مقترنة) وترجمة كاملة بقبول المصدر والـShaderLab والـMeta ثم اعمل جرد Dummy جديد وكرر على بقية عائلات الـ165 Shader. **ممنوع اعتبار فحص الجرد استعادة ناجحة للبرامج ذاتها**. [Chat32](sessions/20261113-GT-owner-restore-everything-before-XAPK-chat-32.md).

---

## أولويات المالك الملزمة 2026-11-13: استعادة كل شيء قبل XAPK

تغيّر ترتيب المشروع رسمياً: **المهمة الأساسية الآن الاستعادة الأصلية والدمج الكامل**، وليس إصدار XAPK أو قياس Adreno. اقرأ [قرار المالك الكامل](OWNER_DIRECTIVE_RESTORE_FIRST_AR.md). تعالج GT أولاً 770 مستند Material ذات Dummy (ولا تعتبرها 770 شيدراً مختلفاً)، وتستعيد 165 Shader ببرامجها/Keyword/Sampler، ثم الموارد الأخرى مجسمات/أنيميشن/Texture2D/Texture2DArray/Mip/الألوان والماء FFT/Compute/Depth/Foam/الظلال والنار والجسيمات وPostFX. ترتيب القرار ومقاييس G0–G6 محفوظة أيضاً في `RESTORATION_PLAN.json`. **M1/M5 الآن مؤجلان لمرحلة التوافق النهائية**، ولا تفتح اختبارات XAPK إلا بعد إزالة جميع النواقص الأصيلة أو إقرار المالك بقيود مثبتة. الطلبات الأقدم [43349181838](https://github.com/alwansan/raf/actions/runs/43349181838) و[43350559665](https://github.com/alwansan/raf/actions/runs/43350559665) لا تُعتبر إعلان بدء الاختبار الجديد؛ لا تشغل بديلاً عنهما الآن. الاستعادة الفعلية والحراسة المصدرية كل جلسة أولاً.

---

## GT Chat-31 — فصل إنجاز Spectrum عن أخطاء Depth/Compute وطلب التجربة

P06 تحقق فعلياً في [Native43346405263](https://github.com/alwansan/raf/actions/runs/43346405263): **Spectrum الأصل 7Pass أُدخل في مشروع AssetRipper مع `.meta`/GUID محفوظين**؛ لم يصل إلى Unity Editor GPU لأنه توقف عند `Authentic water gate`. السبب: `record_documented_water_limitation` رفض شرط Spectrum القديم الموثق مع أنه أصبح PASS. تقرير المشاريع الحقيقية يثبت Spectrum `[7]`، Foam القديم `[1]`، Depth `[6,3]` (الثاني أقل من 4)، Blur `[2]`، Volumetric `[5]`، Water Compute مرشح غير موجود وهوية Kernel غير مثبتة. شرط الفشل موثَّق بدقة وليس Shader compile failure. تم إنشاء fixture الاختبار مع Foam2/Depth6+3/لا Compute في [CI43350378817 SUCCESS](https://github.com/alwansan/raf/actions/runs/43350378817). تم إرسال بناء [43350559665](https://github.com/alwansan/raf/actions/runs/43350559665) جديد بثلاث قيود تجريبية مطابقة للأدلة المتوقعة دون تمرير ادعاء original water كاملة. البناء [43349181838](https://github.com/alwansan/raf/actions/runs/43349181838) ما زال يعيد المشروع مع Spectrum/Foam ومراقب. تحقق من CI قبل قبول أي APK؛ الأصل والـCB0 والسامبلر وFFT و770 Dummy والهاتف ما زالت مفتوحة. [Chat31](sessions/20261113-GT-original-spectrum-foam-native-build-chat-31.md).

---

## GT Chat-30 — اشتراط ShaderUtil و7 Passes قبل تغليف Android

لمنع `Unity Build succeeded` الوهمي، أضيف في كود Native Builder الحالي شرط `GTOriginalWaterPassImportProbe.RequireOriginalSpectrumSevenPasses()` داخل Unity Editor. يرفض 0/2 shaders بنفس اسم Spectrum، أي passCount≠7، Dummy source، ملف غير آمن أو `ShaderUtil.ShaderHasError` true. [CI43347458130 SUCCESS](https://github.com/alwansan/raf/actions/runs/43347458130) اختبار C# صناعي وليس Compilation لملفات اللعبة. **لم يدخل Run43346405263 لأنه بدأ قبل هذا التعديل**. يجب أن يدخل طلب Native لاحقاً ثم تُفحص حزمة Android/Adreno نفسها؛ بقاء عدم إثبات P06/M2 كما هو.

---

## GT Chat-30 — مسار إنتاج Spectrum 7Pass الأصلي الآن داخل Native Unity

P06 انتقل من إثبات `Material→Graphics.Blit` الأصلي إلى **تنفيذ إعادة التركيب الخاص من ZIP2 داخل خط الإنتاج**: B09 original packet→original seven render states→source HLSL 2 variants/7 passes→single original keyword index4 route→ملف ShaderLab واحد بموضع AssetRipper الفعلي وGUID الموجود كما هو، مع backup خارجي ورفض duplicate shader/meta أو missing original name. كُتب [installer](../../scripts/gt_install_original_spectrum.py) و[CI43346292249 SUCCESS](https://github.com/alwansan/raf/actions/runs/43346292249) للاختبارات السلبية. [Full CI43346405263](https://github.com/alwansan/raf/actions/runs/43346405263) طلب بناء APK+OBB+XAPK أحدث، request/license preflight ناجح و`reconstruct` ما زال قيد التشغيل في هذه اللقطة. **P06/M2 device_verified=false** حتى اكتمال التصدير، ترجمة Unity الكاملة، وفحص الماء الحقيقي على الهاتف، ولا تزال Foam/FFT و770 Dummy وLOW_MEMORY مفتوحة. اقرأ [Chat30](sessions/20261113-GT-spectrum-production-original-guid-sevenpass-native-build-chat-30.md).

---

## GT Chat-29 — Source-original Spectrum Material إلى Graphics.Blit وLOW_MEMORY

سلسلة P06 المصدرية الآن تؤكد **الـMaterial الأصلي نفسه يصل إلى معامل `Graphics.Blit` في سبعة استدعاءات**، لا مجرد وجود Graphics مع ldfld في الدالة ([43343971412](https://github.com/alwansan/raf/actions/runs/43343971412)، [43344199792](https://github.com/alwansan/raf/actions/runs/43344199792) SUCCESS). 24 original Material field reads، 8 reader methods؛ stack/locals IL bounded single-block مغطى بالاختبارات السلبية. هذا **لا** يثبت Original ShaderLab 7Pass runtime أو RT/Sampler/CB0/Pixel على Adreno. جلسة CL `20261113-040212-998` و3 صور أدت إلى **28,592** ماء invalid (Spectrum11512/Foam17080) و4,576 kernel6 مع Android LOW_MEMORY PID18885؛ أضيفت كدليل مستقل، وليس تراجع أعداد الأخطاء دليلاً تلقائياً على تحسن. [جلسة Chat29](sessions/20261113-GT-spectrum-material-blit-and-phone-low-memory-chat-29.md). **التالي:** مسار exported Shader + meta الحقيقي من AssetRipper، استبدال dummy المؤقت بالمصدر الأصلي 7pass + global keyword وبقاء GUID، اختبار Unity Android Vulkan ثم اختبار الهاتف، Foam/kernel6، و770 Dummy؛ لا تنسب سبب نفاد الذاكرة للماء دون قياس مباشر.

---

## GT Chat-28 — إغلاق مسار حفظ مادة Spectrum بالمصدر، لا قبول GPU

تم إثبات مواد Spectrum الديناميكية حتى **حقل Material أصلي**: [43338485431](https://github.com/alwansan/raf/actions/runs/43338485431) `Shader.Find→own ctor→Material(Shader)`، [43339062121](https://github.com/alwansan/raf/actions/runs/43339062121) `dup`، [43339407339](https://github.com/alwansan/raf/actions/runs/43339407339) `set_` property→`stfld Material`، [43339688082](https://github.com/alwansan/raf/actions/runs/43339688082) **24 قراءات للحقل موزعة على 8 methods، منها 7 مع Graphics calls ودالتان RenderTexture calls**. هذا دليل source topology على مسار صنع المادة وحفظها وقراءتها، **وليس** برهان GPU ولا أن هذه المادة وسيط Graphics محدد. المطلوب P06: typed IL stack argument lineage لكل 24 ldfld، ثم أصالة ShaderLab 7Pass/Global Keyword وCB0/Sampler/RT، Foam2Pass، Compute kernel6، فحص هاتف Adreno وتغيير 770 Dummy الأصيلة. لا LFS أو GUID وهمي.

---

## GT Chat-28 — مسار Spectrum الديناميكي الأصلي يصل إلى Material(Shader)

P06/M2 تقدّم من مجرد Shader.Find إلى **سلسلة مصدر مثبتة** عبر [43337606930](https://github.com/alwansan/raf/actions/runs/43337606930)، [43337840022](https://github.com/alwansan/raf/actions/runs/43337840022)، [43338106531](https://github.com/alwansan/raf/actions/runs/43338106531)، و[43338485431](https://github.com/alwansan/raf/actions/runs/43338485431): Spectrum original name → typed Shader.Find → Shader local → new original 3-argument constructor, Shader last → **original third Shader argument immediately passed to `new UnityEngine.Material(Shader)`**. الـconstructor 44 IL وMaterial.newobj واحد. **Source evidence only**؛ Material result→Renderer/Graphics/RT غير مثبت، لا Original shader GPU/Android pixel ولا Foam/FFT index6 أو OBB GUID، ولا 770 Dummy أصيلة. P06/M2 يبقيان blocked لقبول الهاتف حتى الربط الحقيقي. التالي: تعقّب الـMaterial الجديد بعد newobj، ثم Runtime/RT/Sampler/CB0 وتضمين shader الأصلي واختبار Android على جهاز المالك. [جلسة Chat28](sessions/20261113-GT-spectrum-original-managed-material-constructor-chat-28.md).

---

## GT Chat-27 — جلسة جهاز جديدة مستقلة وفشل نشر البناء

CL@a320d5e جلسة `LogRaft-20261112-235351-196` ذات **4 صور**: **36,828** أخطاء Shader ماء (Spectrum **15,054**، Foam Global **21,774**) و**6,106 kernel6** غير محدد المصدر و**2,844 Cursor** و**2 OBB GUID**. الصور تثبت البياض الشديد للطوف والقائمة وماء سماوي/داكن غير صحيح رغم تشغيل العالم. هذا دليل جديد مستقل ولا يستبدل عينة Chat20 القديمة في عقود P06/P07/P10؛ كلاهما **فشل قبول GPU**. أُضيف فحص Final LogRaft FIFO writer consistency واختبار CI pinned؛ افحص CI الحقيقي. تشغيل Native [43299084397](https://github.com/alwansan/raf/actions/runs/43299084397) انتهى reconstruct SUCCESS وArtifacts لكن Publish Release HTTP403، لذلك M1/M2 غير مقبولين كـRelease أو رسوميات كاملة. الخطوة التالية Shader.Find consuming IL الأصلية (Chat26)→Material/RT ثم Foam/FFT shader pass و770 Dummy؛ لا LFS أو GUID مصنوع. [جلسة Chat27](sessions/20261113-GT-new-owner-night-phone-session-chat-27.md) · [دليل](evidence/20261113_cl_night_device_graphics_and_build_receipt.json).

---

## GT Chat-26 — Spectrum Shader.Find Managed، دليل مصدر لا GPU

[43300958608](https://github.com/alwansan/raf/actions/runs/43300958608): 19,118 compiled methods، 81 typed Shader.Find، أصل `Assembly-CSharp.dll` SHA، واستدعاء مباشر واحد باسم Spectrum الحقيقي. [43301684794](https://github.com/alwansan/raf/actions/runs/43301684794) أظهر Shader local بعد Find؛ [43302914466](https://github.com/alwansan/raf/actions/runs/43302914466) تابع 35 IL و3 branches مع load محلي واحد ممكن قبل overwrite، **consumer غير مصنف**. هذا يوجّه الاستعادة إلى managed runtime لا GUID Material ثابت؛ لم تُثبت Material ctor/RT/Sampler/CB0 أو Pixels. **P06/M2 لا يزالان blocked**. [جلسة Chat26](sessions/20261112-GT-spectrum-managed-shaderfind-resultflow-chat-26.md).

---

## GT Chat-25 — فحص Global Keyword وMaterial أصلي لجميع 82 owner

Unity2021.3.45f2 Android Vulkan [43297804472 SUCCESS](https://github.com/alwansan/raf/actions/runs/43297804472): synthetic Global serialized flag **0** وLocal **1**؛ Spectrum ZIP2 original `m_KeywordFlags[4]=0`. [43299461114 SUCCESS](https://github.com/alwansan/raf/actions/runs/43299461114) أكد private unified Spectrum 7Pass و2Variants وGlobal keywordSpace مع Material synthetic OFF→ON→OFF وBundle **14,484B** وصفر أخطاء Console نهائية. فحص [43299180998 SUCCESS](https://github.com/alwansan/raf/actions/runs/43299180998) وجد 0 Spectrum PPtr بين 1,392 Material في 40 sharedassets؛ الفحص الأوسع [43300053045 SUCCESS](https://github.com/alwansan/raf/actions/runs/43300053045) أثبت **82 original owners / 1,556 original Materials / 0 direct PPtrs إلى Spectrum**. معنى ذلك: لا مادة أصلية ثابتة مرتبطة به في serialized owners، **وليس** دليلاً بأن Shader.Find أو Material الديناميكي غير مستخدم. **P06/M2 ما زال blocked** حتى typed managed Shader.Find→Material→Renderer وCB0/Sampler/RT وPhone Adreno. [جلسة Chat25](sessions/20261112-GT-original-spectrum-material-82-owner-closure-chat-25.md).

---

> GT Chat24 scope-control follow-up: isolated synthetic Unity2021 Android Vulkan global vs local pragma control CI [43297804472](https://github.com/alwansan/raf/actions/runs/43297804472) launched at commit 682cbea730daf4af33c29f066639d84e14609839. It measures Shader.keywordSpace.isOverridable and serialized synthetic m_KeywordFlags, comparing to source-authentic Spectrum index4 byte 0. At this snapshot Unity compilation in progress; neither CI acceptance nor original game keyword scope established. If CI fails inspect real Unity and independent finalized console jobs; do not conflate bundle success with shader source or Adreno parity.

## تحديث GT Chat-24 — Original Spectrum Keyword Flags مثبتة من المصدر

[CI43296468683 SUCCESS](https://github.com/alwansan/raf/actions/runs/43296468683): فحص `m_KeywordFlags` الأصلي المباشر من ZIP2 SHA (115,978,112B)، وُجدت **5 Flags أصلية** تطابق **5 Keywords** و**Flag index4=0** وكلها متساوية (distinct=1)، ونجحت الاختبارات السلبية. **دليل SOURCE ONLY** وليس mapping مؤكد لمعنى global/local/overridable، ولا proof Material أو GUID/RT/CB0 أو Pixel. P06/M2 يبقيان blocked، وتبقى تجربة Unity السابقة الخاصة ذات 7Pass/2Variants/14,492B منفصلة عن اللعبة. [جلسة Chat24](sessions/20261112-GT-source-original-keyword-flags-chat-24.md).

---

**تاريخ التحديث:** 12 نوفمبر 2026 — GT / Chat-21.  
**فرع الكتابة الوحيد:** `feature/android-native-port`؛ **مصدر القراءة فقط:** `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`. **ممنوع Git LFS**.  
**سجل البيانات المهيكلة المعتمد:** [RESTORATION_PLAN.json](RESTORATION_PLAN.json) — راجع وضع كل دفعة وأدلتها قبل تعديل الحالة.  
**رسالة استكمال الجلسات:** [RESTORE_AR.md](RESTORE_AR.md)؛ **حالة GT:** [state.json](state.json)؛ **الذاكرة:** [MEMORY.md](MEMORY.md).  

## تحديث مثبت — Spectrum الأصلي داخل مختبر Unity (GT / Chat-23)

| الجزء | المكتمل بالدليل | ما يزال مطلوباً |
|---|---|---|
| الأصل | 7 Passes، 14 أزواج VS/FS، 28/28 Vulkan stages، 7 حالات رسم، 6 خصائص، Keyword index4 من ZIP2 | تفسير `m_KeywordFlags` الأصلي |
| Unity Android Vulkan | [43286126572](https://github.com/alwansan/raf/actions/runs/43286126572): المرشحان المنفصلان 7Pass لكل واحد وصفر أخطاء نهائية. [43288288144](https://github.com/alwansan/raf/actions/runs/43288288144): **شيدر واحد خاص، 7 Passes و2 ShaderVariants، Bundle 14,492B، صفر أخطاء Shader وأخطاء GLSL في فحص مستقل للسجل النهائي** | إثبات نطاق Keyword وإدارة Material الأصلية واختيار الفرع أثناء التشغيل |
| رسوميات Raft على الهاتف | **غير مثبتة**؛ لم يُدمج الـShader الموحد في اللعبة | ربط Shader/Material GUID وTexture/Sampler/CB0/RT؛ ثم APK وتجربة Adreno والسجلات والصور |
| بقية الرسوميات | موارد أصلية وأدلة مصدر متنوعة محفوظة في P00–P11 | Foam Global 2Pass، هوية compute kernel6، 770 مادة Dummy وبقية المؤثرات والألوان |

**لا تُحوّل نجاح مختبر ShaderBundle إلى نسبة استعادة للعبة.** مراحل القبول P06/M2 ما زالت معلقة. الاختبار 43288288144 أنتج مرشحاً خاصاً لم يُضمّن في APK أو XAPK، و`originalMaterialRuntimeKeywordSelectionProven=false`. الجلسة المرجعية [Chat-23](sessions/20261112-GT-spectrum-variant1-console-gate-chat-23.md).

## ما المقصود بـ«مستعاد»؟

المراحل لا تتساوى ولا تُجمَع في نسبة واحدة:
1. **موثّق من المصدر:** هوية الأصل/ملف ZIP2 وحجمه وبصمته الأصلية مثبتة.
2. **مستعاد داخل Export:** بيانات الأصل أو ربط Texture/Material أو إعداد importer مثبت في AssetRipper Export نفسه مع التحقق من GUID.
3. **اختبار Unity:** استيراد/ترجمة/Compile في Unity 2021.3.45f2 لنطاق محدد، وقد ينجح حتى مع عيب بصري.
4. **موجود داخل الحزمة:** APK+OBB+XAPK موثّق SHA/توقيع وCRC من commit محدد. ليس إثبات عرض صحيح.
5. **مقبول على الهاتف:** مسار الرسم من Material→Shader/Pass→Textures→GPU ونتيجة الصور/اللوق مثبتة على الجهاز، من دون أعطال معروفة.

**تنبيه:** الوصول إلى `82/82` في الجرد أو إنتاج XAPK لا يعني استعادة `100%` من رسوميات Raft. لا توجد حالياً نسبة صادقة موحّدة لكل الرسوميات المعروضة. الأعداد التالية لأصول المصدر ومواضع استعمالها وليست كلها أشياء مرسومة مستقلة.

## المستعاد والموثّق إلى الآن

| المجال | الدليل المنجز | المتبقي لإعلان الاستعادة الرسومية |
|---|---|---|
| **مصدر ZIP2** | **134 ملفاً** أصلياً بحجم **7,532,909,297 بايت** (82 حاوية Unity مسلسلة، 48 stream و40 مشهداً). تم SHA-authentication دون LFS وصدّر AssetRipper مشروعاً فعلياً. | إثبات الرسم لكل عائلة مورد على GPU، لا الاكتفاء بنجاح استخراجها |
| **Mesh والمشاهد** | **4,708 Mesh** أصلية؛ **40/40 مشهداً** موجوداً في export، وUnity نجح في بناء نسخة Android قديمة موقعة. | رسم Submesh وUV وNormal/Tangent والـSkinning لجميع الحالات المؤثرة، والتأكد من عدم ظهور الطوف أبيض |
| **Texture2D** | **4,050 Texture2D**، منها **3,948** ذات stream خارجي موثق و**102** inline/empty؛ **4,151** ربطاً داخلياً و**416/416** ربطاً خارجياً متطابقاً مع الأصل. | صحة Sampling والألوان/الـmips على Android في كل المواد |
| **Texture2DArray** | **9 مصفوفات/52 طبقة**، **50** طبقة BC3 ذات بيانات أصلية و**2** فارغتان أصلاً؛ أُصلحت 9 importer grids بالـexport المؤقت، وحُفظت GUID و**28** رابط Material؛ **50/50** pixel-parity للـtop mip في المصدر/Export. | كافة الـmips، استيراد/أخذ عينات Adreno وعرض المصفوفات داخل المشاهد |
| **مواد Material** | المصدر **1,556**؛ ملفات Export **1,536** منها **750** تعتمد Builtin؛ نجحت restorers في تحويل **16 مستند Material** مخصصاً من Dummy إلى غير Dummy. | **770 مستند Material مخصصاً لا يزال يرتبط بشيدر Dummy**؛ هذا عدد مستندات مواد وليس 770 شيدراً مختلفاً |
| **Unity Builtins/الـvendors** | أدوات دقيقة لأصول Unity 2021.3.45f2 (198 Shader من الأرشيف الرسمي) وTMP/PostFX/Volumetric وDepth Copy في pipeline، مع حراس للحفاظ على Meta/GUID. | تحقيق Pass/variant/مخرجات PostFX والظلال على هاتف Android، لا الاكتفاء بـsource restorer |
| **Shader48 للجسيمات** | Shader أصلي ذو **108 مواضع ParticleSystemRenderer**؛ أربعة أزواج VS/FS وثمانية برامج مترجمة ونجاح ShaderBundle تجريبي داخل Unity Android Vulkan باستخدام Sampler تقريبي. | المطابقة الأصلية للـsampler والـkeywords والـMaterial/GUID واختبار البكسلات على الهاتف؛ **ليس مدمجاً كشيدر أصلي مكتمل** |
| **الماء/Compute** | **165 Shader objects** و**9 ComputeShader objects** موثقة في المصدر؛ توجد أدوات للتحقق من Spectrum/Foam/FFT. | أصل Spectrum مُثبت بـ**7 Passes** و**28 برنامج VS/FS حسب variants** (7×2×2)، وأصل Foam Global بـ**2 Passes**؛ على الهاتف **42,229** أخطاء Pass و**7,263** خطأ kernel index 6، وهوية هذا kernel لم تثبت |
| **حزمة Android** | استرداد حزمة قديمة موقّعة: APK **672,892,355 B** + OBB **2,320,414,462 B** وXAPK من [43246196803](https://github.com/alwansan/raf/actions/runs/43246196803). | البناء الكامل الحديث [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) لا يزال في Unity Editor عند آخر فحص؛ لم تُقبل الألوان/الماء/النار/الأداء على الهاتف |

**أدلة مصدر مهمّة:** [الجرد الكامل](https://github.com/alwansan/raf/actions/runs/43114648901) · [AssetRipper الحقيقي](https://github.com/alwansan/raf/actions/runs/43125542125) · [بوابة المصدر 9/28/416/50](https://github.com/alwansan/raf/actions/runs/43207734641) · [Shader48 التقريبي في Unity](https://github.com/alwansan/raf/actions/runs/43236578305).

## ما تبقّى والأولويات الحالية

| الرمز | الأولوية | الحالة | المهمة التالية / معيار قبولها |
|---|---|---|---|
| **M1** | P0 | **جارٍ** | راقب بناء [43247161671](https://github.com/alwansan/raf/actions/runs/43247161671) ولا تكرره وهو جارٍ. إذا فشل اقرأ **أول خطوة فاشلة** ثم أصلحها؛ نجاحه = APK/OBB/XAPK موقّعة حديثة وبصماتها صحيحة، وليس إصلاح الصورة |
| **M2** | P1 | **معطّل بنقص برنامج أصلي** | عالج `UltimateWater/Spectrum/Water Spectrum` (يتطلب 6 Pass على الأقل في log baseline) و`UltimateWater/Foam/Global` (2 Pass على الأقل): إثبات Shader GUID/Material/RenderTexture وربط HLSL الأصلي ثم Unity Android import وPass count وإعادة اختبار الجهاز |
| **M3** | P1 | **معطّل بنقص هوية kernel** | اربط kernel رقم 6 بكائن ComputeShader SHA-original وترتيب kernels ومكان Dispatch؛ لا تفترض أنه FFT اعتماداً على الرقم وحده. أعد بناء برنامج حقيقي وقارن النتائج على Vulkan ثم Adreno |
| **M4** | P1 | **لم يكتمل** | رتّب الشيدرات الأصلية حسب عدد استعمالات Renderer في المشاهد، وأصلح على دفعات من ضمن **770 Material Dummy**؛ فحص Guid→Pass→Keyword→Sampler→Texture، ثم المقارنة على الهاتف (ألوان الطوف، النار، الظلال) |
| **M5** | P2 | **قيد التشخيص** | عالج Cursor RGBA32 وOBB GUID وMissing MonoScript من مواقع الأصل، ثم أثبت استقرار frame time وسلامة الواجهة وعالم Offline |
| **M0** | P0 | **مكتمل لهذا النطاق فقط** | توثيق جرد المصدر ونقطة baseline واستقبال CL وتجربة بوابة اللوق. لا يعني استكمال الاستعادة الرسومية |

### تدقيق الفرق بين المصدر الأصلي ورسالة Pass من الهاتف

- كائن `UltimateWater/Spectrum/Water Spectrum` الأصلي يحمل **7 Passes** تحت SubShader واحد، وبرنامجين (VS/FS) لكل نسختين من كل Pass = **28 مرجع stage**؛ وثقته [B09 الأصلي](https://github.com/alwansan/raf/blob/feature/android-native-port/scripts/b09_spectrum_topology_contract.py) مع [CI 41920232173 SUCCESS](https://github.com/alwansan/raf/actions/runs/41920232173).
- كائن `UltimateWater/Foam/Global` الأصلي يحمل **2 Passes** وأربعة برامج VS/FS أصلية؛ برامج Foam الحقيقية وCB0 والـSamplers تحتاج ربطاً وتجميع Unity Android قبل الدمج.
- `verify_water_render_contract.py` يطلب `Spectrum >= 6` لأن السجل القديم طلب Pass #5. **هذا حد أدنى لتفسير log فقط**؛ استعادة شيدر Spectrum الصحيحة تحتاج **7 Passes مع Pass states والـkeywords الأصلية**، ولا يجوز ملء العدد بـPass فارغة.
- [CI 43268872421 SUCCESS](https://github.com/alwansan/raf/actions/runs/43268872421) يختبر هذا الفرق في [بوابة الخطة](../../scripts/gt_restoration_plan_check.py)، ولا يثبت أن البرنامج الأصلي صار داخل APK.

### تجربة GT الجديدة داخل Unity Editor (اختبار قراءة فقط)

أُضيف [GTOriginalWaterPassImportProbe.cs](../../android-port/Editor/GTOriginalWaterPassImportProbe.cs) ويُستدعى من `AndroidNativeBuild.ValidateSdkBindings` قبل بناء Android التالي. يفحص كائني Spectrum وFoam المسمّيين في Assets، ويُبلغ عن عدد الـPasses المستوردة وعن وجود `//DummyShaderTextExporter` وتكرار اسم shader وأخطاء المسار. يحفظ الفرق بين **Spectrum الأصلي 7** والحد الأدنى المسجّل **6**، وFoam الأصلي **2**. لا يطبع GUID أو HLSL أو مسارات الأصل، **ولا يعدّل أي ملف shader أو .meta أو Material**. أدلة Unity على الهاتف ما زالت غير متاحة؛ الفحص التشخيصي وحده لا يُصلح الشيدر ولا يضمن أصالة محتواه.

**[43269999662 — SUCCESS](https://github.com/alwansan/raf/actions/runs/43269999662):** 5 اختبارات مصدرية + تجميع وتشغيل C# بواسطة .NET مع محاكيات Unity API، والتحقق من Shader Spectrum ناقص بPass واحد وFoam بPassين ومنع path traversal. **هذا ليس تشغيل Unity Editor الأصلي ولا اختبار Adreno.** في البناء الحديث التالي، ابحث في سجل Unity عن `GT_WATER_IMPORTED_PASS_DIAGNOSTIC` ثم اربط الناتج بالـGUID والـMaterial وبرنامج المصدر قبل تعديل حالة `unity_verified`.

## دفعة GT الجديدة — Spectrum الأصلي: مصدر → حالات الرسم → ShaderLab خاص (Chat-22)

استخدمت المصدر الأصلي `ZIP2@15964ea8` من دون LFS، وأصلحت تعارض مكان ملف `sharedassets0.assets` بين موفّر ZIP2 وأداة B09، بعد التحقق من **115,978,112 بايت وSHA الأصلي**. **المصدر الأصلي لم يتغير**.

| التحقق | مثبت | حدّ الإثبات |
|---|---|---|
| Spectrum Shader topology | **7 Passes أصلية** و**14 زوج VS/FS** | استعادة هويات المصدر، لا استيراد Android |
| Vulkan 1.1 | **28/28 stage variants** تم تجميعها فعلياً، و**13** برنامجاً مميزاً أُعيدت ترجمته | نجاح glslang/spirv-val فقط |
| حالات الرسم | **7/7** حالات Render State مختلفة، ببيانات أصلية | SHA-verified private source state، لا Pixels |
| خصائص Spectrum | **6**: خامتان Texture و3 Float وVector واحد | القيم/الأسماء باقية في scratch الخاص، ليست منشورة |
| ShaderLab | **مرشحان خاصّان، كل واحد 7 Passes**؛ المجموع 14 Pass structural envelopes | **ليسا شيدراً واحداً ذا Keyword routing أصلي**؛ لا GUID/Material parity |
| أداة Unity 2021 | تجربة **isolated variant0** على Android Vulkan أُطلقت في [43275506146](https://github.com/alwansan/raf/actions/runs/43275506146) | لا تعتبر Unity نجاحاً قبل انتهاء التجربة وفحص `ProbeResults` |
| اللعبة الأصلية على الهاتف | **غير مكتمل** | ألوان الماء والـSamplers والـCB0 والـRT والـShader/Material GUID لم تُثبت |

الاختبارات المثبتة: [43273276394 — ترجمة البرامج 28/28](https://github.com/alwansan/raf/actions/runs/43273276394) · [43273958426 — حالات الرسم الأصلية](https://github.com/alwansan/raf/actions/runs/43273958426) · [43274729958 — مرشحا ShaderLab الخاصان](https://github.com/alwansan/raf/actions/runs/43274729958). كلها **SUCCESS في نطاقها فقط**.

**الخطوة القادمة:** افحص [تجربة Unity 43275506146](https://github.com/alwansan/raf/actions/runs/43275506146). إذا فشلت في استيراد shader أو بناء AssetBundle، استخرج فئة الخطأ الآمنة وصحّح ربط sampler/cbuffer من الأصل؛ لا تصنع سامبلر أو pass وهمياً. بعد نجاح Unity بشكل منفصل، أثبت variant1 ثم Keyword routing الحقيقي وربط GUID والمادة وRT الأصلي، ثم جرّب رسم الماء على الهاتف. لا تدمج المرشحين الاثنين في اللعبة بوصفهما شيدراً أصلياً مكتملًا.

### نتيجة تجربة Unity 2021 الفعلية — عطل CBuffer في Spectrum (Chat-22)

[43275506146 — FAILURE](https://github.com/alwansan/raf/actions/runs/43275506146): **استورد Unity فعلياً Shader Spectrum خاصاً بـ7 Passes** وبنى Android Vulkan AssetBundle حجمه **6,095 بايت**، لكن الفاحص سجّل **خطأَي Shader**، لذلك لا يجوز اعتبار الاختبار ناجحاً. كشف Unity GLSL linker اتحاد نفس اسم Uniform CBuffer بين Vertex وFragment بأحجام مختلفة (`vec4[4]` أمام `vec4[5]` أو `vec4[7]`)؛ ليست مشكلة نقص Passes في هذا المرشح، وليست دليلاً على أن البرنامج الأصلي معطوب.

أضفت إصلاحاً تشخيصياً محدوداً هو `scripts/gt_spectrum_private_stage_buffer_isolation.py`: يفصل أسماء رموز CBuffer المؤقتة بحسب Stage على **نسخة ShaderLab الخاصة** فقط، مع إعادة مطابقة بايتية عكسية بعد إزالة البادئات والتأكد من عدم تغيير annotations من نوع `register(...)`. لا يغيّر مصدر ZIP2 أو Shader/.meta/GUID أو ربط Material الأصلي. [43276622833](https://github.com/alwansan/raf/actions/runs/43276622833) توقف على بيانات الاختبار الصناعي بسبب أحرف `\\n` حرفية لا أسطر فعلية. أصلحت المثال في commit `8e46f03a`؛ و[التجربة الجديدة 43277618651](https://github.com/alwansan/raf/actions/runs/43277618651) دخلت Unity 2021 Android Vulkan، **وما تزال نتيجة تجميع الشيدر غير مثبتة عند آخر تحقق**؛ يجب فحصها وSafeResult.

**الأولوية بعد الإصلاح:** التحقق من ترجمة برنامج Unity دون أخطاء؛ ثم اختبار variant1 وربط كِلا مسارَي Keyword الأصلية في شيدر واحد، ثم مصادر Sampler وCB0 وMaterial/RT/GUID، ثم XAPK حديث وتجربة هاتف. لا تخلط نجاح Bundle مع Pixel equivalence.

### GT / Chat-23 — نجاح Shader Spectrum منفصلين وفحص التوحيد

بعد معالجة `cb4_struct` داخل نسخة اختبار خاصة، [43286126572 SUCCESS](https://github.com/alwansan/raf/actions/runs/43286126572) اجتاز **كلا العملين**: Unity 2021 Android Vulkan والتدقيق المستقل النهائي للسجل. لكل مرشح 7 Passes مستوردة؛ Variant0 Bundle **12080B** وVariant1 **12409B**؛ مجموع أخطاء GLSL linker وInternal Variant وShader import/compile **صفر**. هذه **نجاحات فعليّة لتجميع البرامج الخاصة المعزولة فقط**، لا نسخة Raft الأصلية.

[43286701677 SUCCESS](https://github.com/alwansan/raf/actions/runs/43286701677) أثبت من نفس ZIP2 الأصلية توافق Keyword **index4** والـ14 زوجاً/28 stages في 7 Passes، وركّب ShaderLab خاصاً واحداً يحتوي 7 برنامج Pass و2 فرع مصدر أصلي لكل واحد (مع عزل Uniform Blocks القابل للعكس). **لا يثبت Scope flags ولا Runtime اختيار Material**. [43288288144](https://github.com/alwansan/raf/actions/runs/43288288144) يختبر المشروع الموحد في Unity 2021 Android Vulkan مع تسجيل 2 ShaderVariantCollection candidates، وبعدها فحص Console نهائي مستقل. يلزم نجاح الثلاث مهام قبل اعتباره "Provisional Unity Compilation"، ويبقى Material/GUID/RT/CB0/Adreno غير مثبت.

### GT / Chat-23 — منع False Green من ShaderUtil في Spectrum Variant1

حالة المصدر ما زالت **7 Passes أصلية، 14 VS/FS pairs، 28/28 مراحل Vulkan، 7 حالات رسم، 6 Properties**. [Unity2021 CI 43279249696](https://github.com/alwansan/raf/actions/runs/43279249696) أثبت استيراد وتجميع **Variant0 الخاص** (7Pass، 0 خطأ Shader، Bundle 12079 B). **لا GUID/Material/Adreno**.

[43282759870](https://github.com/alwansan/raf/actions/runs/43282759870) أعاد `SUCCESS` لمرشح Variant1، ومع ذلك سجل Unity أظهر **12 GLSL link errors** و**12 internal variant creation failures** حول `cb4_struct` المتعارض بين VS وFragment، بينما `ShaderUtil.GetShaderMessages` أبلغ صفر خطأ. **هذا فشل مثبت ولا يجوز إدراجه كنجاح.** مُخرَج Bundle 12418B لا يُثبت سلامة البرامج.

أضفت `scripts/gt_spectrum_private_stage_buffer_isolation.py` بإصلاح **اختياري قابل للعكس** لأسماء `cbN_struct`/`cbN` داخل ShaderLab الخاص فقط، دون تعديل `register(bN)` أو أصول Raft؛ وفحصاً جديداً `scripts/gt_spectrum_ci_console_gate.py` يرفض أي أخطاء Link أو Import أو إنشاء internal variant من سجل GitHub Actions النهائي. **[43285251243](https://github.com/alwansan/raf/actions/runs/43285251243)** هو التشغيل الجديد؛ **يجب اجتياز مهمتي `original-private-spectrum-pairs` و`strict-final-unity-console` معاً**. النجاح الظاهري للمهمة الأولى وحدها لم يعد كافياً، ولا يعني أصالة Material أو GPU Pixels.

الخطوة القادمة: حل فشل `cb4_struct` إن بقي، ثم اختبار مصدر Keyword index4 في شيدر واحد، وربط مادة اللعبة/RT/CB0/GUID واختبار الهاتف. [جلسة Chat-23](sessions/20261112-GT-spectrum-variant1-console-gate-chat-23.md).

### فشل الهاتف الذي يحكم القبول

السجل `CL@cffd3f7be2d0c47649da9b28eae17c36d031f0e8` بتاريخ 12 نوفمبر لجلسة `LogRaft-20261112-183147-926` أثبت:
- **42,229** Water Shader invalid passes: **19,191 Spectrum** و**23,038 Foam/Global**.
- **7,263** Kernel index 6؛ لا يثبت السجل وحده جهة استخدام الـCompute.
- **4,668** تحذير Cursor RGBA32، **2** OBB GUID load failures و**1** MonoScript مفقود.
- اللقطات تظهر **الطوف أبيض تقريباً** مع بقاء بعض الأشياء ملونة؛ سجلت لقطة HUD هبوطاً إلى **0.29 FPS**. لا يُنسب سبب اللون أو الإطارات إلى كود معين من هذه اللقطات وحدها.

[الدليل الثابت](evidence/20261112_cl_device_graphics_failure_receipt.json) · [الاختبار المصدرّي الناجح بكشف الفشل](https://github.com/alwansan/raf/actions/runs/43263197989). أداة `scripts/gt_device_graphics_acceptance.py --strict` **ترفض** هذا السجل، وهذا التصرف صحيح. يجب أن ينجح الاختبار على *جلسة جديدة* فقط بعد زوال الأخطاء ومراجعة الصور.

## طريقة التقدّم من أي محادثة جديدة

1. افتح [رسالة الاستعادة](RESTORE_AR.md)، ثم [الخطة JSON](RESTORATION_PLAN.json)، [state.json](state.json)، [SUMMARY_AR.md](SUMMARY_AR.md) وآخر ملف `sessions/`. تحقّق من Git HEAD وActions قبل أي تعديل.
2. اختر هدفاً واحداً من M1→M5، وحافظ على مصدر ZIP2 SHA والبصمات الأصلية؛ استخدم runner مؤقتاً و`lfs: false`.
3. نفّذ اختباراً صغيراً أولاً (synthetic negative controls، ثم source-real/Unity/phone حسب التقدم)، سجّل Run ID وSHA وما **لم** يثبت.
4. حدّث خلية/حقل `Pxx` في JSON والحالة وملخص المالك، ثم [RESTORE_AR.md](RESTORE_AR.md) و[MEMORY.md](MEMORY.md) وملف الجلسة. لا تعلن «مستعاد» دون مستوى الدليل المناسب.
5. لا توقف البناء القديم ولا تضع **SUCCESS** في علامة `device_verified` لمجرد أن Unity أنتج APK أو أن مختبراً مستقلاً نجح. لا تحفظ شيفرات الشيدر الأصلية أو GUID الخاص داخل نتائج عامة.

**الحدّ الحالي:** الاستعادة نجحت في *توثيق المصدر واستعادة أجزاء Export والـvendor وبعض النماذج التجريبية*؛ **استعادة رسوميات اللعبة الكاملة لم تكتمل**. النجاح النهائي مشروط بتصحيح الماء والشيدرات والمواد والنار والظلال وحصول مقارنة هاتف موثوقة.

## دفعات دمج البصريات في Android

استعادة مدخلات المجسمات ومواقع Vulkan لشيدر 921، وتجهيز ShaderLab للفحص المعزول. دمجنا إصلاح معرّفات عظام المجسمات، ومثبّتي Particle108 وDepth Copy مع حفظ GUID. تحقق Unity المعزول للجسيمات وDepth نجح. [جلسة الأدلة والخطوات الباقية](sessions/20261113-GT-visual-restoration-native-batches.md). لا XAPK.
