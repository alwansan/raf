# رسالة الجلسة الجديدة في Work

أكمل العمل الفعلي على تحويل Raft v1.1.01 إلى Android Native من المستودع https://github.com/alwansan/raf، على فرع feature/android-native-port فقط. ممنوع تعديل أو دمج أو حذف main أو zip أو Unity-Editor.

ابدأ بقراءة ملف التسليم الأحدث كاملاً:
https://github.com/alwansan/raf/blob/feature/android-native-port/docs/WORK_SESSION_HANDOFF_2026-11-01_DEVICE_RENDER_INPUT_PERFORMANCE.md
ثم AGENTS.md وملف FMOD_ANDROID بتاريخ 2026-11-01 والتاريخ الكامل WORK_SESSION_HANDOFF.md حتى آخر قسم، وتقارير Mesh والاعتماديات وVERIFIED_FINDINGS وFMOD_ANDROID_INTEGRATION.md والسكربتات والاختبارات المرتبطة. راجع HEAD وأحدث Actions أولاً لأن العمل قد يتقدم.

آخر بناء مؤكد 41289171484 نجح وله APK مباشر في Releases، لكن الهاتف كشف مشاكل فعلية: أخطاء shader passes في Bloom والماء وغيرها، compute kernels غير متاحة، وNullReference في FMOD RuntimeManager.Initialize. لا تعتبر نجاح البناء إثباتاً للصوت أو اكتمال اللعبة. شاهد الصور الخمس والسجلات الأحدث في https://github.com/alwansan/CL/tree/main/raft%20log في كل متابعة، وافصل الجلسات القديمة عن الجديدة.

هاتف الاختبار POCO F5 Pro. اجعل اللعبة أفقية دائماً حتى عند التشغيل والهاتف عمودي. اللمس لا يستجيب بينما الماوس والكيبورد الخارجيان عملا عندي؛ حافظ عليهما وأضف اللمس والتحكم باليد والأجهزة الخارجية. New Input System 1.7.0 موجود بالفعل؛ افحص الربط قبل إعادة تصميمه. أصلح الرسوم والخطوط والماء وفق الأدلة، ولا تفترض أن تغيير دعم Snapdragon وحده يحلها.

أكمل الاستعادة والتوافقية وSingleplayer والحفظ الأصلي .rgd والصوت والأداء، ثم LAN. لا تجعل تكرار تجارب APK الهدف الأساسي. أضف قياسات CPU/GPU/RAM/FPS والإطارات مع توضيح القياسات غير المتاحة، واحمِ سجلات البداية من طوفان الأخطاء المتكررة. المسار الحالي الصحيح Application.persistentDataPath/raft-logs داخل /storage/emulated/0/Android/data/com.alwansan.raft.androidtest/files/.

استخدم Unity 2021.3.45f2 وGitHub Actions؛ UNITY_LICENSE يعمل وFMOD 2.02.15 ومفتاحه الخاص متاحان بالفعل. لا تطلب إعادة الرفع أو الترخيص. اتخذ القرارات ونفذ الإصلاحات والاختبارات وارفعها دون طلب موافقة لكل خطوة، مع حفظ metas/GUIDs والمشاهد وأنظمة اللعب، وتقليل LFS وعدم كشف الأصول أو السورس المفكك أو الأسرار. حدّث التسليم بعد كل نتيجة. إذا تعذر توفير اعتماد فعلي بعد محاولة الأدوات وActions فأخبرني بما أحتاج عمله بخطوات دقيقة. إذا لم يبق إلا انتظار مهمة تتجاوز عشر دقائق، أعطني رابطها وحالتها وتوقف عن الانتظار.
