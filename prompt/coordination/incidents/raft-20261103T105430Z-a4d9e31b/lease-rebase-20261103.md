# A4 DIAG-010 — stale-ref lease during registration (resolved)

When creating independent A4 identity, initial expected-SHA update on parent e70dd94d9ea0309718f523352edb24299960c15d returned a GitHub GraphQL UNKNOWN, while other agents advanced HEAD. The draft commit was not published. A4 rebuilt ONLY its own isolated coordination paths on fresh HEAD 66d8e67da5b4ee610526452ccfb763b6c10e52fc and published ea806b7f75d471e705c048c884a3a02cb610caf9 via expected_sha/force=false. Cause of GitHub internal error is not independently diagnosed. No branch force or job cancellation. Incident RESOLVED.
