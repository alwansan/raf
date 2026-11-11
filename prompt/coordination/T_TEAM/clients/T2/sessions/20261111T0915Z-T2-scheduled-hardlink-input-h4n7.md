# T2 session 20261111T0915Z-T2-scheduled-hardlink-input-h4n7
origin=scheduled
resumed_from_session=20261111T0724Z-T2-scheduled-parent-symlink-q8r3
base_sha=76369b761c688c5c2e88839d40481c178fecd534
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 phone world/save/reopen confirmed, water/FFT errors remain.
scope=Foam aggregate publisher source/output hardlink alias guard only; T3 effects, T4 mouse, T5 resolution left untouched.
hypothesis=source and destination distinct pathnames can alias the same inode, and os.replace may overwrite the source path's linked content; explicit samefile fail-closed guard.
changes=scripts/t2_foam_publish_aggregate.py; tests/test_t2_foam_publish_aggregate.py
verification=Source regression added; CI outcome pending; no local Python execution in this run, no Unity/device or original ShaderLab proof.
next=Inspect Foam CLI gate CI for this SHA; prioritize original Foam RenderTexture and CB0 lineage, stage and shader binding with T1/T3. Publisher is opt-in and legacy integration remains UNKNOWN.
