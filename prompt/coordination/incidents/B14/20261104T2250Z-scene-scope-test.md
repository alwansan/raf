# B14 RENDER-002 — incorrect test subrange in first CI correction

At 2026-11-04T22:51:57.271Z the first B14 attempt 5ef3f839 corrected static SceneLoaded syntax but unintentionally set its snapshot substring to start at the beginning of SceneLoaded. This included the intended GraphicsMemoryAtBoundary sample and the assertion falsely failed.
Impact: run 41928540784 red in Android diagnostic policy only. No production source, device or assets were altered by B14.
Recovery: commit 9ba6990c scopes the snapshot to ReportSceneShaderSnapshot method start, preserves boundary callback samples and low-memory tracing; full platform CI41928677980 SUCCESS. Closed as test-harness error (not a game/Adreno render failure).
