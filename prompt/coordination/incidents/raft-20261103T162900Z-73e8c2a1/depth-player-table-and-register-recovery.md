# W1 bounded recovery failures — resolved in scope

Author W1 raft-20261103T162900Z-73e8c2a1; sessionw1-20261103T133907199Z-7c92e41a; 2026-11-03T13:53:30.498Z.

Initial original recovery41646527015 and41646749500 failed because legacy stage arrays were empty; original player-table bucket3 preserved real programs. Repaired8d40b995;41647000251 SUCCESS18stages/9pairs.

Name rebinding41647688723 exposed9 fragment compilation failures: naive identifier replacement altered register(s0/s1) compiler annotations. Fixed433074c02 plus regression controls;41647954010 SUCCESS18/18 rebound stages.

No original game data, material, texture, .meta or GUID was mutated. Private regenerated programs only. Parameter blob0 semantics, original renderstate ShaderLab wrapper and GPU numeric/render/device proof remain OPEN. No test flag or gate weakened. See docs/W1_DEPTH_COPY_PASS_RECOVERY_2026-11-03.md.
