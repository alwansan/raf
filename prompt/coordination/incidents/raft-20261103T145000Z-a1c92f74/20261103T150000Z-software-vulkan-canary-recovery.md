# A1 software Vulkan experiment recovery — resolved

The first [A1 synthetic CPU Vulkan workflow41658505014](https://github.com/alwansan/raf/actions/runs/41658505014) failed because glslang requires `GL_EXT_samplerless_texture_functions` for samplerless `texelFetch`. It was a synthetic test-setup error, not a Raft original shader failure. The GLSL fixture was corrected; [41658674936](https://github.com/alwansan/raf/actions/runs/41658674936) then passed the positive and intentional arithmetic negative-control GPU-independent tests.

Subsequent code expansion to three deterministic inputs/dispatch cases caused two intermediate non-final failures: [41659830783](https://github.com/alwansan/raf/actions/runs/41659830783) from C++ `inputSeed` declaration order; [41659953039](https://github.com/alwansan/raf/actions/runs/41659953039) from the schema tests temporarily preceding their updated required fields. The later source and test commits corrected these; final exact-source [41660159285](https://github.com/alwansan/raf/actions/runs/41660159285) PASSED both jobs with 8/8 tests, actual authenticated 20 programs × three workloads =60/60 written-pixel output agreement. Earlier failures are not hidden, nor treated as final game build errors.

GitHub reference writes on the shared feature branch sometimes returned transient UNKNOWN/409 during other agents' concurrent commits; A1 created only uniquely named files or used `update_file` with the live content blob SHA, no force, no overwrites, no cancellations, no protected-branch changes. No original GPU binary artifacts or pixel arrays were uploaded.

Status: **resolved for this scoped A1 experiment**. Remaining actual game blockers WATER-001/RENDER-002/FFT-FORMAT-009 stay OPEN; software CPU Vulkan cannot prove Android GPU operation.
