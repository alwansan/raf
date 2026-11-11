# T4 INPUT-005 source route audit
session_id: 20261111T0238Z-T4-scheduled-capture-path-k9q4
origin: scheduled
baseline_sha: c1f67682ba0c70d243632e21ecb9b0446357e751
experiment_key: T4-CAPTURE-ROUTE-AUDIT-20261111
scope: independent mouse source audit, no shared Unity or T5 Resolution files
shared_resource: none

Owner's artifact 42058825739 (source e9c358eda01785b65e4eb14f18723da426635628) succeeded in entering, saving and reopening world; package publication failed. Preserve as device-specific evidence, not current HEAD evidence.

Read AndroidPhysicalMouseCapture.cs and PhysicalMouseMotionSource.cs. Current source already includes View.OnCapturedPointerListener, captured button/wheel buffer, frame-latched Legacy Input fallback, and reader evidence. Non-MOVE callback explicitly returns false for original View handling. This does not prove Raft callsites use wrappers or that physical buttons reach Unity. Main hypothesis: inspect callsite rewrite coverage before further changes. Avoid redundant fallback or parser-only work.

No CI triggered, no game files altered. T5 owns Resolution/right-hand buttons. Next inspect rewrite manifest and patch only demonstrably uncovered original mouse reader; validate keyboard and cursor transitions separately. Do not claim phone validation.