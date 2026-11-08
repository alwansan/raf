package com.alwansan.raftlab;

import java.io.IOException;
import java.io.InputStream;
import java.io.InterruptedIOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Bounded-memory SHA-256 for user-selected SAF streams, including multi-GiB APK/OBB.
 * Does not trust ContentResolver metadata or read the file into memory.
 */
public final class StreamSha256 {
    public static final long MAX_BYTES = 16L * 1024 * 1024 * 1024; // Allows original 10 GiB OBB.
    private static final int BUFFER_SIZE = 256 * 1024;
    private static final long PROGRESS_STEP = 16L * 1024 * 1024;

    private StreamSha256() {}

    public interface Progress {
        void bytesRead(long bytes);
    }

    public static final class Result {
        public final long bytes;
        public final String hex;
        Result(long bytes, String hex) {
            this.bytes = bytes;
            this.hex = hex;
        }
    }

    public static Result digest(InputStream input, Progress progress)
            throws IOException, NoSuchAlgorithmException {
        if (input == null) throw new IOException("Unreadable selected file");
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[BUFFER_SIZE];
        long total = 0;
        long notified = 0;
        int n;
        int consecutiveEmptyReads = 0;
        while ((n = input.read(buffer)) != -1) {
            if (Thread.currentThread().isInterrupted()) {
                throw new InterruptedIOException("SHA-256 cancelled");
            }
            if (n == 0) {
                // A non-empty read should not return zero. Bound broken SAF providers
                // rather than spinning forever with no progress or usable digest.
                if (++consecutiveEmptyReads >= 16) {
                    throw new IOException("Selected file provider returned repeated empty reads");
                }
                continue;
            }
            consecutiveEmptyReads = 0;
            if (total > MAX_BYTES - n) throw new IOException("Selected file exceeds 16 GiB safety limit");
            md.update(buffer, 0, n);
            total += n;
            if (progress != null && total - notified >= PROGRESS_STEP) {
                progress.bytesRead(total);
                notified = total;
            }
        }
        if (Thread.currentThread().isInterrupted()) throw new InterruptedIOException("SHA-256 cancelled");
        if (progress != null) progress.bytesRead(total);
        final char[] digits = "0123456789abcdef".toCharArray();
        byte[] hash = md.digest();
        char[] hex = new char[hash.length * 2];
        for (int i = 0; i < hash.length; i++) {
            hex[i * 2] = digits[(hash[i] >> 4) & 15];
            hex[i * 2 + 1] = digits[hash[i] & 15];
        }
        return new Result(total, new String(hex));
    }
}
