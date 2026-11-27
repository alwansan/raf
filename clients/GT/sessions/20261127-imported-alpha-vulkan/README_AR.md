# G5 — اختبار TextureImporter PNG + Vulkan (مؤلف فقط)

رأس البدء e501998a2128a894ecaff80b7987db0f15033536. نفس PNG رمادي غير متناظر (6x4 RGBA8) مع alpha مستقل؛ 5 عمليات reimport على نفس GUID وMaterial instance؛ 8 حالات: FromInput/None/FromGrayScale linear، FromInput sRGB، wrong blend، explicit white، null binding، missing tint. قراءة CPU RGBA8 وGPU RGBA float؛ alpha target خلفية .25 لتفادي إخفاء alpha. oracle مستقل Python يولد PNG ويتحقق من hash/source/run/settings/coordinates وكل قناة، مع ضوابط فساد الإيصال. لا Unity أو أصل حتى إثبات Action فعلي. لا APK/XAPK.

