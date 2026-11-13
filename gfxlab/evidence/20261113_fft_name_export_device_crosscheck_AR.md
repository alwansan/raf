# FFT — مطابقة المصدر والتصدير والهاتف

- أصل ZIP2: سجل جرد الأصل يثبت اسم ComputeShader عند sharedassets0.assets/pathID2456 ببصمة 60c1b5ee2352bd6e303aa5fc68c88f61031cf21234f524d54ec02334a8e142d1. عشرون برنامج DXBC تشترك في اسم kernel مسلسَل واحد؛ لا مساواة بين ترتيب البرامج وفهارس Unity. [جرد المصدر](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/ORIGINAL_WATER_LFS_COMPUTE_INVENTORY_2026-11-03.md)
- سجل رفع 14 للنسخة 101 يضم البصمة نفسها ضمن ComputeShaders المحمّلة. هذه مطابقة اسم فقط، ولا تثبت هوية receiver في Dx11FFT ولا وجود kernels فيه. [رفع 14](https://github.com/alwansan/CL/tree/710d5cd95efb70a985221cc0646687af7b03ca17/raft%20log)
- تقرير ExportedProject للنسخة 102: صفر مصادر compute مؤهلة باسم الماء مع kernels، وحارس الأصل غير مجتاز. Spectrum 1/6 وFoam 1/2، Blur 2/2 في المصدر المرحلي، وDepth Copy موزع [6,3]. لم يتضمن هذا التقرير فحص Underwater/Base IME. [أثر البناء](https://github.com/alwansan/raf/actions/runs/43299084397/artifacts/13981944130)
- هاتف 102: أول SetTexture رمى في 32/32 محاولة مرصودة. Unity أبلغ عن حد kernels يساوي صفر. [دليل الهاتف](20261113_water_native_v102_fft_binding_AR.md)

العمل التالي: مطابقة Serialized PPtr وملف ComputeShader المصدّر لهوية الأصل، ثم تجربة تسجيل وربط مرشح حقيقي من المصدر. لا يُعتبر الاسم إثبات ربط. اختبارات ترجمة البرامج المنفردة السابقة لا تثبت اختيار Unity لأزواج التمريرات. لا حاجة لإعادة تجربة 102.
