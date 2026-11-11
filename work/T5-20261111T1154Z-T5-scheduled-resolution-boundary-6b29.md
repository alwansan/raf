# T5 independent scope — 20261111T1154Z-T5-scheduled-resolution-boundary-6b29
origin: scheduled
baseline_head: 237855531cca5025e91ca7f323773dfdc5107a5b
issue: DISPLAY-003 / signed delivery and phone performance
scope: read-only original resolution binding audit; no T4 physical mouse or Unity build
files: docs/T5_RESOLUTION_ANDROID_POLICY_REVIEW_2026-11-05.md; docs/T5_ORIGINAL_RESOLUTION_APPLY_CALLERS_2026-11-06.md; android-port/Experiments/T5/ResolutionApplyProbe/Program.cs; scripts/t5_validate_resolution_apply_callers.py
hypothesis: static original Apply caller evidence does not yet authenticate serialized dropdown callback and preference-to-render-scale binding. A speculative production patch risks changing physical display mode and breaking working Settings.
experiment_key: T5-RESOLUTION-SERIALIZED-BINDING-GAP-20261111
shared_resource: none (no Unity/CI requested)
coordination: T4 retains physical mouse; no changes to shared code or other agents' files.
result: original compiled evidence shows 3 same-class direct Apply callers, one dropdown-heavy caller, no direct external callers, and 1 SetResolution site; it does NOT prove Android render-scale selection or persistence. Source-only right-panel CI 42998052750 passed previously, but not a phone test.
next: inspect authenticated serialized UI binding in original scene/prefab privately, identify callback and preference persistence, then implement Android-only aspect-preserving render-scale choice in existing Settings; keep DynamicResolution separate. Signed APK/OBB full SHA and controlled LogRaft phone measurements remain open.
