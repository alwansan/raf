# T2 — full-schema Foam original-IL negative partitions

- session_id: 20261108T0222Z-T2-scheduled-fullschema-negative-q8m4
- origin: scheduled
- issue: WATER-001 OPEN; NOT_READY; status: source_test_added_unexecuted
- baseline HEAD: 442759a8a66781c56df399107e396bedb04c4517
- work: prompt/coordination/work/WATER-001/20261108T0222Z-T2-scheduled-fullschema-negative-q8m4.json
- owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md, native 42058825739; world enter/save/re-enter OWNER_CONFIRMED only for tested artifact; water/FFT remain broken, publish failed.
- inherited: T2 20261108T0120Z synthetic full-schema unmocked test; original pass0 RenderTexture to RenderTexture and pass1 unknown/unknown from 42308583977. Avoid repeated source census.
- scope commit: d6bd2fa745dfa9ac030ec0bf72fbca788b135f4d; code commit: 235dd727d0a4bddc02094012c1fc2201d926140b.
- changed only tests/test_t2_foam_pass_crosscheck_original_integration.py: three fail-closed tests exercising real validate_original for exact original material-field API read-site count, per-pass0 source-role partition, and overall destination-role partition. The tests use only synthetic safe aggregates; no private IL, names or shaders.
- verified from GitHub source: validator enforces source_exact_original_material_field_API_sites_partial, Blit_pass_specific_role_partition_incomplete, and Blit_direct_source_destination_partition_inconsistent respectively; no mocks. Tests are written but NOT EXECUTED; local git clone fails DNS, and no equivalent CI dispatched. No claim of test success.
- at initial live read branch HEAD 442759a8a66781c56df399107e396bedb04c4517; sampled Actions in_progress 0. No native build, Unity, ShaderLab, .meta, GUID, Settings, sound, T3 files, or touch changes.
- trial vote T2 remains «لا يحتاج»: no substantive integrated phone-ready water shader; no duplicate APK request.
- next: execute python -m unittest discover -s tests -p 'test_t2_foam_pass_crosscheck_original_integration.py' -v from original checkout or cheap CI; correct synthetic fixture only if validator legitimately rejects it, never weaken authenticity. Then privately trace Foam pass1 producer and actual CB0/material bindings before ShaderLab.
