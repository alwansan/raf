# A3 transient GitHub ref-update errors — resolved

During source fix `ab556f12`, GitHub GraphQL returned two transient ref-update errors amid concurrent commits. The agent re-fetched branch HEAD, rechecked the current `scripts/restore_tmp_shaders.py` blob SHA before each fresh parented commit and used `expected_sha` with `force=false`. The source commit succeeded and [GREEN CI41737411435](https://github.com/alwansan/raf/actions/runs/41737411435) confirmed it. No lost peer work, forced branch change or cancelled job. Status: resolved.
