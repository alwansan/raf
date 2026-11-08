# رسالة الاستعادة الكاملة — فريق Raft Android T1–T5 | نظام APK المختبر الموحد
**توجيه المالك الأخير: 8 نوفمبر 2026. يُرسل هذا الملف كاملاً لكل عميل T1–T5 في دردشته الموجودة. لا تغير هوية العامل ولا تنتقل إلى دردشة أخرى.**

## 0. استعادة الهوية والعمل الأصلي
**Stay in Chat.** ابق في هذه الدردشة العامة، واستخدم اسمك المحدد سابقاً من T1..T5. نفذ العمل هنا وأكمل التعاون مع نسختك المجدولة وفق بروتوكول الفريق؛ لا تطلب Work/Codex أو دردشة جديدة.

المشروع: https://github.com/alwansan/raf
فرع الكتابة الوحيد: feature/android-native-port
السجلات والصور للقراءة: https://github.com/alwansan/CL/tree/main/raft%20log

اقرأ بالكامل، بهذا الترتيب:
1. AGENTS.md وdocs/CURRENT_OWNER_REQUIREMENTS.md وprompt/README.md وprompt/CONTINUE_RAFT_AR.md وprompt/STATUS.md.
2. prompt/coordination/T_TEAM/RESTORE_AR.md **بالكامل**، وCHAT_AND_SCHEDULE_AR.md، وPROMPT_AR.md، وREADME.md، وOPERATING_MODEL_AR.md، وSOURCES_AND_ACTIONS_AR.md، وSUMMARY.md، وLEGACY_HANDOFF.md، وTEMPLATES.md.
3. **الأحدث والملزم للمختبر:** apk-for-testing/UNIFIED_LAB_POLICY_AR.md، وapk-for-testing/SHARED_BUILD_READINESS.md، وapk-for-testing/TEST_CENTER.md، وapk-for-testing/unified/README.md، وapk-for-testing/TESTPACK_FORMAT.md، وapk-for-testing/UNIFIED_IMPLEMENTATION_STATUS.md.
4. **الجاهزية المستقلة للعبة الكاملة:** prompt/coordination/T_TEAM/TRIAL_BUILD_POLICY_AR.md وTRIAL_BUILD_READINESS.md، وdocs/APK_BUILD_READINESS.md. لا تخلط تصويت المختبر المصغر مع تصويت XAPK الكامل أو 3/3.

تعامل مع التعليمات السابقة التي تجيز خمسة mini APK مستقلة أو تطلب تثبيتها كلها باعتبارها **تاريخية تجاوزها توجيه المالك الجديد**. احتفظ بشيفراتها وأدلتها وروابطها، لكن لا تنشئ APK جديداً باسم عامل واحد. لا تغيّر RESTORE_AR.md الأصلي؛ هذا الملف نسخة استعادة محسنة متكاملة له.

## 1. استعادة أحدث حقيقة
اقرأ live HEAD، commits، جميع GitHub Actions خاصة queued/in_progress/pending، أحدث إصدار لعبة حقيقي، أحدث CL، والفرق بين SHA المضمن في APK مثبت وما أُصلح بعده. لا تخلط إصدارات LogRaft مع اللعبة أو نجاح source/CI مع جهاز Android. اقرأ clients/<اسمك>/sessions الخاصة بالدردشة **والجدولة**، وstate.json وMEMORY.md ومعها ملفات work والـexperiments والـincidents والـissues/resources في B_TEAM الموروثة.

أنشئ session_id فريداً وسجّل origin=chat (أو scheduled عند مهمة الجدولة) وresumed_from وbase_sha وscope وintended_files وexperiment_key وresource_key وrun_urls وnext_step. قبل التعديل افحص التداخل الحي، ولا تكتب فوق جلسة أخرى. عند تعارض الرأس استخدم expected SHA ثم اقرأ وأعد دمج تغييرك المحدد بلا force أو reset لأعمال الآخرين.

## 2. ملاحظات جهاز المالك الجديدة — 8 نوفمبر
سجلات CL من LogRaft-20261108-164850-270: 74,359 ultimate_water_invalid_pass و11,165 water_fft_invalid_compute_kernel و7,372 unity_cursor_rgba32_required في جلسة واحدة؛ توجد تحذيرات أخرى عن OBB GUID وMonoScript/EventSystem. هذه أعداد أخطاء لا تقيس جودة الصورة وحدها أو مقدار الإصلاح. عند تحليل الأداء ميّز SurfaceFlinger عن Unity FPS وعن GPU busy وسجّل نافذة القياس.

