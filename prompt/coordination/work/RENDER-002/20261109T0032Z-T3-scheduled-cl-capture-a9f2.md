# T3 independent scope — 20261109T0032Z-T3-scheduled-cl-capture-a9f2
origin=scheduled; baseline_sha=34a3c09f2749fbd8b62a5e64a48424059349666c

Hypothesis: CL shared-lab screenshots are synthetic GL evidence and cannot be treated as actual Raft Material/Shader/Texture repair. Verify source identity and capture contract before pixel conclusions.

Files: this work record and clients/T3/sessions/20261109T0032Z-T3-scheduled-cl-capture-a9f2.md only. Experiment key: T3-CL-20261108-232759-capture-provenance. Shared resource: none; no Unity, CI, release or other T worker files.

Observed: CL test/shared-20261108-232759-468049775 contains T3-01 through T3-06 PNG files and events JSONL. Event T3-01 records apk 0.2.13-shared, source e7a6248b0d0c14b9772bd52f3bbdc5cf22fa9b9a, pack SHA256 6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f; left RGBA 255,0,0,255 right 0,0,255,255; verified_surface_pixels=true; explicit human visual review still required. The observed viewport is 1060x1768. This is a synthetic GLES frame, not a Raft rendering capture.

Prior evidence: actual ZIP2 same-export selected 41 materials / 227 TexEnv slots and 150 color slots matched in runs 41939404454 and 41940350604. Those tests do not validate imported shader variants or device pixels. Owner Raft test artifact 42058825739 entered/saved/reentered world, but white hand/raft and square smoke remain.

Decision: no shader/material patch from these synthetic pixels; no new CI. Next: download and independently inspect PNG pixel regions; obtain a bounded real game material/shader/texture binding trace and map to the owner screenshot before modifying assets. RENDER-002 OPEN / NOT_READY.
