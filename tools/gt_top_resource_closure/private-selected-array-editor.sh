#!/usr/bin/env bash
# All raw editor output for the exact original-resource method stays runner-local.
set -euo pipefail
real="$(cat /opt/gt-real-unity-editor)"
args=("$@")
target=0
run_id=
log_index=-1
log_count=0
for ((i=0;i<${#args[@]};i++)); do
    case "${args[i],,}" in
        -executemethod)
            if [[ "${args[i+1]:-}" == SelectedArrayUnity.Run ]]; then target=1; fi ;;
        -logfile)
            log_count=$((log_count+1))
            log_index=$((i+1));;
        -gtarrayrunid) run_id="${args[i+1]:-}";;
    esac
done
if [[ "$target" == 0 ]]; then exec "$real" "$@"; fi
private=/github/workspace/gt-selected-array-private
test -d "$private" && test -n "$run_id"
test "$log_count" = 1 && test "$log_index" -lt "${#args[@]}"
test "${args[log_index]}" = /dev/stdout
umask 077
args[log_index]="$private/editor.log"
printf '%s\n' "$run_id" > "$private/editor-output-private"
exec "$real" "${args[@]}" > "$private/editor-stdout.log" 2>&1
