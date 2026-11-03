# A11 incident — shader scope integrity could report an ungrounded snapshot

- Author: A11 / raft-20261103T123040Z-02fe66b3; observed at 2026-11-03T13:26:55Z; issue RENDER-002; status: **source-tool defect fixed, production-export verification pending**.
- Evidence: [test-only RED source11336a6c](https://github.com/alwansan/raf/commit/11336a6c94b9f97d56dabe8e0f716dabb7772c71), [RED CI41644180493](https://github.com/alwansan/raf/actions/runs/41644180493) six of17 failed as expected; [source9e85d22](https://github.com/alwansan/raf/commit/9e85d22cc195d239048be1ef145ec3626e76fc26), [GREEN CI41644281473](https://github.com/alwansan/raf/actions/runs/41644281473) all17 pass.
- Trigger: synthetic ancestor symlink, bad/duplicate 32-hex Unity GUIDs, orphan shader `.meta`, ignored expected count on snapshot creation or incomplete expected count pair.
- Cause: missing lexical project ancestor check, metadata GUID validation/uniqueness and count validation at both CLI modes in A11-owned read-only integrity checker; no original game data proved affected.
- Impact: false local-scope assurance was possible for a supplied directory even though the tool always correctly marked original full-export provenance unverified; this did not change game shaders or weaken the vendor-restoration gate.
- Recovery: source-only input rejection in A11 checker; no native/build action; test fixture red/green and SHA-pinned CI evidence. No LFS, source leakage, Unity, APK or running workflow cancellation.
- Next: original complete-export provenance remains UNKNOWN, so RENDER-002 is still OPEN and overall NOT_READY/0-of-3.
