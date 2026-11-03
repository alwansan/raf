# A8 original ZIP2 source-pin traversal test — resolved

Author: `raft-20261103T224306Z-d17e2cb7`. Date: 2026-11-03 UTC, source-only experiment `LOCAL-005`.

**Failure:** [Run41733527931](https://github.com/alwansan/raf/actions/runs/41733527931) ended FAILURE on source `3e354068cfbd62a684d3f9211d15961f898d4851`. Of 11 synthetic verifier tests, one negative `../escape` pin supplied a traversal component that passed the initial regular expression. Since the same fixture also had an oversized manifest, the tool raised a manifest error instead of rejecting the malicious pin first. This could weaken an API caller supplying independent relative pin paths; the actual CLI uses two hardcoded safe paths. The failure did not fetch corrupt original content or run Unity.

**Fix:** [5f5be032](https://github.com/alwansan/raf/commit/5f5be03230b3becc1f9fa88bc86fa9a395919483) rejects `.` and `..` components before manifest access. [Run41733872815](https://github.com/alwansan/raf/actions/runs/41733872815), same fix source, **COMPLETED SUCCESS**: 11/11 synthetic source checks and authenticated ZIP2 original SaveAndLoad path compatibility test green. No other client's code or source/protected branches touched.

**Status:** RESOLVED for path validation; original Android world/.rgd runtime acceptance remains untested and LOCAL-005 generally OPEN. Do not mark game READY from this result.
