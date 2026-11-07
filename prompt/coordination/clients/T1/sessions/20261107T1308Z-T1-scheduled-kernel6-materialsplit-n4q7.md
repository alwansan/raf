# T1 session 20261107T1308Z-T1-scheduled-kernel6-materialsplit-n4q7
origin: scheduled
base_sha: e0c48cee6c0d22b4ad193d3a795f1cc87fcbc792
resumed_from_sessions: 20261107T1211Z-T1-scheduled-cl-timing-f8c2; 20261107T1005Z-T1-scheduled-first-mismatch-b4e9
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner confirmed world enter/save/reopen from artifact 42058825739; release publish failed.
work: prompt/coordination/work/WATER-001/20261107T1308Z-T1-scheduled-kernel6-materialsplit-n4q7.md
result: pinned CL final_render_failure_breakdown reveals invalid FFT compute kernel index 6 exclusively in both sessions (3850 and 6026 roots) and Ultimate Water invalid passes only Spectrum (8484,15028) and Foam Global (15400,24104). Counts sum to final 23884 and 39132. First timestamps separated by 2ms but no proven causality.
report: docs/T1_WATER_KERNEL6_MATERIAL_SPLIT_2026-11-07.md
source: alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57, two session-summary.json files; metadata-only, no raw proprietary resources.
commits: scope b63778266c9f11ae329a5c782b33578ef3b65eae; report 43844aed5eb28b36ba59f85a732a6fc3deec2e86.
checks: source category sums verified; no Unity/Android/FFT numeric comparison, no Actions launched; T4 mouse and T5 UI/Resolution unchanged; trial vote T1 remains no-needs until substantive device-testable fix.
limitations: summaries lack exact first raw error text and actual Unity FindKernel/Dispatch name/ID; kernel integer 6 is not an original shader program identity. WATER-001 OPEN, NOT_READY 0/3.
next: extract first distinct raw error message and C# stack from pinned CL segments using bounded private streaming; instrument authenticated Unity FindKernel/Dispatch and Spectrum/Foam pass metadata, then paired FFT trace comparison.
