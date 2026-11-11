# T1 original phone CL pre-world FFT ordering — 2026-11-11
Session: 20261111T1712Z-T1-scheduled-preworld-order-93ac; origin=scheduled; WATER-001 OPEN NOT_READY 0/3.

Pinned owner device evidence: [42058825739](../../docs/DEVICE_FEEDBACK_42058825739_AR.md), source e9c358eda01785b65e4eb14f18723da426635628, world entered/saved/reopened from artifact. Artifact publish failed; APK/OBB manifest fingerprint remains unconfirmed.

CL immutable ref: alwansan/CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57, `raft log/lf/{LogRaft-20261105-220911-559,LogRaft-20261105-230108-327}/session-summary.json`.

| CL session | first water pass | first FFT kernel | world loaded | FFT after water | water before world | FFT before world |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 220911-559 | 1793905782604 | 1793905782606 | 1793905840642 | +2 ms | 58038 ms | 58036 ms |
| 230108-327 | 1793908926108 | 1793908926110 | 1793909045761 | +2 ms | 119653 ms | 119651 ms |

Material and index partition checks from both *final* summaries:
- 220911: Spectrum 8484 + Foam Global 15400 = water 23884; kernel index6 3850 = FFT 3850.
- 230108: Spectrum 15028 + Foam Global 24104 = water 39132; kernel index6 6026 = FFT 6026.
- Subsurface Blur and Utility Noise reported 0 in both; no other kernel index root line.
- Source's `final_game_milestones.world_loaded_message_observed` appears once in each session.

**New bounded discriminator:** Both water pass and kernel-index failures were already observed **before** the world-loaded milestone, by ~58 s and ~120 s respectively. Therefore a failure mechanism requiring the world-loaded callback *as its first trigger* is inconsistent with these summaries. This does not prove that errors caused the world to load slowly, that the same frame emitted both roots, that the kernel index is the original compiled FFT program 6, or that the shader asset is missing. Logcat collection loss, asynchronous log timestamps, and session differences remain limits.

Reusable source-only validator: `scripts/t1_water_startup_order.py`, tests `tests/test_t1_water_startup_order.py`. The local equivalent implementation passed five isolated synthetic controls; actual CL timestamps and partitions were read from pinned GitHub summary JSON, not replayed on GPU. For a stronger test capture Unity asset GUID + named HasKernel/FindKernel + GetKernelThreadGroupSizes + original Dx11FFT direct Dispatch thrown/returned in one **new** device run; older artifact predates the hook. No CI or APK run launched here.

T4 physical mouse and T5 three right-side controls/Resolution remain separate scopes; shared touch layout deferred.
