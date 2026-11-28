#!/usr/bin/env bash
set -euo pipefail
real="$(cat /opt/gt-real-unity-editor)"
args=("$@")
target=0
run_id=
log_index=-1
log_count=0
for ((i=0;i<#{args[@]};i++)); do
  case "${args[i],,}" in
    -executemethod) if [[ "${args[i+1]:-}" == GTFFTImport.Run ]]; then target=1; fi;;
    -logfile) log_count=$((log_count+1));log_index=$((i+1));;
    -gtfftrunid) run_id="${args[i+1]:-}";;
  esac
done
if [[ "$target" == 0 ]];then exec "$real" "$@";fi
p=/github/workspace/gt-fft-exact-import
test -d "$p" && test -n "$run_id"
test "$log_count" = 1 && test "$log_index" -lt "${#args[@]}"
test "${args[log_index]}" = /dev/stdout
umask 077
ulimit -c 0
unset VK_INSTANCE_LAYERS VK_LAYER_PATH
args[log_index]="$p/editor-private.log"
printf '%s\n' "$run_id" > "$p/editor-run-marker"
set +e
"$real" "${args[@]}" > "$p/editor-stdout-private.log" 2>&1
rc=$?
set -e
printf '%s\n' "$rc" > "$p/editor-exit-code"
exit "$rc"
