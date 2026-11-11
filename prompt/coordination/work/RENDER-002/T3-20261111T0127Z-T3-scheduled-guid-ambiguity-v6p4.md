# T3 RENDER-002 — 20261111T0127Z-T3-scheduled-guid-ambiguity-v6p4

origin=scheduled; baseline_head=519dad679e30098ceefc2cadf0a34d1a9be1ca0d; experiment=T3-GUID-AMBIGUITY-001.

Owner device feedback: Artifact 42058825739 entered/saved/reentered world, while square smoke, white raft/hand and lighting remain OPEN. CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Latest T3 smoke chain 20261111T0033Z is evidence planning only. Preserve original .meta/GUID/.rgd and no game resource edits.

Hypothesis: duplicate .meta GUID identities are currently counted as resolved_in_supplied_tree, although two distinct local owners make the reference ambiguous. Verify with synthetic duplicate and unique GUID controls. Report ambiguous separately and hashed only; do not label ambiguous references as confirmed game faults. Paths: scripts/t3_unity_guid_link_audit.py and new tests/test_t3_guid_ambiguity.py only, plus own work/session files. No shared Unity, CI, game assets or native build resources reserved. Avoid overlap with T1/T2 water, T4 mouse and T5 display/build. No CI dispatch without checking running jobs.
