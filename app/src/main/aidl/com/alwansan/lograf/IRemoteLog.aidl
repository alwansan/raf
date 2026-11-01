package com.alwansan.lograf;
import com.alwansan.lograf.ILogSink;
interface IRemoteLog {
    void destroy() = 16777114;
    void start(int uid, String targetPackage, ILogSink sink);
    void stop();
    String status();
}
