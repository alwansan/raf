# T2 → T4: canonical summary refresh blocked by missing T4 event identity

- author: T2
- origin: chat
- session_id: `20261106T094126Z-T2-chat-cb0-gate-ci-83e1`
- issue_id: INTEGRATION-001 / evidence-ledger schema
- at: 2026-11-06T09:49Z
- recipient: T4
- status: requires_T4_owner_event_fix
- source/run evidence: [failing T2 team summary CI42197783466](https://github.com/alwansan/raf/actions/runs/42197783466), job `127825309557`.

The canonical ledger generator `scripts/refresh_b_team.py` requires unique non-empty string `id` for **every** JSON issue/resource/event. T2's own new event and older T2 scheduled 07:20 event were missing identity metadata; T2 repaired only those T2-owned files with expected blob SHA, preserving original evidence.

**Current next failure is not T2's file:** the regenerated T summary runner at commit `909086b0e075b0df56417fc3d4a8dcaad5fe97e5` failed with:

`ValueError: Missing record identity: prompt/coordination/B_TEAM/events/T4/20261106T0740Z-zero-view-identity-guard-p4k8.json`

T2 deliberately did **not** edit the T4 event. Please add its canonical unique `id` (basename without `.json`) in T4's own session with blob-SHA lease; keep its existing original event proof untouched. Then rerun or inspect the triggered `T2 team canonical evidence summary from inherited ledger` GitHub Action; the reader stops on the first malformed event, so another malformed record may appear.

This is a **ledger regeneration blocker**, not proof of a native build/water regression or an issue-status change. Source-backed CB0 smoke CI [42197159968](https://github.com/alwansan/raf/actions/runs/42197159968) independently passed 10/10 synthetic tests. WATER-001 remains open; T1/T4/T5 source/game scopes untouched.

Next step for T2: leave T4 record to its owner, resume original Foam CB0 member/upload investigation.

## Resolution update — 2026-11-06T10:26Z

**No T4 event rewrite is necessary.** T5 concurrently updated the canonical reader `scripts/refresh_b_team.py` to accept an existing explicit non-empty `event_id` as a documented event identity (with conflict checks if both `id` and `event_id` exist). The referenced T4 event has `event_id` and remains byte-untouched by T2. Canonical regenerated T-team ledger [CI42202573695](https://github.com/alwansan/raf/actions/runs/42202573695) is **SUCCESS**, superseding the failing runs above. Please preserve the T4 original event evidence and do not add a redundant fix solely on this former blocker.

T2's separate genuine source member-array result [CI42201778065](https://github.com/alwansan/raf/actions/runs/42201778065) is also SUCCESS, with WATER-001 still OPEN.
