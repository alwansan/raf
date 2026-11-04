# B06 synthetic fixture red after fail-safe capability logger update

- Session: `20261104T224512Z-B06-wg7a3`; WATER-001.
- Run [41928250212](https://github.com/alwansan/raf/actions/runs/41928250212), source `f9e34ee647e8eb841fa3a960f01cef5eb2a6be87`, **FAILED** in `tests/b06_fft_caps_smoke/Program.cs`: `Missing failure diagnostic`.
- Root: old synthetic negative fixture demanded the *whole optional probe* fail on a single `maxComputeWorkGroupSize` API throw. New code intentionally isolates each failing API and still emits the four format/5 group queries as unavailable; old assertion contradicted corrected behavior. This was not a Unity compile, private FFT or device failure.
- Recovery: [test commit 2fa36d1](https://github.com/alwansan/raf/commit/2fa36d110cbaf1693cd61fbede26e7ce3e8f8d36) updates assertion to require `max_group_invocations=unavailable` and all five classifications unknown, plus expanded 512/1024 boundary and unrelated format resilience.
- Final [CI41928357485](https://github.com/alwansan/raf/actions/runs/41928357485) **SUCCESS** on exact corrected source; final incident scope closed. No real FFT error fixed or hidden, WATER-001 remains OPEN.
