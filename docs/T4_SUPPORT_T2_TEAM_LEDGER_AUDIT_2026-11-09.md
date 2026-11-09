# T4 → T2/T3/T5 — فحص شامل لهويات أحداث السجل الموروث

**2026-11-09 | origin=chat | session_id=`20261109T1919Z-T4-chat-ledger-preflight-v4k8`**  
**COORD-001 فقط، ولا علاقة له بقبول لعبة Raft على الهاتف.**

## المشكلة

سجل GitHub Actions الخاص بـT2 ([42680680366](https://github.com/alwansan/raf/actions/runs/42680680366) و[42682378346](https://github.com/alwansan/raf/actions/runs/42682378346)) يفشل في `refresh_b_team.py::read_records` بسبب أحداث قديمة تفتقر `id` و`event_id`. أول ملف يوقف التجديد هو `T3/20261106T2007Z-T3-chat-explicit-original-d52e.json`. لا يجوز إلغاء شرط الهوية أو اختلاقها آلياً من اسم الملف لأن هذا يخفي التكرارات أو فقد الأثر التاريخي.

## التنفيذ

أنشأ T4 ماسحًا مستقلاً `scripts/t4_audit_team_event_identities.py` يفحص كل JSON تحت `prompt/coordination/B_TEAM/events/` دون تعديلها. يقلّد شرط الهوية الأساسي: `event_id` النصي الصالح يطابق `id` عند وجودهما، ويقبل `id` الصالح كبديل. يبلغ جميع حالات فقد الهوية والتصادم والتكرار، إضافة إلى JSON التالف والمفاتيح المتكررة وروابط الملفات، لا يتوقف عند أول ملف فقط. حدود الملف 1 MiB، وعدد الملفات 15000، ونتائج المصدر لا تتضمن نص أي حدث، بل أسماء ملفات ومجاميع. لا يكتب في `snapshot.json` أو ملفات T2/T3/T5 ولا يحدد نسب اكتمال أو ادعاءات هاتف.

- الملف: `scripts/t4_audit_team_event_identities.py`، commit `65f1e298c7d3853c51eac42fb8c9b80d3fb47d06`.
- اختبارات Python 10 حالات: `tests/test_t4_audit_team_event_identities.py`, commit `3738fd34e20e88dc4c8eb8797d370a231cafefb0`.
- Workflow خفيف مستقـل: `.github/workflows/raft-t4-ledger-identity-audit.yml`, commit `ad197f28c03fe9b5db66d088a74094e7c749aa26`، ثم تحديث trigger الخاص بملفات T4 فقط `81c43f0b48365c18eb28a61e4f6bf26668c6e2ea`، `cancel-in-progress=false`.

## نتائج قبل الإصلاح

**[GitHub Actions 42682466747](https://github.com/alwansan/raf/actions/runs/42682466747) COMPLETED SUCCESS**. سجل الوظيفة يؤكد `Ran 10 tests ... OK`، ثم مسح **595** ملف أحداث، **22 MISSING_RECORD_ID** فقط:
- T3: **14** ملفًا.
- T4: **3** ملفات.
- T5: **5** ملفات.

ملف النتيجة الكامل (مسارات عامة فقط) [Artifact 13702867598](https://github.com/alwansan/raf/actions/runs/42682466747/artifacts/13702867598). أسماء الملفات التسعة عشر التابعة لـT3/T5 موجودة في **[رسالة التنسيق](../prompt/coordination/discussions/COORD-001/20261109T1923Z-T4-chat-all-event-identities-v4k8.md)**، ولم يكتب T4 فيها.

## إصلاح T4 فقط

نطاق عمل مستقل `20261109T1922Z-T4-chat-own-eventid-repair-z6q4` كتب مفتاح `event_id` النصي إلى الأحداث التاريخية الثلاثة التي صاحبها `owner=T4`، مع الاحتفاظ بكل الدليل السابق:

- `T4/20261106T2222Z-T4-owner-jsonl-single-read-n7b4.json`: commit `2b41ea0da3976cb3f9815677d45acdd3390492dd`.
- `T4/20261106T2231Z-T4-original-runtime-operation-stage-drift-c6p2.json`: commit `891027dbbd040c87df29d0d9264f779e6e362068`.
- `T4/20261106T2254Z-T4-runtime-postinstall-safe-rollback-p9v3.json`: commit `a41c46ef9e5369129dc6e65eae17be274dbfd871`.

المتوقع حسابيًا بعد هذه الخطوة إذا لم تتغير أحداث أخرى: 19 مشكلة خارج ملكية T4. **هذا العدد يجب إعادة فحصه من CI جديد قبل اعتباره مثبتًا.**

## حدود الإصلاح

نجاح workflow الخاص بمدقق T4 = **اكتمل المسح فقط**؛ `canonical_summary_generation_proven=false` حتى عندما لا توجد مشكلات. لا يدل على نجاح `refresh_t_team.py` أو جاهزية الماء أو XAPK. الملف الموروث باقٍ لدى T3/T5 لإضافة الهوية بأنفسهم بالتنسيق مع T2. لا تكرر فشل workflow التحديث المشترك قبل معالجة جميع السجلات الناقصة. لا تعدل أي scene/shader/OBB أو APK.

**فحص لاحق مثبت:** [42682900051](https://github.com/alwansan/raf/actions/runs/42682900051) **COMPLETED SUCCESS** على SHA `81c43f0b48365c18eb28a61e4f6bf26668c6e2ea`; job `129381898864`، `Ran 10 tests; OK`، **596 ملفًا، 20 MISSING_RECORD_ID**: **T3=15، T5=5، T4=0**. زاد عدد سجلات T3 بواحد منذ المسح الأول، وهو `T3/20261109T1913Z-T3-chat-smoke34-sameexport-v5m8.json`، ولذلك بقي 20 بدلاً من التوقع الرياضي 19. Artifact جديد: [13702214952](https://github.com/alwansan/raf/actions/runs/42682900051/artifacts/13702214952). **الملخص القانوني ما زال غير ناجح بسبب ملفات T3/T5.**
