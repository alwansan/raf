# T1 scheduled — timestamp integrity
session_id: 20261111T2007Z-T1-scheduled-chronology-timestamps-c83f
origin: scheduled
baseline_sha: 9ab95c3a0ac7a2d1c8ebf972fc35ed6b15afa9d2
scope: T1 WATER-001 CL chronology timestamp type integrity

## Sources
- Owner report: docs/DEVICE_FEEDBACK_42058825739_AR.md, run 42058825739; world entry/save/re-entry from artifact is confirmed only for that run.
- CL pinned source: alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- Previous passing diagnostic CI: https://github.com/alwansan/raf/actions/runs/43084365164 .
- Current T1 work: prompt/coordination/T_TEAM/work/20261111T2007Z-T1-scheduled-chronology-timestamps-c83f.md

## Engineering result
The existing chronology analyzer used int() on first_observed_unix_ms, which silently truncated floats and accepted booleans and numeric strings. This could manufacture an exact 2ms FFT/water gap from malformed evidence. Replaced coercion with positive exact-int validation for water, FFT, and world-loaded milestones. Added regression covering all three categories, missing field and malformed values.
- Plan commit: 0f1f7756d2bf5e7a372035ee5066ddbdd35c44f5
- Source commit: 2899d4dff63e36c847818e3f7497f5c5e05ed287
- Test commit: 52e969d41bae0289543df6594f813848bb449658
- Tests NOT executed here: local git remote failed DNS resolution; no CI requested to avoid duplicate/heavy work.
- No raw game assets published; no .meta, GUID, scene, save, or native build touched.

## Limits and next step
Source contract fix only; no proof of ComputeShader kernel identity, Unity FindKernel/Dispatch, numerical parity, GPU or device success. Next: run `python -m unittest scripts/test_t1_water_startup_timestamp_types.py` with scripts on PYTHONPATH, then rerun pinned CL chronology; investigate original FFT .compute/.meta/GUID and first divergent pass. Keep WATER-001 OPEN NOT_READY 0/3. T4 owns physical mouse; T5 owns Resolution and three controls; do not overwrite their files.