**مشكلة T4 ذات الأولوية:** الماوس صار يحرك كاميرا اللاعب تحت Pointer Capture داخل Raft بشكل صحيح ولا يخرج إلى قوائم Android، لكن LEFT/RIGHT/MIDDLE CLICK وWHEEL V/H SCROLL جميعها لا تعمل في اللعبة. لا تدّع أن input كامل. افصل Android Activity/View event callbacks عن Unity Input System/Legacy mapping؛ قارن captured وuncaptured actionButton/buttonState وACTION_BUTTON_PRESS/RELEASE وAXIS_VSCROLL/HSCROLL ومسارات dispatchTouchEvent/dispatchGenericMotionEvent/onCapturedPointerEvent، وفسّر أين تُفقد الأحداث. أصلح الأزرار دون تخريب حركة الكاميرا. الصوت والحفظ ودخول العالم أثبتت لها تجربة مالك سابقة محدودة على APK أقدم؛ حافظ عليها، وافحص عدم التراجع.

**T1/T2/T3:** الماء وFFT وFoam/Spectrum/Blur والشيدرات الأصلية والألوان/النار/الإضاءة والمؤثرات لا تزال غير مقبولة على الجهاز. تجارب GLES المصغرة قابلة للفائدة لتحديد قدرات الجهاز والتحقق من عقود GPU، لكنها **لا تثبت إصلاح لعبة Raft/ShaderLab/Unity**. لا ترفع shader/raw proprietary assets أو مفاتيح أو بيانات محمية علناً.

## 3. قرار المالك: تطبيق Android مصغر واحد للفريق بأكمله
**لا تنتج خمسة تطبيقات منفصلة ولا تطلب من المالك تثبيت كل واحد وحده.** التطبيق الوحيد الجديد هو Raft Team Lab، applicationId ثابت com.alwansan.raft.lab.shared، مشروعه apk-for-testing/unified/، ومركز تحميله الوحيد apk-for-testing/TEST_CENTER.md.

يحتوي التطبيق على شاشة تعرض **T1 وT2 وT3 وT4 وT5**، وزر **AUTO ALL** لكل ما يمكن قياسه آلياً، وأزرار **AUTO T1..T5**، وقائمة **طلبات/إشعارات داخل التطبيق فقط** للخطوات التي تحتاج تدخل المالك، مع شاشة الاختبار وNEXT وFINISH. لا تقفز فوق اختبار فشل أو نقص دليل كي تختفي الإشعارات. عند إنهاء عمل فعلي وإرفاق صورته المطلوبة تختفي المهمة؛ الأخرى تبقى موجودة.

**الملف الوحيد للحالات:** apk-for-testing/unified/pack/team-testpack.json، وهو مضمن في التطبيق، ويقبل استيراد أحدث نسخة واحدة عبر SAF على Android 15. لا تفتح ملفات منفصلة لكل عامل للمستخدم. كل case له worker وcase ID وdriver وrevision وmode وscreenshot policy وتعليمات ونتيجة متوقعة. كل عامل يضيف حالاته بملف بيانات آمن موحد، وT5 يدمج النطاق المشترك مع CAS. شغّل scripts/validate_unified_testpack.py والاختبارات قبل النشر. الاستيراد بيانات declarative فقط؛ لا تنفذ dex/so/Java/GLSL/scripts أو مكتبات عشوائية من JSON أو مجلد غير موثوق. محركات جديدة تستلزم APK جديداً، بينما حالات البيانات المتوافقة يمكن استيرادها بدون إعادة بناء.

**المحركات الموجودة مبدئياً في المصدر:** T1ComputeProbe لاختبارات GLES Compute/SSBO الأربعة، T2GpuActivity لاختبارات GLES FBO الأربعة، T3LabActivity لاختبارات الألوان/alpha/sRGB الستة، وT4 physical mouse cases وT5 SAF/package/telemetry. لا تدّع أنها اندمجت واختُبرت هاتفياً قبل نجاح CI وتركيب التطبيق الموحد. شيفرات T1/T2/T3 الفردية الأصلية ونتائج CI السابقة تبقى محفوظة؛ سجلها التاريخي apk-for-testing/LEGACY_INDIVIDUAL_APKS.md.

## 4. اختبار آلي حقيقي وليس نجاحاً مصطنعاً
إذا أمكن استخراج assertion حقيقي على الجهاز، نفذه بالتتابع ومن دون طلب ضغطات. سجّل PASS فقط من نتيجة driver حقيقي، وFAIL/UNEXPECTED من الدليل الفعلي. إذا كانت التجربة تحتاج حركة ماوس مادي أو ملف OBB يختاره المالك أو تقييم صورة، سجّل NEEDS_INPUT أو EVIDENCE_READY أو NEEDS_SCREENSHOT، واجعلها في قائمة المهام داخل التطبيق، لا تحوّلها إلى PASS صامتاً.

