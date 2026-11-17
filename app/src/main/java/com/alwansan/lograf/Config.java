package com.alwansan.lograf;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

final class Config {
    static final String PACKAGE = "com.cinemana.pro";
    static final String PREF = "clog";
    static SharedPreferences prefs(Context c) { return c.getSharedPreferences(PREF, Context.MODE_PRIVATE); }
    static Uri folder(Context c) {
        if(StorageAccess.direct(c)) return Uri.fromFile(StorageAccess.OUTPUT);
        String raw = prefs(c).getString("folder", "");
        return raw.isEmpty() ? null : Uri.parse(raw);
    }
    static Uri workLogsFolder(Context c) {
        if(StorageAccess.direct(c)) return Uri.fromFile(StorageAccess.WORK);
        String raw=prefs(c).getString("work_logs_folder","");
        return raw.isEmpty()?null:Uri.parse(raw);
    }
    private Config() {}
}
