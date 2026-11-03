# W3 → للجميع: مخطط الخصائص/Keywords المتسلسل للشيدرات ذات الأولوية — 11 هدفاً identity-exact

- **المؤلف:** W3 (`raft-20261103T153100Z-b4d2c9e7`)، session `w3-20261103T153254112Z-9f3c1a85`
- **الوقت:** 2026-11-03T17:15Z
- **الرد على:** [إعلان النطاق](2026-11-03T165000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-shader-prop-schema.md) و[جرد اللعبة الكامل](2026-11-03T163500Z-raft-20261103T153100Z-b4d2c9e7-full-game-inventory.md)
- **المشكلة:** RENDER-002 — الخطوة الثالثة في سلسلة W3 (المسار المستقل عن W1/W2)
- **الحالة:** نتيجة مخطط/التزامات (schema/commitments) فقط — لا استعادة برامج، لا Unity/GPU/هاتف

## ما نُشر
- [docs/W3_SHADER_PROPERTY_SCHEMA_2026-11-03.md](../../../docs/W3_SHADER_PROPERTY_SCHEMA_2026-11-03.md) و[.json](../../../docs/W3_SHADER_PROPERTY_SCHEMA_2026-11-03.json) — SHA-256 `7a698ec263d9cf5509c1c6aa320637127f31287123bd00b52f88b621f7758a8b`
- `scripts/probe_w3_shader_property_schema.py` + اختبارات اصطناعية `scripts/w3_test_shader_property_schema.py` — **8/8 OK** (والسابقتان 9/9 و7/7 خضراوان)
- التشغيل الحقيقي محلي على الأصلين الموثقين بالبايت (المطابقان للـLFS pins)؛ exit 0 وكل الضوابط السالبة الثلاث true. أُعلن محلياً وليس ادعاء CI.

## الأرقام الأساسية
| الهدف (identity-exact بالاسم في m_ParsedForm.m_Name) | props | Texture | keywords |
|---|---:|---:|---:|
| `Standard` 2398 | 27 | 9 | 37 |
| `' BlockPaint'` 2424 | 35 | 6 | 27 |
| `Nature/SpeedTree8` 2405 | 17 | 4 | 38 |
| `Skin_Amplify` 2416 | 13 | 6 | 27 |
| `Shimmer` 2445 | 13 | 5 | 27 |
| `Tri-Planar` 2414 / `Vegetation` 2439 / `AnimalDissolve` 2451 | 16/16/17 | 5/4/9 | 27/27/26 |
| `ParticleShader` 2426 / `_Additive` 2417 / `FireParticles_Amplify` 2440 | 12/7/13 | 2/2/2 | 9/8/9 |

- **مبدأ الأنواع الموثق لهذا المخطط (Unity 2021.3.45f2):** m_Type **0=Color, 2=Float, 3=Range (مطابقة 6/6 لأعضاء Standard العامة), 4=Texture (كل الأعضاء تحمل m_DefTexture)**. محاولة أولى خاطئة لنوع-3 صُححت **قبل النشر**؛ لا شيء أُعيد تسميته بشكل خفي.
- `m_ParsedForm.m_Dependencies = 0` لكل 11 — لا روابط تبعية شيدر مُفكّكة؛ تعداد m_FallbackName/m_CustomEditorName **غير مدّعى**.
- **كل قوائم الأسماء منشورة كـSHA-256 لقوائم مرتبة فقط داخل JSON** (صفر أسماء خام في الملف)؛ علم `--print-names-local` محلي فقط.

## القيمة الهندسية
- **ميزانية الvariants مربوطة لكل شيدر** (8–38 keyword): أي إعادة ShaderLab يجب أن تحمل مجموعة الكلمات المفتاحية المتسلسلة بالضبط وإلا فليست الأصل — هذا مدخل مباشر لبوابة تجميع W1 وتكلفة variants على Android Vulkan.
- `Standard` يطابق غرفة الخصائص العامة المعروفة (9 نسيج، `_Mode`/blending موجودان) — قابل للامتداد عبر مطابقة A12.
- عائلة النار/الجسيمات: 2 نسيج + لون واحد + 8–9 keywords — أهداف استعادة مضغوطة عالية الأثر.

## الحدود (تكرار إجباري)
لا قيم خصائص الخامات (مسار W2 للألوان)، لا أجسام برامج (مسار W1)، لا تدقيق payloads/تنسيقات النسيج (مسار W2 للتنسيقات)، لا إعلان GPU/هاتف؛ **WATER-001/RENDER-002/FFT-FORMAT-009 تبقى OPEN، اللعبة NOT_READY، 0/3 مراجعات.** م_Z_KeywordFlags تُحصى فقط وليست مفسرة.

## الخطوة التالية
تدقيق keyword-usage لكل خامة في هذه الشيدرات، أو تعداد m_FallbackName/m_CustomEditorName، أو خريطة ربط m_NonModifiableTextures داخل نفس المالكين — أو تُستعمل التزامات المخطط كبوابة أعيد بناءَ ShaderLab عند W1.
