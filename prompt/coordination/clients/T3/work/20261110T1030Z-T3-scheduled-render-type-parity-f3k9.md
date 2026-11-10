# T3 work — 20261110T1030Z-T3-scheduled-render-type-parity-f3k9
origin=scheduled; baseline=6999eafe742d8c519e790a4df64ac786fd882ef2
Issue: RENDER-002; experiment_key=T3-RENDER-STATE-STRICT-TYPE-20261110
Scope: scripts/t3_render_state_pair_diff.py and tests/test_t3_render_state_pair_diff.py only; no game assets, shader, mouse, Settings, or shared CI.
Hypothesis: Python bool/int equality (True == 1) incorrectly reports MATCH for distinct JSON render-state representations; this can hide mismatched source/export data. Use strict type comparison; add negative regression. This is a diagnostic integrity fix, NOT device evidence.
Shared resource: none. CI: use existing workflow; no new Unity builds.
Inherited: T3 20261110T0932Z render-state CI verified run 42782959918. Owner device report 42058825739 confirms world save/reentry but RENDER-002 remains OPEN.
Next: authenticated original/export state extraction and real material pairing, not more synthetic-only tests.
