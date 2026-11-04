# ملخص فريق B — مولد من السجلات

هذا فهرس أدلة، وليس إعلان جاهزية أو نسبة اكتمال اللعبة. النسبة الكلية غير معلومة.
يُجدد في كل checkpoint؛ ليس خدمة تعمل بين الجلسات.

| المشكلة | الأولوية | الحالة | المسار |
|---|---|---|---|
| [LOCAL-005 — العالم المحلي يتوقف بعد تحميل المشهد](issues/LOCAL-005.json) | P0 | OPEN | world-save |
| [RENDER-002 — الألوان البيضاء والخامات والتكستشر والمؤثرات](issues/RENDER-002.json) | P0 | OPEN | colors-materials |
| [WATER-001 — الماء وFFT وبرامج الشيدرات الأصلية](issues/WATER-001.json) | P0 | OPEN | water-fft |
| [ASSET-RESTORE-001 — اكتمال meshes/textures/Resources/روابطالأصل](issues/ASSET-RESTORE-001.json) | P1 | OPEN | resources |
| [INTEGRATION-001 — دمج الإصلاحات والتحقق وتسليم تشخيصي منسق](issues/INTEGRATION-001.json) | P1 | OPEN | integration |
| [PERF-007 — أداء وذاكرة تحت تدفق أخطاء الرسم](issues/PERF-007.json) | P1 | OPEN | integration |
| [SOURCE-ARCHIVE-001 — اعتماد payload الأرشيف الخاص مقابلZIP2](issues/SOURCE-ARCHIVE-001.json) | P1 | OPEN | source-integrity |
| [AUDIO-REGRESSION — الصوت يعمل بحسب تجربة المالك](issues/AUDIO-REGRESSION.json) | P2 | OWNER_CONFIRMED | regression |
| [DISPLAY-003 — Settings مستقر بحسب تجربة المالك](issues/DISPLAY-003.json) | P2 | OWNER_CONFIRMED | regression |
| [INPUT-005 — التاتش والأزرار واللاي آوت مؤجلة](issues/INPUT-005.json) | DEFERRED | DEFERRED | deferred |

## الموارد ذات السجل المفصل

لكل مورد مراحل منفصلة؛ UNKNOWN لا يعني نجاحاً ولا فشلاً.

- [إصلاح cleanup في دالةBlur الأصلية — دليل سابق محفوظ](resources/blur-original-cleanup.json): acquisition=VERIFIED; extraction=VERIFIED; reconstruction=CPU_TESTED; binding=NOT_APPLICABLE; integration=MANAGED_TESTED; device=UNKNOWN

## الأحداث

- [2026-11-04 / owner-team-bootstrap](events/owner/20261104-b-generation.json): Owner replaces legacy clients with B01–B50. Preserve legacy evidence, release reservations, prioritize water/colors/local-world. Audio/Settings owner-confirmed; touch deferred. No B sessions have been started by setup.
- [2026-11-04T20:47:00Z / B50](events/B50/20261104T2047Z-local-steamstats-sourcefixed.json): SHA-pinned original SaveGame instrumentation now excludes SteamUserStats.StoreStats in Android-local mode only; C# original-source offline integration and bounded synthetic guards pass, device create/save/reload still unverified.
- [2026-11-04T21:02:00Z / B50](events/B50/20261104T2102Z-local-cheat-steamid-sourcefixed.json): Original ZIP2-pin-backed Cheat.AllowCheatsForLocalPlayer SteamUser.GetSteamID() call uses Android-local stable managed CSteamID only, Windows path preserved; six private source-probe negative controls and final original managed compilation CI pass; phone world create/save/reload still unverified.

بصمة المدخلات: 0b0ff37fba84c7fa3c5df3ab41d8e17f4906663d05031da09f352b6623eac10c
