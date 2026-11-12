# GFX-LAB — GFX160 اختبار FFT عبر textures

`session_id=20261112-GFX-chat-water-fft-textures-120` · `origin=chat`

مشروع Unity 2021.3.45f2 مستقل على Vulkan ARM64. ثلاثة kernels: أفقي، عمودي، وقراءة. تمريرتان radix-2 inverse FFT على 32×32 مع وسيط وخرج R32G32_SFloat. أربع حالات، 4096 قيمة، إخراج ZIP آلي. مرجع CPU أعاد إنتاج الخوارزمية وقارنها بالتعبير المغلق عند الحالات الأربع بأقصى فرق 1.61e-15. ذلك فحص CPU، لا إثبات Adreno. [بناء GFX160](https://github.com/alwansan/raf/actions/runs/43148270805).

فرع اللعبة المقروء `a194dce61daeeb1d667f3e7d306d48c2f2bbc954`: قارنت قوائم T5 الحالية ووجدت 18 ملفاً في كل مسار دون اختلاف، وهو دليل source-only على معالجة عدم تطابق القوائم السابق. تقرير البناء 42696228231 سجل Blur 2/2، Spectrum 1/6، Foam 1/2، Depth Copy 9 عبر SubShaders [6،3]، و0 compute مصادر ماء مؤهلة. مقتطفات CL تثبت طلب Depth Copy index 4 أيضاً، وبالتالي الحد الملائم لذلك المسار 5، بينما ثابت native الحالي 4. لا إثبات لاختيار SubShader على الجهاز ولا لتسجيل FFT الأصلي. تجربة GFX160 تسبق إعادة بناء اللعبة لتفريق دعم Vulkan/RGFloat عن استيراد الأصل.

البناء نجح. APK موقع v2، CRC وARM64 IL2CPP وSHA بعد التنزيل متحققة. [الأثر 13912318730](https://github.com/alwansan/raf/actions/runs/43148270805/artifacts/13912318730)، SHA256 `c758b6e08a5249ae94e154f76ab347cdf6587927ac517a77388f6d3f97bcc404`. انتظر ZIP `GFX160-ALL-TEST-LOGS-*.zip` من هاتف المالك في Download/Games/cl/test/g، حتى عند فشل الهاتف. اختبار Android غير منفذ بعد. لم نطلق XAPK من هذه الدورة.
