# GFX141 session — 2026-11-11, origin=chat

Worker: GFX-LAB. Branch: experiment/android-graphics-rootcause ONLY. Parent commit: 9bc5a85a980f119ee1f31bf0e7e3e3906fba94a9.

Goal: reconstruct from immutable zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 every original controlled source asset needed for GFX124's nine cases and 51 readbacks. Install pinned translation toolchain; render private original Mesa references, package through the existing production packer, sign real Android runner with temporary v3 debug signature, check all embedded fixture bytes after signing. Upload **only source-safe aggregate JSON**, never original game assets, raw captures, model, shader, mip textures, or source-original APK. Delete temporary signed APK and source stage. This workflow does not deliver an APK yet. No actions against main, zip2 or T-team branches.

Files: gfxlab/tools/gfx141_stage_original.py; gfxlab/tools/gfx141_compose_original.py; gfxlab/tools/gfx141_compile_shell.sh; .github/workflows/gfxlab-multi141-original-private.yml.

Status: Initial CI execution pending after this commit. Continue by inspecting run logs and making minimal fixes. Success is not assumed. If it passes, solve secure user transfer of original APK separately. Retain original Unity Runtime/pass/animation and PC scene parity gates. phase_closed=false.

## 11 نوفمبر 2026 — GFX141 VERIFIED: بناء APK أصلي موقّع دون نشر موارد Raft

جلسة `20261111-GFX-chat-original-batch-98`، الهوية `GFX-LAB`، `origin=chat`، وفرع الكتابة الوحيد `experiment/android-graphics-rootcause`.

- **النجاح المثبت:** [GitHub Actions 43077708276](https://github.com/alwansan/raf/actions/runs/43077708276) COMPLETED SUCCESS على commit `6b06aef4817e1ad74202def0bc7d2af5fc2ba6c3`. أعيد استخراج المصدر الأصلي المثبّت `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`، وتهيئة وبرمجة Shader48، أصل المجسمات والخامات وmips، اختبارات ForwardAdd و15 عينة حركة وShadowCaster وDeferred بأربعة MRT ومراجع Mesa المضبوطة.
- **الحزمة:** نجح تغليف `9` حالات و`51` لقطة مرجعية و`235` ملف موارد أصلي داخل Android APK تنفيذي مبني من GFX124، وتم `zipalign` والتحقق من توقيع `APK v3` ومن تطابق محتويات الموارد قبل/بعد التوقيع. حجم APK الموقّع المؤقت **23,082,040 بايت**، SHA-256 `fcec3dc62bb00a893ebe5441fa46c402ff0ba190054459784b6c5c3d670a9e46`.
- **سبب فشل المحاولة الأولى:** [43076669980](https://github.com/alwansan/raf/actions/runs/43076669980) نجحت في جميع مراحل مصادر Raft ومراجع Mesa، ثم فشلت بسبب `KeyError: 'mesa'` عند تمرير دليل ForwardAdd إلى أداة التجميع. صُحّحت البنية المتوقعة `{"mesa":{"forward_add":...}}` في commit `6b06aef` وأُعيد البناء بنجاح.
- **الخصوصية والتسليم:** لم يُرفع APK الأصلي أو الـ shaders أو meshes أو textures أو readbacks الخام إلى المرفقات العامة. حُذف APK الموقّع المؤقت وأصول المصدر من بيئة Actions بعد فحصها. [المرفق الآمن 13883790033](https://github.com/alwansan/raf/actions/runs/43077708276/artifacts/13883790033) يتضمن JSON تجميعياً فقط، **وليس ملف APK يمكن تنزيله وتثبيته**.
- **المتبقي فعلياً:** آلية تسليم APK الأصلي بطريقة يوافق عليها المالك، تشغيل 9 اختبارات و51 لقطة على Adreno 730 وتدقيق ZIP داخل `/storage/emulated/0/Download/Games/cl/test/g/`، فحص حالات Pass وG-buffer الأصلية داخل Unity، الحركة الفعلية بمشغل Animator، والمقارنة مع مشهد اللعبة على PC. لا نخلط هذه الأدلة مع نجاح بناء APK.

`originalShaderRestored=false`، `originalAnimationRestored=false`، `phase_closed=false`.

