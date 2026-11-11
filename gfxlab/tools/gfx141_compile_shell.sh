#!/usr/bin/env bash
set -euo pipefail
jar="$(find "$ANDROID_HOME/platforms" -name android.jar | sort -V | tail -1)"
tools="$(find "$ANDROID_HOME/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -1)"
mkdir -p out/classes out/dex
"$tools/aapt2" link -o out/GFX124-unsigned-shell.apk --manifest gfxlab/android-gles-forward124/AndroidManifest.xml -I "$jar"
javac -source 8 -target 8 -bootclasspath "$jar" -d out/classes gfxlab/android-gles-forward124/src/com/alwansan/gfx124/MainActivity.java
mapfile -t classes < <(find out/classes -type f -name '*.class')
"$tools/d8" --lib "$jar" --min-api 29 --output out/dex "${classes[@]}"
python - <<'PY'
from zipfile import ZipFile, ZIP_DEFLATED
p = 'out/GFX124-unsigned-shell.apk'
with ZipFile(p, 'a', compression=ZIP_DEFLATED) as apk:
    apk.write('out/dex/classes.dex', 'classes.dex')
    assert {'classes.dex', 'AndroidManifest.xml'} <= set(apk.namelist())
    assert not any(name.startswith(('assets/', 'META-INF/')) for name in apk.namelist())
PY
"$tools/aapt2" dump badging out/GFX124-unsigned-shell.apk | grep -F "name='com.alwansan.gfx124'"
