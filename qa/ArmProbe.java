package org.raft.qa.armfixture;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

public final class ArmProbe extends Activity {
    private static final String TAG = "RaftQaArm";
    private static native int transform(int input);

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        System.loadLibrary("raftarmprobe");
        int a = transform(0x12345678);
        int b = transform(0x12345679);
        if (a != 17 || b != 18) {
            throw new IllegalStateException("Unexpected JNI results: " + a + "," + b);
        }
        String message = "ARM64_JNI_PASS results=" + a + "," + b;
        TextView text = new TextView(this);
        text.setText(message);
        setContentView(text);
        Log.i(TAG, message);
    }
}
