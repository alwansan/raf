# T3 scheduled — streamed Texture2D manifest extent safety guard

- session_id: `20261105T2230Z-T3-scheduled-streamrange-9c62`; origin: **scheduled**; identity: **T3**.
- issue: RENDER-002 OPEN; readiness: **NOT_READY**.
- resumed_from: `20261105T221843Z-T3-chat-particle28-stream-7c49` (authenticated 3 source Texture2D28 targets with external m_StreamData); `20261105T213100Z-T3-scheduled-clstage-8b4f` (water errors precede world loaded).
- baseline SHA: `cb649454069ff110d1d16393391fd15a2259e3cf`; first attempted plan write was rejected with expected `ff938dbe4a0db6e6dac5d2808c944ee882415cf7` due to concurrent T2 advance, then HEAD was reread and scope registered at `c978f275f04b580d16594c34ea542fa49c568bd2`. No force.
- work file: `prompt/coordination/work/RENDER-002/20261105T2230Z-T3-scheduled-streamrange-9c62.json`.
- experiment key: `T3-synthetic-stream-extent-overlap-guard-v1`; resource key: CPU-only, no ZIP2/Unity/CL private data.
- code commits: `ba7448cdf2ada697d0eeb674e645bd3d821b4c10` and `2a9ad84dd0813ddb068ca3415e9d10d1653d2006`.
- New `scripts/t3_stream_extent_guard.py` checks provider metadata and offsets using subtraction-based range bounds, rejecting invalid types, missing providers, zero/negative lengths, and overrun. It reports partial overlaps separately from legitimate exact shared ranges, without exposing asset names.
- New `tests/test_t3_stream_extent_guard.py` covers nine source-free cases. Equivalent local Python unittest harness: **9/9 PASS**. GitHub CI **not verified** for these commits. No authentic provider manifest was fed into this new helper.
- Actual device report: owner verified world entry/save/re-entry on artifact run 42058825739; menu/raft/hand white and square smoke remain. Latest chat source CI 42120918486 showed three original Texture2D28 objects whose stream extents fall inside the immutable manifest, but external .resS bytes were not staged in that experiment. This helper does not establish missing APK/OBB texture bytes or fix white graphics.
- Concurrent T2 foam run 42121817207 was in progress when checked. No Action cancelled or duplicate original experiment launched. No game shaders, .meta, GUIDs, save, sound, Settings, touch, mouse, or resolution changed.
- Next: coordinate with T5 and chat T3 to validate exact three original stream extents against authenticated external provider byte length and hash, then trace same-instance exported Texture2D GUIDs and actual installed APK/OBB before claiming pixel causes. Do not duplicate expensive source export without checking current Actions.
