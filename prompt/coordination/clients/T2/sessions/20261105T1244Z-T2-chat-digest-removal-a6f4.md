# T2 chat — source-authentic Foam low-domain numeric digest privacy

- session_id: `20261105T1244Z-T2-chat-digest-removal-a6f4`
- origin: `chat`; owner T2, issue WATER-001
- base_sha: `9fae6ebe5fdadace352daa79ca73c04739b030c2`
- resumed_from_sessions: `20261105T1218Z-T2-digest-safety-isolated`, `20261105T1213Z-T2-foam-return-producer-call-isolated`
- status: active (work plan registered first at commit `ce837afedc3959786e518c993aafeaf8dca44db8`)
- work: `prompt/coordination/work/WATER-001/T2-20261105T1244Z-T2-chat-digest-removal-a6f4-privacy-report.json`
- intended files: `scripts/t2_foam_texture_identity.py`, `tests/test_t2_foam_texture_identity.py`, `.github/workflows/raft-t2-foam-member-abi.yml`, this session, work record.
- experiment_key: `t2-foam-original-lowdomain-pair-sha256-removal-zip2-15964ea8-v1`; resource_key: `t2-foam-member-abi-original-ci`
- evidence inherited: [T2 original RenderTexture[] array lookup CI42028369439](https://github.com/alwansan/raf/actions/runs/42028369439) success; separate isolated T2 synthetic low-domain digest enumeration proof at 12:18Z. No queued or running runs at first inspection. T1 reserved separate FFT RGBA32F test; other clients' code/workflows remain untouched.
- exact hypothesis: original index/sampler-index pairs lie in bounded domain; unkeyed SHA256 of such pairs in safe JSON can be brute-forced. The producer still emits `original_numeric_pair_digest_sha256` even after earlier warnings. Remove at producer, preserve non-sensitive counts and ensure original SHA-pinned private CI output asserts no digest.
- tests and CI: pending code change and workflow results.
- limits: no original shader source or raw asset export; no Unity/Adreno pixels or phone acceptance, no changes to game assets, audio, Settings, touch. WATER-001 OPEN, NOT_READY 0/3.
- next_step: commit isolated source/test/workflow changes after live HEAD check; inspect T2 Actions results, finalize this session and work record.
