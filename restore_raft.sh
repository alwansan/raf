#!/usr/bin/env bash
set -Eeuo pipefail
BASE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$BASE/Raft"
MANIFEST="$BASE/RAFT_FILE_MANIFEST.tsv"
OUT="${1:-"$(dirname "$BASE")/Raft-restored"}"
[[ -f "$MANIFEST" && -d "$SOURCE" ]] || { echo 'Manifest/Raft missing' >&2; exit 1; }
mkdir -p -- "$OUT"
OUT="$(cd "$OUT" && pwd)"
[[ "$OUT" != "$SOURCE" && "$OUT" != "$SOURCE/"* ]] || { echo 'Refusing to overwrite upload source' >&2; exit 1; }
count=0
while IFS=$'\t' read -r kind bytes sha mode rel; do
  [[ "$kind" == 'kind' ]] && continue
  [[ -n "$kind" && -n "$rel" ]] || { echo 'Bad manifest line' >&2; exit 1; }
  src="$SOURCE/$rel"
  dst="$OUT/$rel"
  mkdir -p -- "$(dirname "$dst")"
  temp="$dst.raft-restore-incomplete"
  if [[ "$kind" == 'split' ]]; then
    [[ -d "$src" ]] || { echo "Missing chunk directory: $src" >&2; exit 1; }
    cat -- "$src"/part-* > "$temp"
  elif [[ "$kind" == 'plain' ]]; then
    [[ -f "$src" ]] || { echo "Missing file: $src" >&2; exit 1; }
    cp -- "$src" "$temp"
  else
    echo "Unexpected file type: $kind" >&2; exit 1
  fi
  actual_size="$(stat -c '%s' -- "$temp")"
  actual_sha="$(sha256sum -- "$temp")"
  actual_sha="${actual_sha%% *}"
  [[ "$actual_size" == "$bytes" && "$actual_sha" == "$sha" ]] || {
    echo "FAILED SHA-256/size check: $rel" >&2; exit 1;
  }
  mv -f -- "$temp" "$dst"
  chmod "$mode" "$dst" 2>/dev/null || true
  ((count+=1))
done < "$MANIFEST"
echo "SUCCESS: restored and SHA-256-verified $count files into $OUT"
