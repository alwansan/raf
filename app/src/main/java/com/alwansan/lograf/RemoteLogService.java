package com.alwansan.lograf;

import android.os.RemoteException;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicInteger;
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
    private final AtomicLong shaderPassErrors=new AtomicLong(),kernelErrors=new AtomicLong(),missingAssetPaths=new AtomicLong();
    private final ErrorCategorySummary errorGroups=new ErrorCategorySummary();
    private final AtomicLong javaFatalMarkers=new AtomicLong(),nativeFatalMarkers=new AtomicLong(),processDeathEvents=new AtomicLong();
    private volatile Process gameProcess, systemProcess;
    private volatile ILogSink listener;
    private volatile int gameUid;
    private volatile String packageName;
    private final AtomicInteger lastDeathPid=new AtomicInteger(-1);
    private final AtomicInteger lastKnownPid=new AtomicInteger(-1);
    private final AtomicLong lastDeathAtUnixMs=new AtomicLong(-1);
    private final Set<String> gamePids = java.util.Collections.synchronizedSet(new HashSet<>());
    private final AtomicInteger primaryGamePid=new AtomicInteger(-1);
    private final AtomicLong pidProbeFailures=new AtomicLong();
    private final AtomicLong pidProbeSuccesses=new AtomicLong();
    private volatile String pidProbeStatus="not_started";
    private volatile String pidProbeFailureReason="none";
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
        shaderPassErrors.set(0);kernelErrors.set(0);missingAssetPaths.set(0);
        javaFatalMarkers.set(0);nativeFatalMarkers.set(0);processDeathEvents.set(0);
        errorGroups.reset();
        lastDeathPid.set(-1);lastKnownPid.set(-1);lastDeathAtUnixMs.set(-1);
        primaryGamePid.set(-1);
        pidProbeFailures.set(0);pidProbeSuccesses.set(0);pidProbeStatus="not_started";pidProbeFailureReason="none";
        synchronized(gamePids){gamePids.clear();}
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
        // A HashSet iteration is nondeterministic. The sampler must never
        // switch to a :worker process or invent a PID on an unreadable /proc.
        return primaryGamePid.get();
    }

    private static String processCmdline(int pid) {
        if(pid<=0)return null;
        try(FileInputStream in=new FileInputStream("/proc/"+pid+"/cmdline")){
            byte[] buf=new byte[256];
            int n=in.read(buf);
            if(n<=0)return null;
            int end=0;
            while(end<n && buf[end]!=0)end++;
            return new String(buf,0,end,StandardCharsets.UTF_8);
        }catch(Exception ignored){return null;}
    }

    private int findMainPid(Set<String> candidates) {
        int selected=-1;
        for(String item:candidates){
            try{
                int pid=Integer.parseInt(item);
                if(packageName.equals(processCmdline(pid)) &&
                        (selected<0 || pid<selected))selected=pid;
            }catch(NumberFormatException ignored){}
        }
        return selected;
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
                data.put("pid_probe_status",pidProbeStatus);
                data.put("pid_probe_failure_reason",pidProbeFailureReason);
                data.put("pid_probe_failures_total",pidProbeFailures.get());
                data.put("pid_probe_successes_total",pidProbeSuccesses.get());
                data.put("main_process_pid_verified",primaryGamePid.get()>0);
                if("pidof_probe_failed".equals(pidProbeStatus) ||
                        "main_cmdline_unverified".equals(pidProbeStatus)){
                    // The sampler sees PID=-1, but failed discovery is NOT
                    // evidence that the game exited. Preserve raw process
                    // transition separately as an unverified observation.
                    if("game_exited".equals(data.optString("process_transition")))
                        data.put("process_transition","pid_tracking_lost_unverified");
                    if("game_not_running".equals(data.optString("state")))
                        data.put("state","game_process_state_unknown");
                }
                data.put("system_context_lines",systemContextLines.get());
                data.put("logcat_reconnects",reconnections.get());
                data.put("shader_pass_errors_total",shaderPassErrors.get());
                data.put("invalid_compute_kernel_total",kernelErrors.get());
                data.put("missing_asset_path_errors_total",missingAssetPaths.get());
                data.put("java_fatal_markers_total",javaFatalMarkers.get());
                data.put("native_fatal_markers_total",nativeFatalMarkers.get());
                data.put("game_process_death_events_total",processDeathEvents.get());
                data.put("process_exit_reason","unknown; process death alone is not a crash");
                data.put("error_groups",errorGroups.snapshot());
                data.put("error_groups_note","fixed categories only; original messages remain in raw Logcat");
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
                // A wedged pidof must not freeze this thread indefinitely.
                // pidof emits only a short PID list; wait for completion before
                // reading, with a strict timeout and bounded output.
                if(!p.waitFor(2000,java.util.concurrent.TimeUnit.MILLISECONDS)){
                    p.destroyForcibly();
                    throw new IOException("pidof_timeout");
                }
                StringBuilder found = new StringBuilder();
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(p.getInputStream(),StandardCharsets.UTF_8))) {
                    char[] chars=new char[256];
                    int n;
                    while(found.length()<=4096 && (n=reader.read(chars,0,
                            Math.min(chars.length,4097-found.length())))!=-1)
                        found.append(chars,0,n);
                    // Never interpret a truncated numeric PID as a valid one.
                    // The extra character distinguishes an exact 4096-byte
                    // response from a response exceeding the safety limit.
                    if(found.length()>4096)
                        throw new IOException("pidof_output_overflow");
                }
                Set<String> current = new HashSet<>();
                String pidOutput=found.toString().trim();
                // A successful probe must contain only PID tokens. A shell
                // diagnostic mixed into stdout must never become an apparent
                // game exit or an unverified process treated as absent.
                if(!pidOutput.isEmpty()) {
                    for(String item:pidOutput.split("\\s+")) {
                        if(!item.matches("[0-9]+"))
                            throw new IOException("pidof_invalid_output");
                        current.add(item);
                    }
                }
                // pidof may print a diagnostic instead of a PID, or exit
                // nonzero. Never treat that as proof the game has exited.
                int exit=p.exitValue();
                // Android toybox pidof exits 1 when no matching process
                // exists. That is a valid empty observation, not an I/O
                // failure. A nonzero exit with PIDs or diagnostic output
                // remains unverified; never fabricate a game exit.
                boolean verifiedEmpty=exit==1 && found.toString().trim().isEmpty();
                if(exit!=0 && !verifiedEmpty)
                    throw new IOException("pidof_nonzero_exit");
                // Exit 0 without a PID is ambiguous, not confirmed absence.
                if(exit==0 && current.isEmpty())
                    throw new IOException("pidof_empty_success");
                pidProbeSuccesses.incrementAndGet();
                pidProbeFailureReason="none";
                // Preserve all PIDs for system-context correlation, but only
                // sample CPU/RSS/FPS for the exact main process. If /proc is
                // inaccessible, mark PID unavailable instead of guessing.
                int main=findMainPid(current);
                synchronized (gamePids) { gamePids.clear(); gamePids.addAll(current); }
                primaryGamePid.set(main);
                pidProbeStatus=main>0?"main_pid_verified":
                        current.isEmpty()?"pidof_empty":"main_cmdline_unverified";
                if(main>0)lastKnownPid.set(main);
            } catch (Exception probeError) {
                // Stable, bounded reason codes; never export command output or paths.
                String reason=probeError.getMessage();
                pidProbeFailureReason=reason!=null && (reason.equals("pidof_timeout") ||
                        reason.equals("pidof_output_overflow") ||
                        reason.equals("pidof_invalid_output") ||
                        reason.equals("pidof_empty_success") ||
                        reason.equals("pidof_nonzero_exit")) ? reason : "pidof_execution_error";
                pidProbeFailures.incrementAndGet();
                pidProbeStatus="pidof_probe_failed";
                // A failed pidof invocation must not leave a stale main PID
                // behind. Otherwise the sampler can attribute CPU/RSS and
                // process transitions to a PID which is no longer the game.
                // Keep UID-filtered Logcat capture alive independently.
                primaryGamePid.set(-1);
                synchronized(gamePids){gamePids.clear();}
            } finally { if (p != null) p.destroy(); }
            try { Thread.sleep(800); } catch (InterruptedException e) { return; }
        }
    }

    // Reject substring-only matches (com.alwansan.raft.androidtest, :worker).
    // Keep punctuation boundaries because system events can include a package
    // followed by a comma, slash, space or closing bracket.
    private static boolean containsExactPackage(String line,String target) {
        if(line==null || target==null || target.isEmpty())return false;
        int from=0;
        while((from=line.indexOf(target,from))>=0){
            int end=from+target.length();
            boolean left=from==0 || !isPackageCharacter(line.charAt(from-1));
            boolean right=end==line.length() || !isPackageCharacter(line.charAt(end));
            if(left && right)return true;
            from=end;
        }
        return false;
    }

    private static boolean isPackageCharacter(char c) {
        return (c>='a'&&c<='z') || (c>='A'&&c<='Z') ||
                (c>='0'&&c<='9') || c=='_' || c=='.' || c==':';
    }

    private boolean systemRelevant(String line) {
        if (containsExactPackage(line,packageName)) return true;
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
                            if(onlyContext) {
                                systemContextLines.incrementAndGet();
                                if(line.contains("am_proc_died") && line.contains(packageName)){
                                    // Count ONLY parseable death events for the exact target.
                                    // A substring match alone can select a different process
                                    // (e.g. com.alwansan.raft.androidtest:worker).
                                    Matcher died=Pattern.compile(
                                            "\\[\\s*\\d+\\s*,\\s*(\\d+)\\s*,\\s*([^,\\]]+)").matcher(line);
                                    if(died.find() && packageName.equals(died.group(2).trim())){
                                        try{
                                            int exactPid=Integer.parseInt(died.group(1));
                                            if(exactPid>0){
                                                processDeathEvents.incrementAndGet();
                                                lastDeathPid.set(exactPid);
                                                lastDeathAtUnixMs.set(System.currentTimeMillis());
                                            }
                                        }catch(NumberFormatException ignored){}
                                    }
                                }
                            } else {
                                gameLogLines.incrementAndGet();
                                errorGroups.observe(line);
                                if(line.contains("Invalid pass number") && line.contains("Graphics.Blit"))
                                    shaderPassErrors.incrementAndGet();
                                if(line.contains("Invalid kernelIndex"))
                                    kernelErrors.incrementAndGet();
                                if(line.contains("DirectoryNotFoundException"))
                                    missingAssetPaths.incrementAndGet();
                                if(line.contains("FATAL EXCEPTION"))
                                    javaFatalMarkers.incrementAndGet();
                                if(line.contains("Fatal signal") || line.contains("SIGSEGV") || line.contains("SIGABRT"))
                                    nativeFatalMarkers.incrementAndGet();
                            }
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
        primaryGamePid.set(-1);
    }

    @Override public String finalExitEvidence() {
        JSONObject evidence=new JSONObject();
        try {
            int pid=lastDeathPid.get();
            evidence.put("target_package",Config.PACKAGE);
            evidence.put("source","Shizuku shell / Android ActivityManager exit-info");
            evidence.put("last_system_death_pid",pid>0?pid:JSONObject.NULL);
            evidence.put("last_system_death_observed_unix_ms",
                    lastDeathAtUnixMs.get()>0?lastDeathAtUnixMs.get():JSONObject.NULL);
            evidence.put("system_death_event_count",processDeathEvents.get());
            evidence.put("cause_warning","Signal 9 means SIGKILL; its sender and motive are not established by exit-info alone");
            if(pid<=0){
                evidence.put("status","no_game_death_event_observed");
                return evidence.toString();
            }
            String snapshot=PerformanceSampler.command(2400,24000,"dumpsys","activity",
                    "exit-info",Config.PACKAGE);
            // Select only the record for the precise PID that Logcat observed.
            // Android may localize timestamps with Arabic digits, so match the
            // ASCII PID/reason/status tokens rather than interpreting the date.
            String[] lines=snapshot.split("\\n");
            for(int i=0;i<lines.length;i++){
                String line=lines[i];
                if(!line.contains("pid="+pid+" ") && !line.endsWith("pid="+pid))
                    continue;
                evidence.put("matched_pid",pid);
                evidence.put("exit_header",line.trim().length()>450?
                        line.trim().substring(0,450):line.trim());
                if(i+1<lines.length){
                    String details=lines[i+1].trim();
                    java.util.regex.Matcher reason=Pattern.compile(
                        "reason=([0-9]+) \\(([^)]*)\\)").matcher(details);
                    java.util.regex.Matcher status=Pattern.compile(
                        "\\bstatus=([0-9]+)").matcher(details);
                    java.util.regex.Matcher subreason=Pattern.compile(
                        "subreason=([0-9]+) \\(([^)]*)\\)").matcher(details);
                    if(reason.find()){
                        evidence.put("android_exit_reason_code",Integer.parseInt(reason.group(1)));
                        evidence.put("android_exit_reason_label",reason.group(2));
                    }
                    if(status.find())evidence.put("signal_or_exit_status",
                            Integer.parseInt(status.group(1)));
                    if(subreason.find()){
                        evidence.put("android_exit_subreason_code",Integer.parseInt(subreason.group(1)));
                        evidence.put("android_exit_subreason_label",subreason.group(2));
                    }
                }
                evidence.put("status","matched_pid_in_android_exit_history");
                return evidence.toString();
            }
            evidence.put("status","exit_history_pending_or_pid_not_found");
        }catch(Exception err){
            try{evidence.put("status","exit_history_unavailable:"+err.getClass().getSimpleName());}
            catch(Exception ignored){}
        }
        return evidence.toString();
    }

    @Override public String status() {
        return "running=" + running.get() + " uid=" + gameUid + " mainPid=" + primaryGamePid.get() + " pids=" + gamePids;
    }

    @Override public void destroy() { stop(); System.exit(0); }
}
