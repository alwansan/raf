package com.alwansan.raftlab;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InterruptedIOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;

/** Standalone JDK 17 fixture: tests the actual streamed production implementation. */
public final class T5StreamSha256Test {
    private static final String EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
    private static final String ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
    private static int checks = 0;
    private static void check(boolean yes, String label) {
        if (!yes) throw new AssertionError(label);
        checks++;
    }

    private static final class ZeroStream extends InputStream {
        long left;
        ZeroStream(long bytes) { left = bytes; }
        @Override public int read() { if (left <= 0) return -1; left--; return 0; }
        @Override public int read(byte[] target, int off, int len) {
            if (left <= 0) return -1;
            int n = (int) Math.min((long)len, left);
            Arrays.fill(target, off, off + n, (byte)0);
            left -= n;
            return n;
        }
    }
    private static void testKnownVectors() throws Exception {
        check(StreamSha256.digest(new ByteArrayInputStream(new byte[0]), null).hex.equals(EMPTY), "empty sha");
        StreamSha256.Result abc = StreamSha256.digest(
            new ByteArrayInputStream("abc".getBytes(StandardCharsets.US_ASCII)), null);
        check(abc.bytes == 3 && abc.hex.equals(ABC), "abc sha and size");
    }
    private static void testBeyondLegacyLimit() throws Exception {
        final long size = 70L * 1024 * 1024 + 17; // Legacy host rejected >64MiB.
        final ArrayList<Long> positions = new ArrayList<>();
        StreamSha256.Result result = StreamSha256.digest(new ZeroStream(size), positions::add);
        check(result.bytes == size, "70MiB+ long size");
        check(result.hex.length() == 64 && result.hex.matches("[0-9a-f]{64}"), "SHA hex format");
        check(!positions.isEmpty() && positions.get(positions.size()-1) == size, "final progress");
        long prev = -1;
        for (long n : positions) {
            check(n > prev, "progress strictly increasing");
            prev = n;
        }
    }
    private static void testOriginalObbByteCount() throws Exception {
        // Synthetic zero stream of the known 2,301,256,312-byte OBB size;
        // no original assets and no multi-GiB memory/disk allocation.
        final long size = 2301256312L;
        StreamSha256.Result r = StreamSha256.digest(new ZeroStream(size), null);
        check(r.bytes == size && r.bytes > Integer.MAX_VALUE, "long byte counter > 2GiB");
        check(r.hex.equals("fca7c0f70c873f1e0b0b17bc96ecfdfa3fde05b7da982e7098455f1dad7a698d"),
            "2.3GB synthetic zero stream SHA-256 digest");
    }
    private static void testInterrupted() throws Exception {
        Thread.currentThread().interrupt();
        boolean rejected = false;
        try { StreamSha256.digest(new ZeroStream(1024), null); }
        catch (InterruptedIOException expected) { rejected = true; }
        finally { Thread.interrupted(); }
        check(rejected, "honors interruption");
    }
    private static void testInputFailure() throws Exception {
        InputStream bad = new InputStream() {
            @Override public int read() throws IOException { throw new IOException("provider failed"); }
            @Override public int read(byte[] b,int off,int len) throws IOException {
                throw new IOException("provider failed");
            }
        };
        boolean rejected = false;
        try { StreamSha256.digest(bad, null); }
        catch (IOException expected) { rejected = true; }
        check(rejected, "propagates SAF provider failure; no partial SHA success");
    }
    private static void testRepeatedEmptyReads() throws Exception {
        InputStream broken = new InputStream() {
            @Override public int read() { return 0; }
            @Override public int read(byte[] b, int off, int len) { return 0; }
        };
        boolean rejected = false;
        try { StreamSha256.digest(broken, null); }
        catch (IOException expected) {
            rejected = expected.getMessage().contains("repeated empty reads");
        }
        check(rejected, "broken SAF stream fails boundedly instead of infinite loop");
        InputStream transientZero = new InputStream() {
            int zeros = 3;
            @Override public int read() { return -1; }
            @Override public int read(byte[] b, int off, int len) {
                if (zeros-- > 0) return 0;
                if (zeros == -1) { b[off] = (byte)'a'; return 1; }
                return -1;
            }
        };
        StreamSha256.Result result = StreamSha256.digest(transientZero, null);
        check(result.bytes == 1, "transient empty reads do not reject valid subsequent data");
    }
    public static void main(String[] args) throws Exception {
        testKnownVectors();
        testBeyondLegacyLimit();
        testOriginalObbByteCount();
        testInterrupted();
        testInputFailure();
        testRepeatedEmptyReads();
        System.out.println("PASS T5 StreamSha256 regression checks=" + checks);
    }
}
