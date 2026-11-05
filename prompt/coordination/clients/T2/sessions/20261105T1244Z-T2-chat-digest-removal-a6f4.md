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

## Source fix submitted; source-authentic original-data validation pending

- commit [e8f3641551c54e7f5cd64bd74b01a9d0fcb3b871](https://github.com/alwansan/raf/commit/e8f3641551c54e7f5cd64bd74b01a9d0fcb3b871), built from live HEAD `52afde9353b09ab40012fc04e6d9ff73371c38ff` using expected-HEAD fast-forward lease, no force.
- source: removed unkeyed original numeric pair SHA256 producer and output key, retained complete/distinct counts and source/authenticity checks. Tests: order-invariant cardinality and single-pair privacy adversarial regression. Own CI: added assert against public hash/digest keys in per-stage safe JSON. No original private indices emitted by changed code.
- [SHA-pinned original CI42030329788](https://github.com/alwansan/raf/actions/runs/42030329788): **in_progress** at 12:49Z; [runner guard42030329635](https://github.com/alwansan/raf/actions/runs/42030329635): in_progress. They were triggered by **one** atomic three-file push. No original CI success/device claims until result verified.
- status: `waiting_ci`; resource occupied only by T2 Foam private source CI. No Unity/native job launched; T1 independent FFT RGBA32F control previously succeeded in CI42029739318.
- next_step: inspect result/first failed step/artifact schema; close scoped work if passed, then start distinct field-write/index-argument provenance experiment, preserving current owner code and water shader authenticity restrictions.
