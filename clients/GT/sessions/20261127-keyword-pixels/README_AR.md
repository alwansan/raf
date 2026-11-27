# GT A2 — اختبار فعلي لاختيار الكلمات بالبكسلات (مكتمل في نطاق مؤلف)

الرأس المختبر `50332d816ac2bc5a8f92e84a0991f9bffde6a0a8`. [Actions45931001072](https://github.com/alwansan/raf/actions/runs/45931001072) job140283349151 انتهى SUCCESS. حفظنا كامل [ZIP الأصلي](actual-run-45931001072.zip) (3191B، بصمة API مطابقة وCRC صالح) وفيه raw.unity.json وstage.json وverified.json. [إعادة الحساب المحلية](artifact-review.json) على إيصال Unity الفعلي طابقت التقرير المستقل للـrunner. **15 حالة × 24 pixel = 360 pixel / 1440 RGBA، max error0**. أربع علامات فعلية من VS وFS، route3 فارغ وليس route0. G global وL local صريحان في العينة، مادتان بعلامتي B .25/.75، اختبارات on/off/on والعزل، ومحاولة تفعيل L globally لا تغيّر local. خمس مقارنات مع نتيجة مسار خاطئ، min separation0.125. Linux/Vulkan llvmpipe، Unity2021.3.45f2 Linear؛ ليست بكسلات Android أو اللعبة. لا أصل أو APK/XAPK. نحتفظ بكل البايتات الخام حتى بعد انتهاء صلاحية artifact.

## إعادة الإنتاج
من checkout مصدري مأذون للرأس الذي يحتوي هذه الجلسة وأدوات الاختبار، مع Python3:
```sh
python3 -B tools/synthetic_material_alpha/keyword_pixels.py selftest
python3 -B clients/GT/sessions/20261127-keyword-pixels/review_artifact.py --archive clients/GT/sessions/20261127-keyword-pixels/actual-run-45931001072.zip --sha256 e302694238bf4a5f95d904904ae169adbd840894124c1b6eda245811a8f2867b --run-id 45931001072-1-50332d816ac2bc5a8f92e84a0991f9bffde6a0a8 --out /tmp/gt-a2-independent-review.json
```
المسار الأخير يجب أن يكون جديداً. أداة الإعادة لا تشغل Unity، وتعتمد هوية التشغيل على Actions المثبت. للتجربة الفعلية عند الحاجة فقط، وضع keyword-pixels في workflow raft-gt-synthetic-material-alpha.yml على فرع العمل، مشروع مؤلف فارغ وسحب sparse فقط. لا تكرر تشغيل ناجح بلا حاجة. [اختبارات المصدر](selftest.log) و[CPP](cpp-source.json) منفصلة عن دليل الرسم. لم يتوفر clone كامل محلياً، وتم التحقق من تطابق Git blobs وملفات الأدلة.

## الخطوة التالية
A3: تحقق من توافر مصدر NEXT23b المأذون، وأثبت scope/PassType والـlattice والبرامج واختيار المادة الأصلية قبل الدمج. إذا تعذر، وثق العائق المحدد وتحرك في G0–G6 إلى أقرب إصلاح مأذون. لا تكرر عقداً اصطناعياً بلا أثر. الجرد التاريخي 688/786 Custom، 98 Dummy/37 GUID لم يتغير. لا قبول بصريات اللعبة، لا XAPK أو هاتف جزئي. الأنيميشن مؤجل. [evidence.json](evidence.json) يحفظ تفاصيل التنفيذ والبصمات. 
