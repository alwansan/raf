# LogRaft Binder sink delivery accounting — 2026-11-04

Scope: `lograf` only. Source change `b874096b769e050889020d85560e0d34bfa4f83d`; regression checks follow.

The Shizuku remote pump previously cleared its batch before invoking `ILogSink.onBatch`. If the Binder call failed, it stopped recording without exposing how much data had unverified delivery. The remote service now records `remote_sink_failed_batches` and `remote_sink_failed_bytes` (UTF-8 bytes) in metrics and its status, attempts an explicit failure notification, and stops rather than retrying an ambiguous Binder transaction. These are **possibly lost / unverified delivery**, not proven lost bytes: the receiver may have accepted the batch before the exception. The counters are in the remote process, so they are not guaranteed to survive process death or be persisted if the sink is disconnected. No raw content is uploaded or copied into the diagnostic.

A bounded batch is cleared in `finally` after the delivery attempt, preserving memory bounds. This is not a durability guarantee: the SAF writer's asynchronous enqueue is a separate acknowledgement boundary. A future end-to-end device test must deliberately kill/disconnect the receiving process during a high-rate Logcat stream, inspect `status()` while the remote is alive, verify whether the failure callback/metrics reached the UI, and compare raw segment boundaries. Avoid automatically replaying unacknowledged batches because duplicate data would compromise timestamp and rate interpretation.

The existing structural Python suite now guards the new accounting and stop-on-failure behavior. CI success would establish source/build invariants only, not Poco F5 Pro Android 15 reliability. No Raft game branch was modified.
