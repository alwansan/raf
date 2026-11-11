## 11 Nov 2026 — GFX138 original Windows Forward versus Deferred mask gate

Session `20261111-GFX-chat-original-pass-mask-96`, `origin=chat`, writing only to `experiment/android-graphics-rootcause`. Base `239808dbc7390c323f6aa0aac9884b258d0f1ea7`.

GFX136's actual original Windows D3D11 WARP Deferred result recorded 2,008 coverage pixels, and its RT0 mask SHA256 `539a7b7685e303394c783b9a9b88deeda9bc775cd3df041263f51e6a4f1b7f91` exactly equals the prior source-pinned original GFX121 Forward mask SHA256. A matching count alone could hide displaced pixels, so GFX138 adds an independent source-free fail-closed exact per-pixel alpha comparison across four original Windows Forward controls and three Deferred RT0 controls, checks prior safe Forward SHA and Mesa coverage count, rejects bad-length/nonbinary images and shifted coverage with unchanged pixel count. The pinned GFX136 Windows workflow now reruns original DXBC Forward and Deferred using the same stage/source texture preparation in one private job, runs GFX138 unit tests and uploads only aggregate safe JSON. Original assets/readbacks are purged with the existing `if: always()` cleanup. **CI new workflow result is pending**; no phone test or signed owner APK produced. Actual Unity shader/pass selection and native G-buffer formats, original game scene parity, inter-driver RGB differences, original animation playback and final Android acceptance remain open. `phase_closed=false`.


---

