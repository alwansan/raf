#!/usr/bin/env python3
"""CLog source-level safety and isolation checks; does not replace device testing."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
app=root/"app/src/main/java/com/alwansan/lograf"
config=(app/"Config.java").read_text()
manifest=(root/"app/src/main/AndroidManifest.xml").read_text()
gradle=(root/"app/build.gradle").read_text()
remote=(app/"RemoteLogService.java").read_text()
perf=(app/"PerformanceSampler.java").read_text()
collector=(app/"CinemanaWorkLogCollector.java").read_text()
service=(app/"CaptureService.java").read_text()
ui=(app/"MainActivity.java").read_text()
counters=(app/"CinemanaEventCounters.java").read_text()

assert 'static final String PACKAGE = "com.cinemana.pro"' in config
assert "applicationId 'com.alwansan.clog'" in gradle
assert '<package android:name="com.cinemana.pro"/>' in manifest
assert 'android:label="CLog"' in manifest
assert "com.alwansan.raft.androidtest" not in config+manifest
assert '"--uid=" + gameUid' in remote
assert 'packageName+":filedownloader"' in remote
assert 'new PerformanceSampler(packageName,this::currentPid,this::currentDownloaderPid' in remote
assert "cinemanaCounters.observe(line,onlyContext)" in remote
assert "CinemanaEventCounters" in remote
assert "mkv_ffmpeg_acquired" in counters and "mkv_ffmpeg_released" in counters
assert "android_anrs" in counters and "art_verify_errors" in counters
assert '"filedownloader"' in perf and '"android_ui_gfxinfo"' in perf
assert '"dumpsys","gfxinfo",target' in perf
assert "source files never edited" in service
assert "getContentResolver(),internal,sessionFolder,workLogRunning" in service
assert "writeSessionSummary(status)" in service
assert "new CinemanaWorkLogCollector" in service
assert 'DocumentsContract.buildChildDocumentsUriUsingTree' in collector
assert 'resolver.openFileDescriptor(source,"r")' in collector
assert 'MAX_FILES_PER_POLL=20' in collector
assert 'CHUNK_LIMIT=256*1024' in collector
assert 'SEGMENT_LIMIT=16L*1024L*1024L' in collector
assert 'PICK_WORK_LOGS=203' in ui
assert '"work_logs_folder"' in ui
for forbidden in ("deleteDocument(", "openFileDescriptor(source,\"w\"", "Runtime.getRuntime().exec", "POST /upload"):
    assert forbidden not in collector, forbidden
print("CLog isolation, multi-process capture, telemetry, optional SAF and signing scope: PASS")