اضبط timeout وإعادة المحاولة المحدودة، وسجّل أول خطأ وstack وcase/device/app/pack/source fingerprint. لا تعالج نقص الوصول بأن تطلب روت أو All Files Access، ولا تتجاوز فحص اللعبة بعبارات نجاح وهمية. لا تدمج Unity full game في المختبر؛ هو برنامج صغير مستقل.

**السكرين شوت:** لا تلتقط إلا إذا حدد العامل سياسة screenshot للحالة. الصور الآلية تلتقط من نافذة تطبيق المختبر نفسه (مثل PixelCopy) إلى ملف PNG حقيقي مع اسم case والتاريخ/البصمة، لا تختلق صورة أو تحاول تصوير تطبيق Raft آخر خلفه بصمت. إن لم يمكن التصوير/كانت الحالة تحتاج صورة من Raft، ضع طلباً داخلياً؛ عندما يفتح المالك الطلب أعرض الحالة والتعليمات واسمها وNEXT/FINISH، ودعه يصور أو يستورد الصورة عبر Android SAF؛ تحقق من وجود ملف الصورة بالفعل قبل إغلاق الطلب. المحتوى البصري يحتاج قبولاً بشرياً حتى لو تم التقاط لقطة آلية.

**منع التكرار:** حالة منفردة تحتفظ بنتيجة وتوقيت وبصمة الحالة وrevision/driver source والجهاز وإصدار inputs/الصورة URI/sha256. قبل إعادة تشغيلها تأكد أنها لم تتغير وأن صورة مطلوبة حقيقية ما زالت قابلة للفتح؛ إذا صالحـة فأعد استعمالها ولو تغير APK العام لمهمة عامل آخر. عند تغيرها أو فقد الصورة أعد هذه الحالة لا جميع الحالات. أخطاء سابقة لا تصبح PASS بمجرد عدم تكرارها؛ دعم force rerun تشخيصي.

## 5. السجلات ومجلد التصدير
أكتب JSONL بشكل متتابع إلى app-private أولاً، مع نتائج متكاملة وتحذيرات GPU/input/asset/exception، ثم صدّر events/summary/images إلى:

/storage/emulated/0/Download/Games/cl/test/shared-<session>/

على Android 15 استخدم MediaStore.Downloads أو SAF، بلا صلاحية Root وبدون طلب MANAGE_EXTERNAL_STORAGE. لا تعتمد على الوصول إلى Android/data لتطبيق آخر. التطبيق يستطيع تصدير logs تلقائياً بعد Auto All أو Auto Tn وعلى إيقاف النشاط، مع زر Export وإنقاذ session القديمة عند انقطاع/Crash. لا تكتب صوراً فارغة ولا تضع أنها وصلت لو فشل MediaStore. يمكن تزويد المالك بصورة أو ملف pack واحد، وLogRaft (فرع lograf) أداة منفصلة اختياريّة لا تمنح مختبرنا صلاحيات إضافية.

## 6. تنسيق العملاء وحماية الملفات
**T1:** يطوّر محرك compute واصطفاف FFT/GPU وcase IDs الخاصة به في حزمة الفريق، ويقدم دليل أصالة وحدود synthetic. **T2:** محرك FBO/Foam/Spectrum/Blur وpositive/negative controls. **T3:** محرك المواد والألوان والإضاءة والنار والparticle واختبارات السطوع واللقطات. **T4:** Android mouse event bridge وأزرار physical mouse/scroll/capture وملفات إثبات وسلوك input. **T5:** بناء التطبيق الواحد، signature/versionCode، pack merge، MediaStore/SAF، UI والأداء، حزم التوزيع والروابط.

هذه أدوار بداية لا حدود ملكية دائمة. قبل تحرير ملف مصدر مشترك/manifest/workflow/pack، تحقق من work الحي واتفق على صاحب الجزء/الملف؛ لكل عامل تعديل حالاته بمعرّف مستقل، ويُفضّل ملفات مستقلة للموديولات ثم يدمج T5 تغييرها في package واحد. لا تحول الفريق إلى خمسة أبنية CI لنفس التجربة؛ استعِد الإصلاحات المفيدة فقط من مختبراتهم السابقة. إذا لم يبق لعامل عمل مفيد دون هاتف، يسجل حالته ثم يساعد عائق زميل مستقل بدلاً من الانتظار.

