# T2 — original Foam collision-only DescriptorSet remap, preserve CB0

- session_id: `20261106T024715Z-T2-chat-selective-descriptor-cbguard-a91c`; origin: chat; status: active
- base_sha: `1530d4efb3fe3f9d76d13423c81a9c09f8e3c341`
- resumed_from: `20261106T022741Z-T2-chat-foam-private-set-remap-f6a2` (original CI42151620701 success), `20261106T021504Z-T2-chat-foam-descriptor-collision-c7e8`
- work: `prompt/coordination/work/WATER-001/T2-20261106T024715Z-T2-chat-selective-descriptor-cbguard-a91c.json`; experiment: `zip2_original_Foam_two_pass_Vulkan_minimal_conflicting_descriptor_only_OpDecorate_DescriptorSet_relocation_with_CB0_guard_v1`
- original SHA source `ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, owner `sharedassets0.assets` 115978112 bytes SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original Foam raw object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`.
- Baseline: full private fragment-only remap CI42151620701 SUCCESS 67 synthetic tests, original 4 type collisions removed by moving 14 fragment descriptor decorations (pass0 11, pass1 3), but it *also moved* shared CB0 fragment descriptors off the VS binding. All private source/binary erased and no Unity/device tested.
- New hypothesis: relocate only four **conflicting-type** Fragment descriptors, preserve genuine original same-type shared CB0 coordinates and all non-decorated SPIR-V words; explicitly distinguish remaining source CB0 block-size differences from descriptor class collisions.
- Owned files: `scripts/t2_foam_private_selective_descriptor_set_remap.py`, `tests/test_t2_foam_private_selective_descriptor_set_remap.py`, isolated T2 private original workflow and own experiment/work/report. No original game shaders/meta/GUID, others' work, sound/Settings/touch, or full Unity/Android build.
- Source-free adversarial plus SHA-original CI verification required. Strict privacy: only bounded aggregate counters, no original symbols/bytes or private descriptor numeric coordinates. WATER-001 remains OPEN, project NOT_READY.
