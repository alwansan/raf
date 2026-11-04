#!/usr/bin/env bash
set -euo pipefail
DIR="$(mktemp -d)"
trap 'rm -rf "$DIR"' EXIT
javac -encoding UTF-8 -d "$DIR" \
  scripts/tests/org/json/JSONObject.java \
  app/src/main/java/com/alwansan/lograf/ErrorCategorySummary.java \
  app/src/main/java/com/alwansan/lograf/MemoryTelemetryQuality.java \
  app/src/main/java/com/alwansan/lograf/PidProbeObservation.java \
  scripts/tests/com/alwansan/lograf/DiagnosticRegression.java
java -cp "$DIR" com.alwansan.lograf.DiagnosticRegression
