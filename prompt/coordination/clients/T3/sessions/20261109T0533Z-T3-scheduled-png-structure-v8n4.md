# T3 scheduled — PNG structural evidence guard

- session_id: 20261109T0533Z-T3-scheduled-png-structure-v8n4
- origin: scheduled
- issue: RENDER-002 OPEN / NOT_READY
- resumed_from: 20261109T0425Z-T3-scheduled-rgba-alpha-k5p7; 20261109T0150Z-T3-chat-particle-emitter-3p7k
- baseline_head: 6ae2ee2b241c4d6d3b45e066d01684066cafb392
- work_scope_commit: 158f9baedcc449e01c6c2a83b6d65bb8d36e4403
- source_commit: f4c0931ded2bb5eb0d24bc855ff6d1dd9c911a14
- regression_commit: 5178fe80f8e35b8d5369a226f6fec7f185efc124
- experiment_key: t3-png-critical-order-sourcefree-v1

## Evidence and result

Read 5-Nov owner phone report: artifact 42058825739 proved limited world entry/save/re-entry, not color or smoke repair. Read T_TEAM protocol, owner requirements, STATUS and previous T3 chat/scheduled results. Latest head at start 6ae2ee2b; recent T2 CI 42561294739 success; no new Unity/native CI requested. CL owner images and lab captures remain read-only and not reinterpreted as device proof.

Independent issue in T3 PNG pixel-audit: CRC-valid malformed PNG critical chunk ordering could be accepted. The parser now fails closed on IHDR not first, duplicate IHDR, noncontiguous IDAT, nonempty IEND and missing IDAT. Added five synthetic negative fixture cases to existing source-free unittest suite. No original game files, .meta, GUID, .rgd, sound, Settings or input changed. No heavy CI launched. **Tests committed but not executed in this run** because local container DNS could not resolve raw.githubusercontent.com and GitHub connector does not execute Python; no PASS claimed.

## Next

Run `python -m unittest discover -s tests -p 'test_t3_cl_png_pixel_audit.py'` on real checkout or existing cheap CI; inspect failure, if any. Then audit six pinned CL binary PNGs and original smoke-linked Shader48 (34 uses, not dummy evidence of separate 108-use shader) with Pass/Blend/Alpha and real material binding. Preserve RENDER-002 OPEN / NOT_READY. Coordinate with T3 chat before touching original smoke files. No duplicate APK or Unity build.
