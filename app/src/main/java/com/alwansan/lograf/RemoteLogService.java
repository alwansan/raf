package com.alwansan.lograf;

import android.os.RemoteException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import org.json.JSONObject;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Runs as Shizuku's shell/root UID. All ordinary Raft lines use logcat --uid;
 * system context is selected separately and never dumped wholesale.
 */
public final class RemoteLogService extends IRemoteLog.Stub {
    private final AtomicBoolean running = new AtomicBoolean(false);
    private final AtomicLong gameLogLines=new AtomicLong(),systemContextLines=new AtomicLong(),reconnections=new AtomicLong();
    private volatile Process gameProcess, systemProcess;
    private volatile ILogSink listener;
    private volatile int gameUid;
    private volatile String packageName;
    private final Set<String> gamePids = java.util.Collections.synchronizedSet(new HashSet<>());
    private Thread gameThread, systemThread, pidThread, telemetryThread;
    private static final Pattern PID = Pattern.compile("^\\s*(?:\\d{4}-)?\\d\\d-\\d\\d\\s+\\d\\d:\\d\\d:\\d\\d[^ ]*\\s+(\\d+)\\s+");
    private static final Pattern CRASH_MARK = Pattern.compile("(?i)(FATAL EXCEPTION|Fatal signal|tombstone|crash_dump|am_crash|am_anr|Force finishing|ANR in|native crash|Fatal Java|Process:)");
    private static final int BATCH = 32768;
    private volatile long metricPreviousAt=-1, metricPreviousGameLines=0, metricPreviousSystemLines=0;

    public RemoteLogService() {}

    @Override public synchronized void start(int uid, String targetPackage, ILogSink sink) throws RemoteException {
        if (!Config.PACKAGE.equals(targetPackage) || uid < 10000 || sink == null) {
            throw new SecurityException("Refusing non-Raft target or invalid UID");
        }
        stop();
        listener = sink; gameUid = uid; packageName = targetPackage;
        gameLogLines.set(0);systemContextLines.set(0);reconnections.set(0);
        metricPreviousAt=-1;metricPreviousGameLines=0;metricPreviousSystemLines=0;
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
        telemetryThread=new Thread(()->new PerformanceSampler(packageName,this::currentPid,running,this::sendMetric).run(),"lograf-telemetry");
        telemetryThread.start();
    }

    private int currentPid() {
        synchronized(gamePids) {
            for(String pid:gamePids) {
                try {return Integer.parseInt(pid);} catch(NumberFormatException ignored){}
            }
        }
        return -1;
    }

    private void sendMetric(String line) {
        ILogSink sink=listener;
        if(sink!=null && running.get()) {
            try {
                JSONObject data=new JSONObject(line.trim());
                long now=android.os.SystemClock.elapsedRealtime();
                long gameLines=gameLogLines.get();
                long systemLines=systemContextLines.get();
                if(metricPreviousAt>0 && now>metricPreviousAt){
                    double seconds=(now-metricPreviousAt)/1000.0;
                    double rate=Math.max(0,gameLines-metricPreviousGameLines)/seconds;
                    data.put("game_log_lines_per_second",Math.round(rate*100.0)/100.0);
                    data.put("error_flood_warning",rate>=10000);
                    data.put("system_context_lines_per_second",Math.round(Math.max(0,systemLines-metricPreviousSystemLines)/seconds*100.0)/100.0);
                }
                metricPreviousAt=now;
                metricPreviousGameLines=gameLines;
                metricPreviousSystemLines=systemLines;
                data.put("game_log_lines",gameLines);
                data.put("system_context_lines",systemContextLines.get());
                data.put("logcat_reconnects",reconnections.get());
                data.put("logcat_unobserved_losses","unknown");
                sink.onBatch("METRICS",data.toString()+"\n");
            } catch(Exception e){error("Metrics delivery: "+e.getClass().getSimpleName());}
        }
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
                    while (running.get()) {
                        // readLine blocks indefinitely on a quiet logcat stream.
                        // Poll ready() so pending small batches are flushed within 0.7s.
                        if (!in.ready()) {
                            if (batch.length()>0 && System.nanoTime()-lastDelivery>700_000_000L) {
                                send(source,batch);
                                lastDelivery=System.nanoTime();
                            }
                            if (!p.isAlive()) break;
                            Thread.sleep(60);
                            continue;
                        }
                        line=in.readLine();
                        if(line==null)break;
                        if (line.startsWith("--------- beginning of ")) continue;
                        if (!onlyContext || systemRelevant(line)) {
                            if(onlyContext)systemContextLines.incrementAndGet();else gameLogLines.incrementAndGet();
                            batch.append(line).append('\n');
                            if (batch.length() >= BATCH || System.nanoTime()-lastDelivery>700_000_000L) {
                                send(source,batch);
                                lastDelivery=System.nanoTime();
                            }
                        }
                    }
                }
            } catch (Exception e) {
                if (running.get()) error(source + ": " + e);
                // The intentional logcat pipe close on Stop is not a recorder failure.
            } finally {
                if (batch.length() > 0) send(source,batch);
                if (p != null) { p.destroy(); }
            }
            if (!running.get()) break;
            reconnections.incrementAndGet();
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
        if (telemetryThread != null) telemetryThread.interrupt();
        // Close the pipe and deliver tail batches instead of discarding them.
        for (Thread t : new Thread[]{gameThread, systemThread}) {
            if (t != null && t != Thread.currentThread()) {
                try { t.join(1600); } catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
            }
        }
        gameProcess = null; systemProcess = null;
    }

    @Override public String status() {
        return "running=" + running.get() + " uid=" + gameUid + " pids=" + gamePids;
    }

    @Override public void destroy() { stop(); System.exit(0); }
}
