# B46 recovery memory

Session 20261104T2058Z-B46-6e3d, started 2026-11-04T20:58:00Z; no existing B46 state at first read. Initial HEAD 0484260051916587e102359d6a3ccb820358c7e5.

Scope RENDER-002 material -> texture exported GUID link integrity. Preserve owner-confirmed working audio and Settings; touch/layout deferred. Related owners: W2 original binding census 1556 materials/4583 bound slots, W3 source Material graph, W1 1536 exported Material documents, A13 exported Shader GUID guard. Source ref zip2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385. B50 is actively handling LOCAL-005; do not overlap.

Read B_TEAM PROMPT_AR, README, OPERATING_MODEL_AR, SOURCES_AND_ACTIONS_AR, SUMMARY, REVIEW_2026-11-04, TEMPLATES, RESTORE_AR; AGENTS; CURRENT_OWNER_REQUIREMENTS; ZIP2_SOURCE_PROVIDER; prompt README/CONTINUE/STATUS and W2/W3/A13/W4 evidence. Live Actions at initial read: B50 41911081809 running, other preflights successful. Latest game is APK86 source d181ee7152580f49ee0b41dfd05fa2bfdacfafe5, https://github.com/alwansan/raf/actions/runs/41812889049, NOT_READY 0/3. CL 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29 contains white surfaces, 40327 water pass errors and 5555 kernel errors.

Hypothesis: exported material shader PPtrs may be intact while m_SavedProperties.m_TexEnvs texture refs are malformed or dangling. Implement read-only fail-closed bound parser and asset GUID resolution, local synthetic positive/negative controls, optional isolated CI. This cannot claim source-to-export full equivalence, shader recovery, GPU/image or device success. Do not upload original asset payloads or guess missing GUIDs; retain all .meta files.

Next checkpoint: script/test results and safe integration step, update experiment/work/state/summary/STATUS. Do not start full Unity build or edit shared native workflow while others run.
