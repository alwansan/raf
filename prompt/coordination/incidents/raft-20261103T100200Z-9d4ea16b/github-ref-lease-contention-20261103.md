# A10 — transient GitHub ref and shared-doc contention (resolved)

- Date: 2026-11-03, during resumed A10 LOCAL-005 SHA-pinned source work
- Scope: `feature/android-native-port` only
- Symptoms: GitHub expected-head ref updates returned GraphQL `UNKNOWN` during concurrent branch commits. Later append-only `prompt/STATUS.md` SHA-locked updates initially returned HTTP 409 because other agents updated the same file.
- Recovery: Refresh live branch HEAD and target blob, rebuild a fast-forward commit on the new parent, preserve all concurrent tree entries and use `force=false` with `expected_sha`; for the shared status file, re-read full content, verify the A10 marker absent, append without erasing other sections. No branch reset, force, lost work, cancellation or native request occurred.
- Successful result: A10 source commit [29128ab](https://github.com/alwansan/raf/commit/29128ab789d5cf8a26a7e01d3ae5a9a39f331848), test [fbc95905](https://github.com/alwansan/raf/commit/fbc95905d690c83d809183b2ad09c0e5bf1d010b), CI source [031236bb](https://github.com/alwansan/raf/commit/031236bb5f4d4aeefc5b6ddc4b4de5188082920a); [41624212828](https://github.com/alwansan/raf/actions/runs/41624212828) SUCCESS.
- Residual risk: concurrent branch updates may recur; repeat read/rebase/lease, never force another client's commits. Incident is resolved, not a gameplay blocker.
