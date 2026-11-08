# T5 independent CI failure discrimination — 20261108T1550Z-T5-scheduled-mini-lab-javac-6a31
origin: scheduled
base_sha: b74603b011357c7c2880f3b88ef74546664fa076
experiment_key: javac-final-local-T1ComputeProbe-run42496449259-dd9a5de
input: GitHub Actions 42496449259, source dd9a5de9225d4330e0c7513564879615dd9d481d, job 128779717319, Gradle 8.10.2, Java 17.
observed: :app:compileDebugJavaWithJavac failed T1ComputeProbe.java:93 "variable observation might already have been assigned". On immutable failing SHA, the try and catch each assign `final String observation`; javac definite-assignment cannot prove exclusivity because a Throwable can arise after assignment inside try.
resolution_already_present: commit ae450f1f84ef4956f577df29cb21214517a8f065 (T1-owned) changes to mutable `String observed` in try/catch, followed by one `final String observation=observed` before nested UI lambda. This is correct Java capture pattern.
new evidence: workflow 42496622364 on 1beab49d26aa31a6cc4765f0c6020c2d552cce7b is in_progress at 2026-11-08T15:50Z. Do not launch duplicate or claim build success. Check whether this SHA contains ae450f1; its source ancestry should be checked before attribution.
scope: read-only failure triage; T1 source untouched; T4 build request untouched. No phone, APK, OBB or Unity acceptance.
next: inspect 42496622364 result and source SHA; if compile passes, verify actual APK artifact and SHA/version before updating T5 test center row; if failure, triage next compiler error without overlapping T1/T4 files.
