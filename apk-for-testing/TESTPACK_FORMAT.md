# صيغة testpack.json v1

كل pack ملف JSON بيانات فقط. الحد الأقصى 64KiB، ومن 1 إلى 20 اختباراً، دون تنفيذ ملفات Java/DEX/so/scripts من حزم مستوردة.

الحقول: `schema_version:1`, `worker:T1..T5`, `pack_id` آمن، `title`, `version`, `source_sha` (40 lowercase hex أو null للعرض التعريفي)، و`tests` تضم `id, type, title, instructions, expected`، و`asset`/ `sha256` اختياريان. الأنواع المتاحة في host العام: `note, mouse, file_sha256, image_preview`. Asset مجرد مسار بيانات نسبي آمن؛ اختيار الملف يتم عبر نظام Android SAF ولا يُقرأ بشكل عشوائي. GPU shader/mesh/Unity experiments تحتاج renderer مُجمّعاً داخل mini APK مخصص، ولا يمكن تشغيل PC DXBC بالنص المستورد.

[مثال T4](examples/t4-mouse-testpack.json) | [تعليمات](LAB_PROTOCOL_AR.md) | validator: `python3 scripts/validate_android_testpack.py apk-for-testing/examples/t4-mouse-testpack.json`.

لا يتم إصدار روابط تنزيل APK حتى تثبت الحزمة الفعلية والـSHA256 على GitHub Artifact/Release.