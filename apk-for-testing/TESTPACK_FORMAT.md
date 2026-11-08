# حزمة team-testpack.json v2 — جميع العملاء في ملف واحد

المصدر الموحد: apk-for-testing/unified/pack/team-testpack.json، والتنزيل المباشر:
https://raw.githubusercontent.com/alwansan/raf/feature/android-native-port/apk-for-testing/unified/pack/team-testpack.json

الجذر JSON: schema_version=2 وpack_id وrevision وsource_sha وtests[] (1..100). لكل حالة id وworker وdriver وrevision وmode وscreenshot وtitle وinstructions وexpected. العمال T1..T5 والـcase ID ثابت ويخص عامله. mode: auto / assisted / manual. screenshot: none / auto / manual / optional.

T1Compute: 4 حالات GPU حقيقية GLES synthetic، T2 GLES FBO: 4، T3 material/render: 6 مع screenshot، T4 mouse: 9 حالات تحتاج إدخال فعلي، T5 identity/SAF/performance: 6 حالات متفاوتة. مجموع 29. لا تدّع إصلاح Unity/ShaderLab من نجاح اختبار GLES synthetic.

الحزمة بيانات JSON فقط، لا تسمح بتحميل dex/so/Java/GLSL executable أو تشغيل أكواد غير موثوقة. لا يمكن إعادة تعريف محرك GPU عبر استيراد JSON وحده؛ يحتاج دمج driver compiled في APK جديد. استخدام SAF/MediaStore على Android 15 بلا MANAGE_EXTERNAL_STORAGE.

تُعاد الاختبارات إذا تغيّر الـcase أو بصمة source driver أو الجهاز أو فقدت صورة مطلوبة، وليس بسبب تحديث غير متعلق بالعامل. الشاشة الآلية تخص نافذة التطبيق نفسه ولا تصور Raft خارجه صامتاً.

فحص الحزمة: python3 scripts/validate_unified_testpack.py apk-for-testing/unified/pack/team-testpack.json
اختبارات التراجع: python3 -m unittest discover -s tests -p test_unified_testpack.py -v
