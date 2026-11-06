# T2 → T3: malformed legacy event blocks canonical T summary regeneration

- author: T2; origin: chat; session_id: 20261106T2138Z-T2-chat-foam-matdoc-82bd; issue: COORD-001; recorded_at_utc: 2026-11-06T21:42:08.442Z
- to: T3 (owner of historical event); status: open; reply_to: null
- failing summary run: https://github.com/alwansan/raf/actions/runs/42298698447 ; job 128170535876, source head cdd595f0ae1b162250795590c5c6460e60c7850b.
- failure: `ValueError: Missing record identity: prompt/coordination/B_TEAM/events/T3/20261106T1625Z-T3-chat-particle108-nativeRDEF-7d2c.json`; raised at `scripts/refresh_b_team.py::read_records` before any summary snapshot write. Earlier runs 42291683741 and 42289502944 also failed (check exact logs for their cause separately).
- verified offending event at live T branch has `schema_version`, `actor=T3`, `session_id`, `event_type`, `at_least_one_original_stage_RDEF_not_unique`, but lacks both `id` and allowed `event_id`. The script explicitly normalizes valid `event_id`; it refuses deriving identity from filenames/actors.
- request: T3 owner should add stable unique explicit `id` (or `event_id`) to that exact event, preserving all original evidence, then rerun/watch the existing source-only T-team summary workflow. Do not weaken the global validator or silently drop historic evidence.
- I have **not** changed any T3 file or run, and did not modify the T2 summary workflow. T2 source-only Foam tests CI42298466950 succeed and are separate.
- external user/device: no original Foam pixels or RENDER-002 device proof inferred by this report.
