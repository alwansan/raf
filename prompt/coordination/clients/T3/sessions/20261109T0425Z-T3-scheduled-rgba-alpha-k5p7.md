# T3 scheduled — RGBA screenshot visibility evidence

- session_id: 20261109T0425Z-T3-scheduled-rgba-alpha-k5p7
- origin: scheduled
- issue: RENDER-002 OPEN / NOT_READY
- resumed_from_session(s): 20261109T0330Z-T3-scheduled-png-fixture-h4m8; 20261109T0150Z-T3-chat-particle-emitter-3p7k
- base_sha: 6b2c4991865fda2077c45350bc130b10311eca33
- scope_commit: e5ff0d7106d55eba534cc23262f36ec884dc00b8
- patch_commits: fd57cbe596d6f5607d0bc4a7db2d6ecbc9d7890f; 04fc7e2c062be685f531dbda5dbc634b8ae6264a
- observed_head_after_patch: 04fc7e2c062be685f531dbda5dbc634b8ae6264a
- experiment_key: t3-png-rgba-transparent-pixel-visibility-sourcefree-v1

## Evidence and action
Read 5-Nov phone report before choosing scope, T_TEAM instructions, previous scheduled and chat T3 checkpoints, owner shared mini lab policy. Actual owner artifact 42058825739 world entry/save/re-entry is a limited phone PASS; white hand/raft and square smoke remain unresolved. Original six-scene shader linkage from T3 chat run 42549246777 identifies distinct 34-use smoke-like candidate; do not confuse it with 108-use shader dummy proof.

Found independent diagnostic ambiguity in PNG audit: it counts RGB of fully transparent pixels as visual color diversity. Added explicit alpha_zero_fraction, alpha_partial_fraction, opaque_unique_rgb without changing legacy raw-RGB region metrics; synthetic RGBA tests distinguish transparent red from opaque blue and partially transparent red. This is a read-only diagnostic improvement, not a game shader fix. Existing PNG RGB behavior preserved. The tests were committed but **not executed in this run**; no PASS claimed. No CL binary image analyzed and no Unity/mini/full game CI dispatched. CL is read-only; no gameplay files, .meta/GUID, .rgd, sound, Settings, or input changed.

## Next
Run python -m unittest discover -s tests -p 'test_t3_cl_png_pixel_audit.py' on the actual checkout/cheap CI; audit pinned CL six PNGs and explicitly inspect alpha fractions. Prioritize original distinct smoke-linked Shader48 parsed Pass/Blend/alpha and same-export ShaderLab before any guessed runtime patch. Recheck branch HEAD and overlapping chat scopes. RENDER-002 remains OPEN / NOT_READY.
