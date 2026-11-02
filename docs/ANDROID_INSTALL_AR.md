# تثبيت نسخة Raft التجريبية من الهاتف

الأولوية اكتمال بيانات اللعبة، وليس صغر حجم التنزيل. نجاح البناء لا يثبت عمل الماء والصوت والحفظ واللمس على الهاتف.

## اختر مسار تنزيل واحداً

- **XAPK**: يحتوي APK وكل OBB المطابق له، دون تعديل بايتاتهما. افتحه بمثبّت XAPK يدعم ملفات OBB وصلاحيات وضعها في مكانها على إصدار Android لديك. XAPK ليس APK عادياً يثبّته Android تلقائياً؛ امتداد الملف وحده لا يضمن التثبيت. دعم ZIP64 ونسخ OBB على Android15 يحتاج تحققاً فعلياً من المثبّت.
- **APK + OBB**: ثبّت APK وانقل OBB المطابق إلى `Android/obb/com.alwansan.raft.androidtest/` باسمه الكامل `main.<versionCode>.com.alwansan.raft.androidtest.obb`. إذا كان `companion_required` في `delivery.json` يساوي true، فـAPK وحده غير مكتمل. لا تخلط ملفات بناءين مختلفين.
- لا تحتاج تنزيل XAPK وAPK+OBB معاً؛ المحتويات متطابقة وهما طريقتان بديلتان للتسليم.

## إذا وجدت أجزاء `.part001` وغيرها

GitHub يسمح بأقل من2GiB لكل ملف Release، حتى إذا كانت اللعبة أكبر. لذلك قد يكون OBB أو XAPK منشوراً كأجزاء نقل1GiB. الأجزاء ليست ملفات OBB جديدة للعبة، وليست ملفات قابلة للتثبيت منفردة. تجمع إلى الملف الأصلي المطابق تماماً قبل التثبيت.

نزّل كل الأجزاء الخاصة بالملف الذي اخترته، ومعها `delivery.json` و`reassemble.py` إلى مجلد واحد. من Termux، بعد منح الوصول للتنزيلات:

```bash
termux-setup-storage
pkg install python
cd ~/storage/downloads
python reassemble.py Raft-Android-Test.xapk
```

استعمل Python3.11 أو أحدث. إذا وضعت الملفات في مجلد داخل Downloads فانتقل إليه بدلاً من المجلد أعلاه. لضم OBB استعمل اسمه الكامل الموجود في `delivery.json` بدلاً من اسم XAPK. الأداة تتحقق من طول وبصمة SHA256 لكل جزء ثم طول وبصمة الملف الكامل، وترفض الملف الناقص أو التالف أو الكتابة فوق ملف موجود. احتفظ بمساحة إضافية بحجم الملف الكامل أثناء الجمع. لا تحذف الأجزاء قبل نجاح التحقق.

إذا نُشر ملف `.xapk` أو `.obb` كاملاً فلا يحتاج إلى جمع. `SHA256SUMS` يصف الملفات التي نُشرت بالفعل.

## إذا منع Android15 وضع OBB

لا تمنح الصلاحيات عشوائياً ولا تفترض أن أي مثبّت يستطيع تجاوز قيود Android. يمكن استعمال مثبّت يدعم OBB مع آلية الوصول المسموح بها على جهازك، أو ADB اللاسلكي من Termux دون PC:

```bash
pkg install android-tools
adb pair PHONE_IP:PAIRING_PORT
adb connect PHONE_IP:DEBUG_PORT
adb shell mkdir -p /sdcard/Android/obb/com.alwansan.raft.androidtest
adb push main.VERSION.com.alwansan.raft.androidtest.obb /sdcard/Android/obb/com.alwansan.raft.androidtest/
```

استبدل IP والمنافذ بالقيم المعروضة في خيارات المطوّر > تصحيح الأخطاء اللاسلكي، وأدخل رمز الاقتران على هاتفك فقط. منفذ الاقتران قد يختلف عن منفذ الاتصال. استبدل اسم OBB بالاسم الفعلي من الإصدار، ونفّذ الأمر من مجلد تنزيل الملف بعد جمعه إن كان مجزّأً. التثبيت ونسخ OBB بهذه الطريقة يحتاجان تجربتك؛ لا يعتبران مثبتين بمجرد نجاح CI.

## التحكم والتقرير

افتح Test report ثم Enable touch gamepad. لتخصيص مواضع وأحجام وشفافية وربط الأزرار اختر Edit touch layout. التحكم ما زال تجريبياً وقد لا يستجيب كل فعل. الماوس والكيبورد والكونترولر الأصليون محفوظون.

بعد التشغيل، سجلات التطبيق في Application.persistentDataPath/raft-logs. أرسل التقرير وسجلات الجلسة عند توفرها؛ التطوير المستقل يستمر دون اشتراط تجربتك في كل خطوة.

## الصيغ والحدود

لا ننشئ APKS بمجرد تغيير امتداد ZIP. صيغة bundletool الرسمية تحتاج مجموعة APKs صحيحة وبياناتها الوصفية، ولا تحل نقل OBB تلقائياً. في المسار الحالي XAPK وAPK+OBB يخدمان المطلوب دون اسم مضلل. لا نقسم أرشيف Unity إلى ملفات OBB عشوائية؛ أي تقسيم حقيقي للموارد يحتاج دعماً من تحميل اللعبة، بينما تجزئة النقل أعلاه لا تغيّر تشغيلها.

المصادر: https://developer.android.com/tools/bundletool ، https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases ، https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0145/ .
