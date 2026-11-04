package com.alwansan.lograf;

/** Bounded, data-free user action marker shared by UI and saved raw stream. */
final class CaptureEventMarker {
    private CaptureEventMarker(){}
    static String encode(long unixMs,long elapsedMs){
        if(unixMs<=0 || elapsedMs<0)throw new IllegalArgumentException("invalid_marker_clock");
        return "[USER MARKER] timestamp_unix_ms="+unixMs+
                " elapsed_realtime_ms="+elapsedMs+
                " event=owner_reported_issue\n";
    }
}
