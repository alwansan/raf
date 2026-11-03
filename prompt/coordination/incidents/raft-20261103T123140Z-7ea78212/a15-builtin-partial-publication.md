# A15 RENDER-002 interrupted include/license publication

- **Author:** A15 (raft-20261103T123140Z-7ea78212); **UTC:** 2026-11-03T13:29:17.236Z
- **Issue:** RENDER-002 (restoration failure recovery subissue)
- **Evidence:** [RED 41643857822](https://github.com/alwansan/raf/actions/runs/41643857822) intentional 4/4 failure before patch; includes stranded partial include and rewritten identical file.
- **Cause confirmed by source:** additions were written with truncating `write_bytes` but exception cleanup restored shader bodies only.
- **Fix:** [b7188de1](https://github.com/alwansan/raf/commit/b7188de1daffb34eaba11efcf24d4295f912453a) creates absent additions exclusively, skips identical destinations and deletes its newly created partial files on exception.
- **Verification:** [GREEN 41644109948](https://github.com/alwansan/raf/actions/runs/41644109948) 22/22; same-source A3, A9 and official vendor workflows PASS.
- **Status:** mitigated for CPU simulated failures; not proven power-loss atomic or on phone. Broader RENDER-002 and 41624581951 strict zero-match remain OPEN, NOT_READY 0/3.
