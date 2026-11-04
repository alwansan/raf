# T3 memory — 20261104T2354Z-T3-render-harness

Identity: T3; generation T-2026-11-05; writable branch only `feature/android-native-port`.
Baseline HEAD: `b56ebc3847f251cee2539e9797471417d32698d2`; prior owner migration baseline `58047d3b293f04547e36536518fd936ad328f4d1`.

## Initial reading and inherited evidence
Read T_TEAM/PROMPT_AR, README, OPERATING_MODEL_AR, LEGACY_HANDOFF, MIGRATION, TEMPLATES, SUMMARY, source policy, AGENTS, owner requirements, source provider and B03/B05/B12/B21 records. No active/queued Actions observed in recent run collection at startup; oldest latest real game Android release is APK86 tag `android-early-test-41812889049-1`, source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`. Newer `lograf-*` releases are separate.

Inherited B03: six original scenes 1,635 non-null Renderer→Material identities verified **on original only**; B05: 41 Material/227 TexEnv/227 UV slots from original sharedassets6, but no actual same-instance export parity. B21: two original Light identities/properties survived bounded actual same-instance export; do not blame these lights. Source archive not proven byte identical. B12 one-shot bounded production scene diagnostics needed to distinguish white shader/material/mesh defects in next APK; CI 41933025319 FAILED in managed harness compile.

## Working plan (recorded before editing code)
Fix B12's current synthetic execution guard without weakening source method assertions. Exact CI log reports unresolved `ComputeShader`, `Resources`, `Encoding` symbols because the extracted production code now references B18 `LoadedComputeShaderSnapshot`. Add minimal no-game-object stubs and namespace imports; ensure synthetic log records only render entry while still allowing water diagnostic; add fail-closed expectation that real production compute probe remains present. Preserve the 8 budget controls; do not change production diagnostic or actual Unity resources. Test via local Python harness/source and, when possible, dotnet or isolated CI. Then return to original/export same-instance mapping with B03/B05 tools; only repair a measured mismatch.

No raw original assets, .meta/GUID, Steam, Settings, audio, touch, or delivery requests to be changed. RENDER-002 stays OPEN; this harness repair alone is not a graphics fix, Unity/phone/FFT proof, or READY.

## Resume
Fetch current HEAD and tests; inspect whether another T agent fixed the harness; update this memory with patch SHA, exact checks, CI outcome, next material export experiment. No hidden ongoing work.
