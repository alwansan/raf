package com.alwansan.lograf;

import android.os.RemoteException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Runs as Shizuku's shell/root UID. All ordinary Raft lines use logcat --uid;
 * system context is selected separately and never dumped wholesale.
 */
public final class RemoteLogService extends IRemoteLog.Stub {
    private final AtomicBoolean running = new AtomicBoolean(false);
    private volatile Process gameProcess, systemProcess;
    private volatile ILogSink listener;
    private volatile int gameUid;
    private volatile String packageName;
    private final Set<String> gamePids = java.util.Collections.synchronizedSet(new HashSet<>());
    private Thread gameThread, systemThread, pidThread;
    private static final Pattern PID = Pattern.compile("^\\s*(?:\\d{4}-)?\\d\\d-\\d\\d\\s+\\d\\d:\\d\\d:\\d\\d[^ ]*\\s+(\\d+)\\s+");
    private static final Pattern CRASH_MARK = Pattern.compile("(?i)(FATAL EXCEPTION|Fatal signal|tombstone|crash_dump|am_crash|am_anr|Force finishing|ANR in|native crash|Fatal Java|Process:)");
    private static final int BATCH = 4096;

    public RemoteLogService() {}

    @Override public synchronized void start(int uid, String targetPackage, ILogSink sink) throws RemoteException {
        if (!Config.PACKAGE.equals(targetPackage) || uid < 10000 || sink == null) {
            throw new SecurityException("Refusing non-Raft target or invalid UID");
        }
        stop();
        listener = sink; gameUid = uid; packageName = targetPackage;
        running.set(true);
        gameThread = new Thread(() -> pump("RAFT", new String[]{
                "logcat", "-b", "main", "-b", "system", "-b", "crash", "-b", "events",
                "-v", "threadtime", "-v", "uid", "-v", "year", "-v", "usec", "-v", "printable",
                "-T", "1", "--uid=" + gameUid, "*:V"
        }, false), "lograf-raft-uid");
        systemThread = new Thread(() -> pump("SYSTEM", new String[]{
                "logcat", "-b", "system", "-b", "crash", "-b", "events",
                "-v", "threadtime", "-v", "year", "-v", "usec", "-v", "printable",
                "-T", "1", "*:V"
        }, true), "lograf-system-context");
        pidThread = new Thread(this::watchPids, "lograf-pid-watch");
        gameThread.start(); systemThread.start(); pidThread.start();
    }

    private void watchPids() {
        while (running.get()) {
            Process p = null;
            try {
                p = new ProcessBuilder("pidof", packageName).redirectErrorStream(true).start();
                StringBuilder found = new StringBuilder();
                try (BufferedReader b = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8))) {
                    String line;
                    while ((line=b.readLine()) != null) found.append(line).append(" ");
                }
                Set<String> current = new HashSet<>();
                for (String item : found.toString().trim().split("\\s+")) {
                    if (item.matches("[0-9]+")) current.add(item);
                }
                synchronized (gamePids) { gamePids.clear(); gamePids.addAll(current); }
            } catch (Exception ignored) {
                // The UID stream does not depend on pidof.
            } finally { if (p != null) p.destroy(); }
            try { Thread.sleep(800); } catch (InterruptedException e) { return; }
        }
    }

    private boolean systemRelevant(String line) {
        if (line.contains(packageName)) return true;
        Matcher m = PID.matcher(line);
        if (m.find()) {
            synchronized (gamePids) {
                if (gamePids.contains(m.group(1))) return true;
            }
        }
        return false;
    }

    private void pump(String source, String[] command, boolean onlyContext) {
        int retries = 0;
        while (running.get()) {
            Process p = null;
            StringBuilder batch = new StringBuilder(BATCH * 2);
            try {
                p = new ProcessBuilder(command).redirectErrorStream(true).start();
                if (onlyContext) systemProcess = p; else gameProcess = p;
                retries = 0;
                try (BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream(), StandardCharsets.UTF_8), 65536)) {
                    String line;
                    long lastDelivery = System.nanoTime();
                    while (running.get() && (line = in.readLine()) != null) {
                        if (line.startsWith("--------- beginning of ")) {
                            // Preserve buffer boundaries even if no Raft activity.
                            continue;
                        }
                        if (!onlyContext || systemRelevant(line)) {
                            batch.append(line).append('\n');
                            if (batch.length() >= BATCH || (System.nanoTime()-lastDelivery)>800_000_000L) {
                                send(source,batch);
                                lastDelivery=System.nanoTime();
                            }
                        }
                    }
                }
            } catch (Exception e) {
                error(source + ": " + e);
            } finally {
                if (batch.length() > 0) send(source,batch);
                if (p != null) { p.destroy(); }
            }
            if (!running.get()) break;
            error(source + " stream closed; reconnecting (a short gap may occur)");
            try { Thread.sleep(Math.min(10000L, 1000L << Math.min(retries++,3))); }
            catch (InterruptedException e) { break; }
        }
    }

    private void send(String source, StringBuilder batch) {
        String text = batch.toString(); batch.setLength(0);
        if (text.isEmpty()) return;
        ILogSink sink = listener;
        if (sink == null) return;
        try { sink.onBatch(source,text); }
        catch (Exception e) { running.set(false); }
    }

    private void error(String message) {
        ILogSink sink = listener;
        if (sink != null) try { sink.onFailure(message); } catch (Exception ignored) {}
    }

    @Override public synchronized void stop() {
        running.set(false);
        if (gameProcess != null) gameProcess.destroy();
        if (systemProcess != null) systemProcess.destroy();
        if (gameThread != null) gameThread.interrupt();
        if (systemThread != null) systemThread.interrupt();
        if (pidThread != null) pidThread.interrupt();
        gameProcess = null; systemProcess = null;
    }

    @Override public String status() {
        return "running=" + running.get() + " uid=" + gameUid + " pids=" + gamePids;
    }

    @Override public void destroy() { stop(); System.exit(0); }
}
