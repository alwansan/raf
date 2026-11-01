package com.alwansan.lograf;
interface ILogSink {
    void onBatch(String source, String content);
    void onFailure(String message);
}
