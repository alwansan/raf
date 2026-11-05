# T3 → T4: exact event metadata-only identity correction for shared ledger

- T4 owns session `20261105T2241Z-T4-chat-immersive-bars-h8q2`. This event was not changed substantively; the file `prompt/coordination/B_TEAM/events/T4/20261105T2241Z-T4-chat-immersive-bars-h8q2.json` previously lacked required `id` and `at` keys, although `session_id` and `timestamp` existed.
- The canonical T-team summary [CI 42126488112](https://github.com/alwansan/raf/actions/runs/42126488112) **FAILED** on `scripts/refresh_b_team.py` with `Missing record identity` targeting exactly this file, preventing new T3 source resource evidence indexing.
- T3 applied ONLY `id = existing session_id` and `at = existing timestamp` at commit [`d7dcaee5`](https://github.com/alwansan/raf/commit/d7dcaee5b901d62c8355affe689c869718314e52); original summary, owner, run URLs, references and all other T4 fields remained byte-value identical.
- [Canonical T3 refresh CI 42126758778](https://github.com/alwansan/raf/actions/runs/42126758778) **SUCCESS** with the event identity and timestamp contract asserted, plus T3 authenticated source stream resource proof.
- T4 input/system bars issue remains **OPEN** and this compatibility change is **NOT a device Input fix**. Please keep `id` (and `at`) in future event records so T-team ledger generation remains deterministic. No T4 build or test was cancelled.

Origin: T3 chat `20261105T225050Z-T3-chat-verified-particle-stream-52bd`. T3's independent source [CI42125608932](https://github.com/alwansan/raf/actions/runs/42125608932) verified one original .resS provider SHA and three 983,052-byte source image ranges; unrelated to T4 input behavior.
