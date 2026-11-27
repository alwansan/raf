# GT A2 — اختبار اختيار الكلمات بالبكسلات

رأس البدء 23f999062acf3c891fa4e87466844b38ea9ff822. طبقنا عقد strict_engine_router على شبكة مؤلفة من أربعة مسارات وكلمتين GT_A2_GLOBAL وGT_A2_LOCAL؛ scope المحلي مصرح في العينة، وليس استنتاجاً عن أصل اللعبة. مسار empty رقمه 3 وroute0 يحتوي الكلمتين. المشهد المؤلف 6×4 float RGBA Linear، علامتان مستقلتان من VS وFS وعلامة المادة. 15 تبديل حالة على مادتين، 360 بكسلاً متوقعاً و5 مقارنات مع مسارات خاطئة؛ لا نقبلها قبل actual Unity receipt. اختبارات Python المحلية 5/5 شملت 9 تحريفات إيصال وexit غير ناجح. مرشح C# لم يُ مترجم محلياً. لا clone كامل؛ الملف المشترك مطابق للبصمة المنشورة.

وضع keyword-pixels داخل workflow المجرب، sparse checkout للأدوات فقط، LFS disabled، لا أصل أو APK. يعيد بناء Unity Linux Vulkan في المشروع المؤلف، يقارن الإيصال الرقمي مستقلاً، ويحفظ النتائج فقط. commit يحمل [gt-keyword-pixels] لا [skip ci] لإطلاق هذه التجربة المأذونة. تحقق بعد الدفع من Actions والـjob والأرشيف؛ لا تنسب أية بكسلات جديدة قبل اكتمالها. حالة A2 ACTIVE ولا قبول للعبة. لا XAPK.

إعادة اختبارات المصدر من الجذر:
```sh
python3 -B tools/synthetic_material_alpha/keyword_pixels.py selftest
python3 -B tools/synthetic_material_alpha/keyword_pixels.py stage --project /tmp/gt-keyword-a2 --out /tmp/gt-keyword-stage.json
```