## 7. تصويتان منفصلان لا يختلطان
**A. المختبر المصغر المشترك** — apk-for-testing/SHARED_BUILD_READINESS.md. كل عامل يحدّث **صفه وحده** (NEED_BUILD، NO_BUILD، WAITING_MERGE) مع سبب مختصر ودليل commit/CI ووقت UTC والجولة. إذا الخمسة NEED_BUILD فهذا إجماع. لكن **واحد NEED_BUILD حديث على الأقل** يكفي لأن يراجع T5 إطلاق **بناء Mini مشترك واحد** بعد تحقق مصدر مدمج/حاجة هاتف وغياب تشغيل أو نسخة مكافئة. لا تبن APK إن كان تحديثاً على testpack فقط قابلاً للاستيراد في APK موجود؛ صدّر الملف الموحد فحسب. لا تصوّت نيابة عن عامل آخر ولا تفتعل أصواتاً.

**B. XAPK اللعبة الكاملة** — prompt/coordination/T_TEAM/TRIAL_BUILD_READINESS.md وTRIAL_BUILD_POLICY_AR.md؛ **باقٍ كما هو** ويتطلب الخمسة (5/5) ومعاييره. الجاهزية النهائية للعبة (3/3 + إغلاق العوائق) مختلفة أيضاً. لا تسمح أن يلمس طلب Mini ملف .github/raft-native-build-request.json أو يشغّل Unity full game.

قبل بناء Mini، T5 يقرأ apk-for-testing/BUILD_REQUEST_AR.md ويستخدم فقط .github/raft-mini-lab-build-request.json بــsource parent SHA وpack SHA وrequest_id فريد ورسالة [raft-mini-lab]، بعد مراجعة queued/running Actions والتوقيع وعدم وجود Artifact مكافئ. لا تلغِ تشغيل أحد أو تصدر duplicate. لا تكرر بناء ثقيل بسبب commit شكلي أو اختلاف timestamp.

## 8. روابط التحميل الحقيقية
للمالك صفحة واحدة فقط: apk-for-testing/TEST_CENTER.md. عرّف فيها رابط **APK مباشر** صالح بالفعل بعد نجاح البناء والنشر على أصل Release يُفتح مباشرة؛ لا تسمِّ Artifact ZIP رابط APK مباشراً ولا تخترع رابطاً. ملف الحزمة المباشر:
https://raw.githubusercontent.com/alwansan/raf/feature/android-native-port/apk-for-testing/unified/pack/team-testpack.json

أرفق SHA256/bytes/package/versionCode/Build SHA/certificate fingerprint ووقت انتهاء Artifact، وتعليمات تشغيل Auto All، ومكان logs وطلب الصور. إن فشل GitHub Releases HTTP403، سجّل العائق وحافظ على Artifact ZIP كحل مؤقت مع توصيفه الصحيح ولا تعِد Unity بناء مكرر لتصحيح نشر ملف موجود. توقيع debug مؤقت قد يغيّر شهادة التطبيق بين runners ويفقد إمكانية الترقية/الذاكرة؛ T5 يجب إثبات شهادة مستقرة قبل تقديمها كقناة تحديث ثابتة.

**حدود الوضع الحالي عند إنشاء هذا الملف:** الشيفرة الموحدة والـteam-testpack موجودان في المصدر؛ لا تعتبر APK موحداً READY_TO_TEST أو Device PASS قبل تنفيذ بناء CI فعلي على SHA محدد، فحص التحميل/التوقيع/الـpackage والاختبار على الهاتف. كل نتيجة CI تخص مصدرها ووقت حدوثها.

## 9. التنفيذ وتوثيق دورة الاستعادة
بعد القراءة، قم بعمل هندسي فعلي لا تقرير شكلي: راجع أحدث evidence، أصلح/ادمج مختبرك ضمن التطبيق المشترك أو اللعبة الحقيقية حسب العائق، شغّل الاختبارات المناسبة، ثم احفظ session وwork/experiment وروابط CI وحدود الإثبات والخطوة التالية. حدّث MEMORY.md وملف حالتك **أنت فقط**، وصفك في SHARED_BUILD_READINESS.md إذا تغيّر قرارك، وأحداث B_TEAM وملخص T_TEAM بالأداة الحالية عند نتيجة مهمة. تعامل مع أخطاء بناء Mini مثل أي فشل CI: افحص أول فشل لا تتجاوز gates، حافظ على المصدر الحقيقي وشهادة التطبيق.

**عند الاستكمال التالي** اقرأ هذا الملف من الرأس الحي واستخدم نفس اسم العامل؛ التوجيه متكرر في chat والجدولة، لا ينشئ توقيتاً أو مهام خلفية. لا تسأل المالك عما وفره سابقاً من ZIP2/CL/جهاز/إذن؛ لا تعد بأنه سيحتاج خمسة APKات أو خمسة packs بعد اليوم.

**ابدأ الآن: أصلح العائق المسؤول عنه، ساعد الآخرين، وانشر أدلة اختبار قابلة لإعادة الإنتاج. إذا استحق الأمر اختبار هاتف، استخدم التطبيق المشترك والحزمة الواحدة.**
