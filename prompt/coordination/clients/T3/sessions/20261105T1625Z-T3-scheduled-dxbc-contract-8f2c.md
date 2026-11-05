# T3 scheduled — independent DXBC signature component contract

- session_id: 20261105T1625Z-T3-scheduled-dxbc-contract-8f2c
- origin: scheduled; identity: T3; issue: RENDER-002 OPEN; readiness: NOT_READY 0/3.
- resumed_from_sessions: 20261105T1607Z-T3-chat-spv-name-location-7c2d, 20261105T1526Z-T3-scheduled-iosem-6c42.
- base_sha: ae8fbd240a1cc64f9711489fe3172c27b46fd9a8.
- work registration commit: fe5bf013d69cf5d8d66f9394d7c0a5bd6406ae83.
- experiment_key: T3-DXBC-signature-register-mask-schema-sourcefree-v1.
- source script commit: 34b94e2d595877cc00eaafc21c5a35b15b571e01; test commit: 150f506e5653586e3e6977f8b5fcd038d07421a4.
- Evidence inherited: genuine original [CI42062573338](https://github.com/alwansan/raf/actions/runs/42062573338) SUCCESS; 8/8 original DXBC stages roundtrip; 0/34 input and 0/29 output generated names preserved; therefore name equality is not a valid semantic mapping. The new tool DOES NOT parse original DXBC nor establish semantic correspondence.
- New isolated helper validates bounded pre-extracted signature records: kind, integer register, four-bit component mask and system-value flag; rejects overlapping component claims within a stage side, invalid fields and accidental disclosure of private names. Emits aggregate counts only. This is a prerequisite for a future original DXBC ISGN/OSGN extraction and avoids falsely equating numeric Location with semantic identity.
- Local command: `cd /mnt/data/t3 && python -m unittest -q` => 6/6 PASS after correcting an initial local typo; source published includes correction. GitHub CI not yet verified. No native/Unity/phone run dispatched.
- Rejected hypotheses: reflected SPIRV-Cross generated names cannot prove source semantics; equal type multisets cannot prove interpolation or DXBC register/component mapping. No claim of shader restoration or pixels.
- Next: inspect authentic DXBC signature chunk layout and implement fail-closed ISGN/OSGN/ISG1/OSG1 extraction with pinned original input; join private register/component/system-value counts to SPIR-V builtin and location decorations, without publishing original names.
- Preserved original assets, .meta/GUID, .rgd, sound, Settings, deferred touch. No Actions cancelled or repeated.
