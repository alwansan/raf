# A11 shader-export provenance (RENDER-002)

- Identity: A11, raft-20261103T123040Z-02fe66b3; 2026-11-03 UTC. Initial head inspected aae8cc2070126449fa05049a669235a144309101; HEAD changes constantly because clients work in parallel.
- Read full project/current owner/coordination instructions. Read related A9 ShaderLab identity, A3 path and A6 include safety findings and earlier 107-local-file sample work. These fixes do not settle actual full-export matches.
- Evidence: native CI 41624581951 failed before Unity in reconstruct job 125878883840 at restore built-in step (198 SHA-pinned official vendor identities). Pre-restore audit in same run: 140 shader files all source 1-pass; 0 .compute. Different local 107-file subset: 24 empty, 83 parseable nonvendor, 0 vendor; no proven full-run scope.
- Planned distinct work: strict read-only exported-shader inventory provenance diagnostics, independent tests and workflow; no original source/name disclosure, no weakening strict identity/water checks.
- RENDER-002 and WATER-001 OPEN; game NOT_READY, readiness reviews 0/3. No Unity/Android/native request/Release/LFS or scheduled-task changes.
- At registration, GitHub branch-level update_ref(expected_sha) returned provider errors; exclusive creation of per-client new paths is used, no other clients' files altered. For shared files use blob SHA CAS only if necessary.
