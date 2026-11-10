# GFX-LAB — 20261110-GFX-chat-glsl-source-evidence-08
- session_id: `20261110-GFX-chat-glsl-source-evidence-08`; origin=`chat`; resumed_from=`20261110-GFX-chat-unused-program-platform-07`
- base_sha: `b43b9258dda3db785abcda7dbcf76606212960d0`; source ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`
- experiment_key: `GFX-MULTI-034`, scope: verify if unlinked 139 GLES + 120 GLCore source programs contain bounded UTF8 GLSL with authored Shader48 property identifiers and uniform names.
- status: IN_PROGRESS; private source-only. No new Android APK or artifact with shader code; no T-team branch edits.
## Background
[GFX-MULTI-033 CI42808967835](https://github.com/alwansan/raf/actions/runs/42808967835) SUCCESS 205 tests: unused programs 139 GLES, 120 GLCore, 9 DX9, 1 other; alternate original Pass prog* rows 0; no leading direct version/SPIRV. The UnityPy public ShaderSubProgram exporter `UnityPy/export/ShaderConverter.py` interprets GL-family code as text. Check actual source privately.
## Boundaries
Even exact token or uniform name match in unlinked text is only candidate source semantic evidence, **NOT linked original shader runtime** or original DX11 t/s/CB offsets. Never disclose private GLSL, raw property names or source indexes.
## Runs / result
Pending.

## GFX-MULTI-034 implementation and CI checkpoint
- Private inspector `gfxlab/tools/multi_shader_glsl_text_property_evidence.py` with 27 authored Shader48 property labels, nine texture properties, and 21 original bound Texture2D roles (source-only). Strict UTF-8, comment-stripped exact identifiers and bounded uniform-statement matching; no names/code in public report.
- Source-free tests `gfxlab/tests/test_multi_shader_glsl_text_property_evidence.py`; pinned-ZIP2 workflow `.github/workflows/gfxlab-multi-glsl-text-props.yml` safely purges source.
- Initial [CI42809825046](https://github.com/alwansan/raf/actions/runs/42809825046) failed **source-free synthetic test fixture only**: supplied an empty mock compiled table and asserted property guard instead of table-count guard; private source not checked and purge step passed.
- Corrected test to supply valid 1656-slot fixture before checking wrong property set. [CI42809913702](https://github.com/alwansan/raf/actions/runs/42809913702) source-free test **SUCCESS**, original ZIP2 scan in progress at checkpoint. No claim yet of original GLSL text or GPU equivalence.

## GFX-MULTI-034 confirmed terminal (2026-11-10)
- Initial [CI42809825046](https://github.com/alwansan/raf/actions/runs/42809825046) synthetic fixture failure fixed, no original source scanned. Corrected run: [GFX-MULTI-034 CI42809913702](https://github.com/alwansan/raf/actions/runs/42809913702) **SUCCESS**, 210 source-free tests, SHA-pinned original ZIP2, private cleanup passed. Across **139 unlinked GLES** type entries, strict UTF8 54, invalid UTF8/binary 85, embedded NUL 115. Across **120 unlinked GLCore**, strict UTF8 33, invalid UTF8 87, embedded NUL 106. Neither family had verifiable simple GLSL `#version`, `void main`, `uniform` or `sampler` declarations under full strict UTF8 plus comment-stripped matching. GLES only: 6 programs with exact source Shader48 property-token occurrences (3 unique authored properties, 3 unique texture properties, 1 unique bound texture property); **0 authentic Uniform property bridges**. GLCore 0 property tokens. No exact original Pass/keyword/tier links, no DX11 t/s/CB map, no GPU/PC pixel parity. Source bytes/proprietary names remain private. Artifact [13760603589](https://github.com/alwansan/raf/actions/runs/42809913702/artifacts/13760603589) expiry 2026-11-17T11:45:19Z.
- Meaning: typed GLES/GLCore entries may contain wrapped/binary content; UTF8 validity and property-token presence do not prove there are compilable original GPU programs. Next GFX-MULTI-035 inspect safe **byte-level embedded ASCII markers and bounded framed text** in 259 GL candidate payloads without publishing source.
