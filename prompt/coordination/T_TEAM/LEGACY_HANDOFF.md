# خريطة انتقال العمل من B إلى T
المراجعة على58047d3b293f04547e36536518fd936ad328f4d1. قرئت ملفاتstate لجميع36 اسماًB الموجودة في هذاHEAD، مع ملخصات المشكلات والموارد والتقارير الأساسية. السجل الكامل [LEGACY_HANDOFF.json](LEGACY_HANDOFF.json) يربط الهوية والخطوة القديمة؛ هذا ليس إعلان نشاطهم الآن. المالك أوقفهم جميعاً، بما فيهم أيstate قديم يقولactive. لا حجوزات ملزمة ولا انتظار إذن منB. لا تكتب في ذاكرتهم.

## T1 — FFT
ابدأ من MEMORY للعملاء B01/B06/B08/B18/B30/B48 والتجارب المرتبطة. ثبتت20برامج أصلية وتفاصيلdescriptor/SSA وخرائطDXBC→SPIR-V المصرّح بها؛ لا تستنتج أن20compiledprograms هي20Unityruntimekernels.
[B18 آخر تحقق41931883517](https://github.com/alwansan/raf/actions/runs/41931883517) نجح في مقارنة هوية المتغيرات والكود بعد إخفاءdeclarations المحددة، لا في تشغيلUnity. التالي: runtime selection الأصلي، إنشاء.compute أصيل وربطه واختبار العدديات/الموارد ثمUnity. لا تكررcensus ناجحاً بلا سؤال مختلف.

## T2 — برامج الماء
اقرأ B09/B17 لـSpectrum، B20/B24/B25 لـFoam، وB45 معB20 لـBlur. [تقريرFoam](../../../docs/B20_FOAM_CB_DESCRIPTOR_SIZE_2026-11-04.md) يثبت اتفاقslots رقمياً، لكن7من8أحجامpartialCB تختلف عنSPIR-Vblockextent؛ هذا ليس دليلاً تلقائياً علىpadding مفقود أوبيكسل تالف. التالي: offset/type/usage وCB0 alias وsampler/upload، ثمShaderLab/install/Unity أصلي.
[Spectrum41932008860](https://github.com/alwansan/raf/actions/runs/41932008860) مصدرnamebridge ناجح، لاPixels هاتف. [Blur B45](../clients/B45/MEMORY.md) يحوي مساراًمجهزاً معgatedstaging؛ افحصه قبلعملبديل.

## T3 — الألوان والخامات والموارد
B03 أثبت1635/1635روابطRenderer→Material للأصل فقط ضمن6مشاهد؛ لم يثبتالتصدير لنفسRenderer. B05 استخرج41Material/227TexEnv وUV؛ B15 استخرج87Texture2D samplers فيsharedassets6؛ أدوات المقارنةجاهزة ولا تغنِ عنsame-export data.
B21 [41931942755](https://github.com/alwansan/raf/actions/runs/41931942755) أثبت فيتصديرفعلي bounded أنقيمومراجعمالكضوءينأصليين2/2محفوظة. لا تعِد افتراض فقدانهما لتفسيرالبياض فيالنطاقنفسه؛ بقيةالمشاهد والshader/ambient/pixelsمفتوحة.
اقرأ B02/B04/B05/B11/B12/B15/B21/B22/B31/B38/B43/B44/B46. الهدف التالي تصديرsame-instanceمنسق، تشغيلالمقارناتالموجودة ثمإصلاحdriftمثبت. لا تعِد بناءسلسلةأدواتcensusمنالصفر.

## T4 — العالم والحفظ
حواجزB50 الخاصةبـStoreStats وCheat.GetSteamID موجودةفيالمصدر معmanagedCI؛ لا تكررالpatch. B14 [41929777877](https://github.com/alwansan/raf/actions/runs/41929777877) يثبتأنالأصليناديSaveWorld ثمSaveUser ثمStoreStats؛ خطأAPK86 لايعنيأنالحفظلمتُستدعَطرقه، ولايثبتdurablewrites.
B07 coroutinefirstMoveNext وOnWorldRecieved instrumentation وحماياتB13/B14/B19/B22والدليلRGDمنB37تفيدفيالتشخيص. اقرأالأصلوالمحولالحالي واختبرالمسارالتاليالمتاح، ثمcreate/save/close/reopenحقيقيعندنُسخةمناسبة. لاWorldHasBeenRecievedوهمي.

## T5 — الدمج والمصدر والتحقق التنفيذي
أعداستعمالأدواتB03لاعتمادpayloadالأرشيف؛ لمينجزتقريرهاعينةخاصةحيةمطابقةSHA. ZIP2متاحفلاتوقفP0بانتظارالأرشيف.
[B12 أحدث41933025319](https://github.com/alwansan/raf/actions/runs/41933025319) FAILED فياختبارتنفيذcoroutineعلىsyntheticUnityscene، بينماmanagedstartup41933025251وplatform41933025184نجحا. لا تصفكلCIبأنهأخضر؛ شخّصالفشلثمأصلحهمعT3 دونإخفاءاختبار.
T5 يجمعالتغييراتويشغّلالتصديروالتحققالفعلي المناسب، ويعالجintegrationوالمواردوالاختبارات؛ ليسمراقباًينتظرتقاريرالأربعة. لا يطلبمنB موافقة، ولا يحتكراعتمادكلcommit.

## الذاكرة والتوثيق
سجّل فيwork الجديد taken_over_from بروابطالمصدر/العمل/الذاكرة، وbaseline_sha وlast_verified_result وnext_step. الذاكرةالجديدةclients/Tn منفصلة. لا تنسخذاكرةBوكأنTهوالذيشغّلها. القواعدوالتقاريرتظل منسوبةلأصحابها معدليلالاستعمالالجديد.
