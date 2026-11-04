# B37 — authenticated original cursor-callsite provenance (2026-11-04)

Scope: a **separate non-water rendering/log-flood symptom**, not Unity touch controls, buttons, layout, audio, or Settings. The current priority of original water/FFT and white material restoration remains higher.

## Evidence and verified result

The read-only CL log summary for installed APK86, session \`20261104-225757-156\`, source CL commit \`5394407b5cd0a0ca1848ff0902f8d2133bf6ea29\`, records **1,449** \`unity_cursor_rgba32_required\` warnings. This is the old game version, not source-modified Android proof:
https://github.com/alwansan/CL/blob/5394407b5cd0a0ca1848ff0902f8d2133bf6ea29/raft%20log/lf/LogRaft-20261104-225757-156/session-summary.json

B37's isolated [original-source CI 41926487471](https://github.com/alwansan/raf/actions/runs/41926487471) **SUCCESS**, immutable tested source \`2e42cc325403140b4c4bcb5ef2dc2d0d4e829a02\`: exact original managed Assembly-CSharp.dll, 3,211,776 bytes, SHA256 \`0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e\`, privately decompiled by pinned ILSpy 11.2.0.10050; all **2,394 C# files** scanned with comment/string masking. **3** direct lexical \`Cursor.SetCursor\` calls in **2** source files, no \`using static Cursor\` alias directives, and **six of six** source-free negative controls passed. Caller identity is represented only by SHA256 digest \`4df6ae990786151b4c613b17af96e9f6b4a74d158306d01326d318bc3987bcca\`. [Sanitized aggregate artifact](https://github.com/alwansan/raf/actions/runs/41926487471/artifacts/13370195464) (no original C# or file names).

The primary goal is to discriminate whether actual non-null pointer texture callsites exist; source lexical presence alone does not prove these calls executed on Android, caused Unity's warning, or were invoked 1,449 times. The follow-up argument-classification version was committed as \`ecb4838da2b9a2b2aa49d761e6c4926807f2d966\` plus negative cases \`99c7774d7e6100f62a43a31120f4fec3618482f4\`; check the associated Actions results and record null/nonliteral counts, without leaking private arguments.

## Guardrails and next action

Do not change original cursor textures, imports, alpha/sRGB, source shaders, input/touch/virtual Xbox layout or fake cursor texture success. When source-bound argument types and a future *new* APK device warning are available, prove whether the current source calls produce unsupported \`Texture2D\` formats and only then design a color-preserving, narrow Android correction. If a call is \`SetCursor(null,...)\`, do not count it as a texture-format producer. Preserve all original .meta/GUIDs and project asset data.

No Unity build, new APK, on-device test, water reconstruction, world save round-trip, graphics pixel comparison or owner acceptance is claimed. WATER-001/RENDER-002/LOCAL-005 remain OPEN; readiness is NOT_READY, 0/3 full independent immutable reviews.
