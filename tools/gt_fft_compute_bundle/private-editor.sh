#!/usr/bin/env bash
# All raw editor output for the exact original-resource method stays runner-local.
set -euo pipefail
real="$(cat /opt/gt-real-unity-editor)"
args=("$@")
target=0
building=0
run_id=
log_index=-1
log_count=0
for ((i=0;i<${#args[@]};i++)); do
    case "${args[i],,}" in
        -executemethod)
            if [[ "${args[i+1]:-}" == GTIndexedPair.Run ]]; then target=1; fi ;;
        -logfile)
            log_count=$((log_count+1))
            log_index=$((i+1));;
        -gtfftrunid) run_id="${args[i+1]:-}";;
        -gtfftbuildonly) building=1;;
    esac
done
if [[ "$target" == 0 ]]; then exec "$real" "$@"; fi
private=/github/workspace/gt-fft-bank-private
test -d "$private" && test -n "$run_id"
test "$log_count" = 1 && test "$log_index" -lt "${#args[@]}"
test "${args[log_index]}" = /dev/stdout
umask 077
ulimit -c 0
test -d "$private/vktrace" && test ! -L "$private/vktrace"
export VK_LAYER_PATH=/opt/gt-fft-layer
export VK_INSTANCE_LAYERS=VK_LAYER_GT_fft_capture
export GT_FFT_CAPTURE_DIR="$private/vktrace"
if [[ "$building" == 1 ]]; then
    logfile=bundle-build.log; stdout=bundle-build-stdout.log; marker=bundle-build-marker; exitfile=bundle-build-exit-code
else
    logfile=editor.log; stdout=editor-stdout.log; marker=editor-output-private; exitfile=editor-exit-code
fi
args[log_index]="$private/$logfile"
printf '%s\n' "$run_id" > "$private/$marker"
# Preserve the native process exit and a private launch marker even when
# the editor cannot enter its managed method. Raw output stays private.
set +e
{ "$real" "${args[@]}"; rc=$?; } > "$private/$stdout" 2>&1
set -e
printf '%s\n' "$rc" > "$private/$exitfile"
exit "$rc"
