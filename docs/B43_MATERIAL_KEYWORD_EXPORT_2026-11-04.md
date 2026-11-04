# B43 Material keyword fidelity — 4 November 2026

The W3 source census proves Standard uses seven configured keyword strings across 674 materials (including 22 base-variant materials). An export can retain the correct Shader GUID and texture references while dropping or modifying its per-Material keyword/pass configuration. This is distinct from B02 import sRGB, B44 SavedProperties, and B46 texture references.

B43 adds a read-only verifier on SHA-pinned original 14 Shader-owner files and the SAME-instance private exporter trace. It joins original Material object identity to actual exported YAML anchor and meta GUID, not generated names or guessed GUIDs. It compares sorted original/export multisets for m_ValidKeywords, m_InvalidKeywords and disabledShaderPasses, and fails closed on unsupported YAML, missing originals/documents, redirects that are not engine transport pointers, duplicate source/export identities or content mismatches. Implicit fonts are excluded from comparison and counted. It outputs only safe aggregate counts and abstract status codes, never original object names, raw values, IDs or private material paths.

Reproduce when a real private export is available:

    python3 -m scripts.b43_material_keyword_fidelity --source /private/input --private-trace /private/trace.json --project /private/ExportedProject --out /private/report.json

The independent B43 workflow uses synthetic tests, no LFS, Unity or private data. The real source+same-export comparison has not run, so the verifier is diagnostic-only; it has NOT been installed into a shared native gate. No shader programs, Material values, pixels or game behavior have been changed or verified. RENDER-002 stays OPEN, NOT_READY, 0/3 readiness reviews. Audio/Settings/touch and native request remain untouched.

## B43 executable validation — 4 November 2026
[First B43 code 9a918009](https://github.com/alwansan/raf/commit/9a918009c18332fa3bc176ebd008c6dd5eba7baa) [CI 41913711656](https://github.com/alwansan/raf/actions/runs/41913711656): 14 synthetic controls PASS. [Fixture expansion 8f9ecde](https://github.com/alwansan/raf/commit/8f9ecde1fc82808af79fdc6194a211c2560c1398) [CI 41914188268](https://github.com/alwansan/raf/actions/runs/41914188268): 17/17 PASS; adds actual temporary Unity Material YAML and .meta path parsing and a deliberately altered keyword rejection. No real game source/export/pixel parity has been tested. Real signed private same-process trace remains required before production gate adoption; RENDER-002 OPEN and NOT_READY 0/3.
