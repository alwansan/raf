# B45 — 20261104T2056Z-B45-f0c1

## Scope
WATER-001: authentic original two-pass UltimateWater Subsurface Blur restoration. Original ZIP2 pinned source 15964ea8f246b6e076ce26b60931ee2e1a9a2385; feature/android-native-port only. Preserve audio/Settings/LEFT Mouse0; no touch work, native request or full APK.

## Live source and evidence
Read B_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, SOURCES_AND_ACTIONS_AR.md, REVIEW_2026-11-04.md, TEMPLATES.md, SUMMARY.md, AGENTS.md, CURRENT_OWNER_REQUIREMENTS.md, prompt README/CONTINUE/STATUS and ZIP2_SOURCE_PROVIDER. Baseline HEAD f835f66c67fba9cf36fdbc9f49793b7b8f06b12a at first read; later concurrent B50 commits require refresh before mutation. Latest game APK86: https://github.com/alwansan/raf/actions/runs/41812889049 ; CL source 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29 and 4 Nov screenshots, session-summary/segment3 reviewed through team review. Original W5 run 41821419074 at 7764fd7: both Blur passes (three seeds each) positive within tolerance, negative controls true; then ValueError, after raster phase, without private candidate or Unity import. B50 independently handles LOCAL-005 Steam source, so no shared modifications.

## Hypothesis
The W5 failure is after original stage recovery / per-pass numeric raster, likely original ShaderLab state or other wrapper serializer unsupported shape. Error phase not isolated. First isolate without releasing shader/source, then implement only a proven original state serialization repair with synthetic controls. No claim of authentic Android pixels.

## Test/limits
Known W5 tool stage checks do not imply Unity/adreno/device acceptance. Must maintain original SHA256 and original pass/state, property identities and meta/GUID. Workflow needs unique B45 group, timeout and safe aggregate output only.

## Next
Record B45 work/experiment and run bounded preflight, repair exact classification and check CI; sync state/issue/events/SUMMARY at checkpoint.
