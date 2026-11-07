# T1 — Water faults precede world-loaded milestone (pinned CL)

Date: 2026-11-07 UTC. origin=scheduled. This is a **timing discriminator**, not a shader repair or proof of causation.

Sources: owner phone report `docs/DEVICE_FEEDBACK_42058825739_AR.md` (Artifact run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628), read-only `alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57` at `raft log/lf/LogRaft-20261105-{220911-559,230108-327}/session-summary.json`. Fields: `final_error_category_breakdown.*.first_observed_unix_ms` and `stop_time_android_process_exit_info.final_game_milestones.world_loaded_message_observed.first_observed_unix_ms`.

| Session | First invalid water pass (Unix ms) | First invalid kernel (Unix ms) | World-loaded message (Unix ms) | Pass precedes world-loaded | Kernel precedes world-loaded |
|---|---:|---:|---:|---:|---:|
| 220911-559 | 1793905782604 | 1793905782606 | 1793905840642 | 58,038 ms | 58,036 ms |
| 230108-327 | 1793908926108 | 1793908926110 | 1793909045761 | 119,653 ms | 119,651 ms |

In both sessions, classified water-pass and index-6 kernel errors begin **before** the logged world-loaded milestone, not only after it. This favors examining initialization/scene/menu-time water setup and repeated rendering paths rather than exclusively world-spawn callbacks. It does **not** prove the first errors were emitted from a particular scene, that the two errors have a common cause, or that index 6 is a particular named FFT kernel. Logcat observation and milestone logging may be incomplete; the installed APK/OBB SHA remains unverified. The owner independently confirmed world entry/save/reopen on the Artifact; Release publishing failed.

Next discriminating test: obtain first raw game-UID root lines and nearest scene/renderer markers from the pinned private CL segments; record C# callsite, ComputeShader asset GUID, FindKernel(name)/return, HasKernel, thread group dimensions, SetTexture/SetBuffer and Dispatch index at the earliest error. Compare authentic Vulkan/Unity FFT traces only after input/fixture hashes match. Never publish raw game shader or private log contents.

WATER-001 OPEN; NOT_READY 0/3. T4 physical mouse and T5 buttons/Resolution untouched. No native build requested.
