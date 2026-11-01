package com.alwansan.lograf;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;

final class Config {
    static final String PACKAGE = "com.alwansan.raft.androidtest";
    static final String PREF = "lograf";
    static SharedPreferences prefs(Context c) { return c.getSharedPreferences(PREF, Context.MODE_PRIVATE); }
    static Uri folder(Context c) {
        String raw = prefs(c).getString("folder", "");
        return raw.isEmpty() ? null : Uri.parse(raw);
    }
    private Config() {}
}
