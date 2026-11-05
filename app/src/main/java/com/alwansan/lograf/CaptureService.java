package com.alwansan.lograf;

import android.app.*;
import android.content.*;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.*;
import android.provider.DocumentsContract;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;
import org.json.JSONArray;
import rikka.shizuku.Shizuku;

public final class CaptureService extends Service {
    public static final String START="com.alwansan.lograf.START";
    public static final String STOP="com.alwansan.lograf.STOP";
    public static final String MARK="com.alwansan.lograf.MARK";
    private static final String CHANNEL="record";
    private static final int NOTIFICATION=11;
    private static final long SEGMENT_BYTES=32L*1024*1024;
    private final Object writeLock = new Object();
    // Never hold a SAF provider write lock on the incoming Binder callback.
    // Bounded buffer (512 batches, hard 12 MiB); on overload fail visibly, not silently.
    private static final long QUEUE_BYTES_LIMIT = 12L*1024*1024;
    private static final int QUEUE_BATCH_LIMIT = 512;
    private final ArrayBlockingQueue<LogChunk> writeQueue=new ArrayBlockingQueue<>(QUEUE_BATCH_LIMIT);
    private final AtomicLong pendingBytes=new AtomicLong(),peakPendingBytes=new AtomicLong();
    private final AtomicLong receivedBatches=new AtomicLong(),writtenBatches=new AtomicLong();
    private final AtomicLong failedBatches=new AtomicLong(),maxQueueDelayMs=new AtomicLong();
    private final AtomicLong markerEnqueued=new AtomicLong(),markerWritten=new AtomicLong();
    private volatile Thread writerThread;
    private volatile String writerFailure="";
    private volatile String stopExitEvidence="";
    private final SessionMetricsSummary sessionMetrics=new SessionMetricsSummary();

    private static final class LogChunk {
        final String source,content;
        final byte[] bytes;
        final long enqueuedAt;
        LogChunk(String source,String content){
            this.source=source;
            this.content=content;
            this.bytes=(("METRICS".equals(source) || "MARKER".equals(source))?content:"["+source+"]\n"+content)
                    .getBytes(StandardCharsets.UTF_8);
            this.enqueuedAt=SystemClock.elapsedRealtime();
        }
    }

    private void enqueue(String source,String content) {
        // Accept final reader batches during remote.stop(); active becomes false only after tail delivery.
        if(!active)return;
        final LogChunk chunk=new LogChunk(source,content);
        final long pending=pendingBytes.addAndGet(chunk.bytes.length);
        if(pending>QUEUE_BYTES_LIMIT){
            pendingBytes.addAndGet(-chunk.bytes.length);
            failedBatches.incrementAndGet();
            fatal("LOG BUFFER OVERFLOW: queued bytes exceeded 12 MiB; recording stopped. "+
                    "Some unqueued lines may be missing; reduce log flood or use faster storage.");
            return;
        }
        peakPendingBytes.accumulateAndGet(pending,Math::max);
        boolean added=false;
        try {added=writeQueue.offer(chunk,"MARKER".equals(source)?0:1200,TimeUnit.MILLISECONDS);}
        catch(InterruptedException e){Thread.currentThread().interrupt();}
        if(!added){
            pendingBytes.addAndGet(-chunk.bytes.length);
            failedBatches.incrementAndGet();
            fatal("LOG BUFFER OVERFLOW: writer fell behind SAF storage; recording stopped "+
                    "with an explicit gap warning.");
        }else {
            receivedBatches.incrementAndGet();
            if("MARKER".equals(source))markerEnqueued.incrementAndGet();
        }
    }

    private void startWriter() {
        writeQueue.clear();
        pendingBytes.set(0);peakPendingBytes.set(0);
        receivedBatches.set(0);writtenBatches.set(0);failedBatches.set(0);
        maxQueueDelayMs.set(0);markerEnqueued.set(0);markerWritten.set(0);
        writerFailure="";stopExitEvidence="";
        sessionMetrics.reset();
        writerThread=new Thread(()->{
            // Stop only after remote.stop() has finished sending tail batches
            // and the queue has drained. Each entry is retained in FIFO order.
            while(active || !writeQueue.isEmpty()){
                LogChunk item=null;
                try{
                    item=writeQueue.poll(180,TimeUnit.MILLISECONDS);
                    if(item==null)continue;
                    long lag=SystemClock.elapsedRealtime()-item.enqueuedAt;
                    maxQueueDelayMs.accumulateAndGet(Math.max(0,lag),Math::max);
                    synchronized(writeLock){
                        if("METRICS".equals(item.source)){
                            if(metricsOutput==null ||
                                    metricsSegmentBytes+item.bytes.length>METRICS_SEGMENT_BYTES)
                                openMetricSegment();
                            metricsOutput.write(item.bytes);
                            metricsOutput.flush();
                            metricsSegmentBytes+=item.bytes.length;totalBytes+=item.bytes.length;
                            sessionMetrics.add(item.content);
                            android.content.SharedPreferences.Editor edit=Config.prefs(CaptureService.this)
                                    .edit().putString("metrics_last",item.content);
                            if(item.content.contains("\"exit_history_status\"")){
                                edit.putString("last_exit_history_sample",item.content);
                                try{edit.putString("exit_history_status",
                                        new org.json.JSONObject(item.content.trim())
                                                .optString("exit_history_status",""));}
                                catch(org.json.JSONException ignored){}
                            }
                            edit.apply();
                        }else{
                            if(output==null || segmentBytes+item.bytes.length>SEGMENT_BYTES)
                                openSegment();
                            output.write(item.bytes);
                            segmentBytes+=item.bytes.length;totalBytes+=item.bytes.length;
                            if("MARKER".equals(item.source) || SystemClock.elapsedRealtime()-lastWriterFlush>1200){
                                output.flush();
                                lastWriterFlush=SystemClock.elapsedRealtime();
                            }
                        }
                        writtenBatches.incrementAndGet();
                        if("MARKER".equals(item.source)){
                            markerWritten.incrementAndGet();
                            saveStatus("Issue marker written to session log");
                        }
                        if(System.currentTimeMillis()-lastStatus>1500){
                            Config.prefs(CaptureService.this).edit()
                                    .putLong("writer_pending_bytes",pendingBytes.get())
                                    .putLong("writer_max_lag_ms",maxQueueDelayMs.get())
                                    .putLong("writer_failed_batches",failedBatches.get()).apply();
                            saveStatus("Recording Raft • "+(totalBytes/1024)+" KiB");
                        }
                    }
                }catch(InterruptedException interrupted){
                    // Intentional Stop does NOT interrupt this thread: it must drain.
                    if(!active && writeQueue.isEmpty())break;
                }catch(Exception e){
                    writerFailure=e.getClass().getSimpleName()+": "+e.getMessage();
                    failedBatches.incrementAndGet();
                    fatal("Storage writer failed: "+writerFailure+
                            "; recording stopped; queued data might be incomplete");
                    break;
                }finally{
                    if(item!=null)pendingBytes.addAndGet(-item.bytes.length);
                }
            }
            synchronized(writeLock){
                try{if(output!=null)output.flush();}catch(Exception ignored){}
                try{if(metricsOutput!=null)metricsOutput.flush();}catch(Exception ignored){}
            }
        },"lograf-saf-writer");
        writerThread.setPriority(Thread.NORM_PRIORITY-1);
        writerThread.start();
    }

    private volatile long lastWriterFlush=0;
    private OutputStream output, metricsOutput;
    private long metricsSegmentBytes;
    private int metricsPart;
    private static final long METRICS_SEGMENT_BYTES=8L*1024*1024;
    private Uri folder, sessionFolder;
    private final ArrayList<String> fileUris = new ArrayList<>();
    private long segmentBytes, totalBytes, lastStatus;
    private int part;
    private volatile boolean active;
    private volatile boolean failed, stopping, starting;
    private volatile long startupRequestedElapsedMs=-1, startupReadyElapsedMs=-1;
    private volatile String startupPhase="not_started";
    // All session creation, shutdown and privileged Binder setup are serialized
    // off the Android service main looper. SAF can block for seconds on MediaProvider.
    private final ExecutorService lifecycle=Executors.newSingleThreadExecutor(r->{
        Thread t=new Thread(r,"lograf-control");
        t.setPriority(Thread.NORM_PRIORITY-1);
        return t;
    });
    private IRemoteLog remote;
    private String session;
    private Shizuku.UserServiceArgs args;

    private final ILogSink.Stub sink = new ILogSink.Stub() {
        @Override public void onBatch(String source,String content){
            enqueue(source,content);
        }
        @Override public void onFailure(String message){
            enqueue("WARNING","[RECORDER WARNING] "+message+"\n");
            saveStatus("Warning: "+message);
        }
    };

    private final ServiceConnection connection=new ServiceConnection() {
        @Override public void onServiceConnected(ComponentName component, IBinder binder) {
            final IRemoteLog bound=IRemoteLog.Stub.asInterface(binder);
            // remote.start may synchronously wait for a Shizuku Binder; Android
            // dispatches onServiceConnected on the app main thread by default.
            // A late Shizuku callback after Stop must not enqueue work on
            // a destroyed executor or revive an already closed session.
            if(lifecycle.isShutdown() || !active || stopping || failed)return;
            try {
                lifecycle.execute(()->{
                if(!active || stopping || failed)return;
                try {
                    ApplicationInfo info=getPackageManager().getApplicationInfo(Config.PACKAGE,0);
                    remote=bound;
                    bound.start(info.uid,Config.PACKAGE,sink);
                    startupReadyElapsedMs=SystemClock.elapsedRealtime();
                    startupPhase="remote_started";
                    saveStatus("Recording: " + Config.PACKAGE + " (UID " + info.uid + ")");
                } catch(Exception e){fatal("Cannot start privileged capture: " + e);}
            });
            } catch(java.util.concurrent.RejectedExecutionException ignored) {
                // Service already destroyed; never revive a finished session.
            }
        }
        @Override public void onServiceDisconnected(ComponentName component) {
            remote=null;
            if(active && !stopping) fatal("Shizuku disconnected; capture ended. Reconnect and restart.");
        }
    };

    @Override public void onCreate(){
        super.onCreate();
        NotificationChannel channel=new NotificationChannel(CHANNEL,"LogRaft recording",NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("Continuous Raft diagnostics");
        getSystemService(NotificationManager.class).createNotificationChannel(channel);
    }

    private Notification notification(){
        Intent ui=new Intent(this,MainActivity.class);
        PendingIntent open=PendingIntent.getActivity(this,0,ui,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Intent stop=new Intent(this,CaptureService.class).setAction(STOP);
        PendingIntent stopPi=PendingIntent.getService(this,1,stop,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Intent mark=new Intent(this,CaptureService.class).setAction(MARK);
        PendingIntent markPi=PendingIntent.getService(this,2,mark,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this,CHANNEL)
                .setContentTitle("LogRaft • recording").setContentText("Raft log streaming into your chosen folder")
                .setSmallIcon(android.R.drawable.stat_notify_sync).setContentIntent(open)
                .addAction(android.R.drawable.ic_menu_edit,"Mark issue",markPi)
                .addAction(android.R.drawable.ic_menu_close_clear_cancel,"Stop",stopPi)
                .setOngoing(true).build();
    }

    @Override public int onStartCommand(Intent intent,int flags,int startId) {
        if(intent!=null && MARK.equals(intent.getAction())){
            appendMarker(); // bounded non-blocking FIFO offer
            return START_NOT_STICKY;
        }
        if(intent!=null && STOP.equals(intent.getAction())){
            // Serialize Stop after any pending startup, never join the writer
            // or invoke slow SAF calls on Android's event-dispatching thread.
            lifecycle.execute(()->{
                halt("Stopped by user");
                stopSelf();
            });
            return START_NOT_STICKY;
        }
        if(active || starting || stopping)return START_STICKY;
        boolean recovering=intent==null;
        if(recovering && !Config.prefs(this).getBoolean("recording",false)){
            stopSelfResult(startId);
            return START_NOT_STICKY;
        }
        try{
            // Foreground notification must be promoted promptly on the caller
            // thread; all document creation, shell probes, file opens and
            // Shizuku binding happen on the serial background control thread.
            startForeground(NOTIFICATION,notification());
            starting=true;
            startupRequestedElapsedMs=SystemClock.elapsedRealtime();
            startupReadyElapsedMs=-1;
            startupPhase="initializing";
            lifecycle.execute(()->initializeSession(recovering));
            return START_STICKY;
        }catch(Exception e){
            starting=false;
            fatal("Startup scheduling failed: "+e);
            return START_NOT_STICKY;
        }
    }

    private void initializeSession(boolean recovering) {
        try {
            Uri selected=Config.folder(this);
            if(selected==null) throw new IOException("Select a recording folder first");
            if(!Shizuku.pingBinder() ||
                    Shizuku.checkSelfPermission()!=PackageManager.PERMISSION_GRANTED)
                throw new SecurityException("Shizuku is not running or not permitted");
            folder=selected;
            session = new SimpleDateFormat("yyyyMMdd-HHmmss-SSS",Locale.US).format(new Date());
            Uri base=DocumentsContract.buildDocumentUriUsingTree(folder,DocumentsContract.getTreeDocumentId(folder));
            sessionFolder=DocumentsContract.createDocument(getContentResolver(),base,
                    DocumentsContract.Document.MIME_TYPE_DIR,"LogRaft-"+session);
            if(sessionFolder==null) throw new IOException("Folder creation failed");
            active=true; stopping=false; failed=false;
            totalBytes=0;metricsSegmentBytes=0;part=0;metricsPart=0;
            fileUris.clear();
            Config.prefs(this).edit().remove("metrics_last").remove("last_exit_history_sample")
                    .remove("exit_history_status").remove("writer_pending_bytes")
                    .remove("writer_max_lag_ms").remove("writer_failed_batches").apply();
            String metadata="LogRaft "+BuildConfig.VERSION_NAME+"\nTarget="+Config.PACKAGE+
                    "\nRecoveryRestart="+recovering+
                    "\nStart="+new Date()+"\nBuild="+Build.MANUFACTURER+" "+Build.MODEL+
                    "\nVersionCode="+BuildConfig.VERSION_CODE+
                    "\nAndroid="+Build.VERSION.RELEASE+" API="+Build.VERSION.SDK_INT+
                    "\nCollector=Shizuku shell/root UID; no root required\n"+
                    "Capture=Raft UID plus Raft-associated system/crash events\n"+
                    "Note=Logs only when emitted; cannot capture internal unlogged state\n"+
                    "Telemetry=3s sampling CPU process, process/system memory, KGSL GPU, thermal, battery, SurfaceFlinger displayed frames\n"+
                    "Missing metrics are null, not measured zeros. Game-internal FPS needs Unity logging.\n"+
                    "Warnings=Low available RAM, raw log flood, and suspected presented-frame stalls are heuristic indicators.\n";
            Uri meta=DocumentsContract.createDocument(getContentResolver(),sessionFolder,
                    "text/plain","session-info.txt");
            if(meta==null) throw new IOException("Metadata creation failed");
            try(OutputStream out=getContentResolver().openOutputStream(meta,"w")){
                if(out==null) throw new IOException("Cannot write metadata");
                out.write(metadata.getBytes(StandardCharsets.UTF_8));
            }
            fileUris.add(meta.toString());
            openSegment();
            openMetricSegment();
            startWriter();
            saveStatus("Preparing Shizuku logger...");
            args=new Shizuku.UserServiceArgs(
                    new ComponentName(getPackageName(),RemoteLogService.class.getName()))
                    .daemon(false).processNameSuffix("lograf").debuggable(false).version(1);
            if(!failed){
                startupPhase="shizuku_binding_requested";
                Shizuku.bindUserService(args,connection);
            }
        }catch(Exception e){
            startupPhase="failed";
            fatal("Startup failed: "+e);
        }finally{
            starting=false;
        }
    }

    private void openSegment() throws IOException {
        if(output!=null) { output.flush(); output.close(); }
        part++;
        String name=String.format(Locale.US,"raft-%s-%05d.log",session,part);
        Uri u=DocumentsContract.createDocument(getContentResolver(),sessionFolder,"text/plain",name);
        if(u==null) throw new IOException("Cannot create "+name);
        output=getContentResolver().openOutputStream(u,"w");
        if(output==null) throw new IOException("Output stream unavailable for "+u);
        fileUris.add(u.toString());
        segmentBytes=0;
        Config.prefs(this).edit().putString("files",new JSONArray(fileUris).toString())
                .putString("sessionFolder",sessionFolder.toString()).apply();
    }

    private void appendMarker() {
        // Do not write directly to SAF ahead of the reader FIFO. A marker
        // captures both wall and monotonic time so offline analysis can align
        // it with raw Logcat even when a remote batch arrives afterwards.
        // A single marker uses a non-blocking enqueue on the service thread.
        if(!active || stopping || failed)return;
        long unixMs=System.currentTimeMillis();
        long elapsedMs=SystemClock.elapsedRealtime();
        enqueue("MARKER",CaptureEventMarker.encode(unixMs,elapsedMs));
    }

    private void openMetricSegment() throws IOException {
        if(metricsOutput!=null){metricsOutput.flush();metricsOutput.close();}
        metricsPart++;
        String name=String.format(Locale.US,"metrics-%s-%05d.jsonl",session,metricsPart);
        Uri uri=DocumentsContract.createDocument(getContentResolver(),sessionFolder,"application/octet-stream",name);
        if(uri==null)throw new IOException("Cannot create telemetry segment: "+name);
        metricsOutput=getContentResolver().openOutputStream(uri,"w");
        if(metricsOutput==null)throw new IOException("Cannot open telemetry segment");
        fileUris.add(uri.toString()); metricsSegmentBytes=0;
        Config.prefs(this).edit().putString("files",new JSONArray(fileUris).toString()).apply();
    }

    private void saveStatus(String status){
        long now=System.currentTimeMillis();
        if(now-lastStatus<1300 && status.startsWith("Recording Raft")) return;
        lastStatus=now;
        Config.prefs(this).edit().putString("status",status)
                .putBoolean("recording",active)
                .putLong("bytes",totalBytes).apply();
    }

    private void fatal(String message) {
        if(failed) return;
        failed=true;
        saveStatus(message);
        if(!lifecycle.isShutdown()) lifecycle.execute(()->{
            halt(message);
            stopSelf();
        });
    }

    private void writeSessionSummary(String stopReason) {
        // Do not rescan gigabytes of raw logs. This small final summary only
        // contains counters from the last sample; raw segments remain untouched.
        if(sessionFolder==null) return;
        try {
            org.json.JSONObject report=new org.json.JSONObject();
            report.put("schema",1);
            report.put("session",session);
            report.put("target_package",Config.PACKAGE);
            report.put("end_unix_ms",System.currentTimeMillis());
            report.put("stop_reason",stopReason);
            report.put("total_recorded_bytes",totalBytes);
            report.put("raw_log_segments",part);
            report.put("metric_segments",metricsPart);
            report.put("raw_log_policy","preserve all segments; never delete");
            report.put("writer_received_batches",receivedBatches.get());
            report.put("writer_written_batches",writtenBatches.get());
            report.put("writer_failed_batches",failedBatches.get());
            report.put("user_markers_enqueued",markerEnqueued.get());
            report.put("user_markers_written",markerWritten.get());
            report.put("user_marker_delivery_note","Accepted markers share the FIFO with Logcat batches; remote batches can arrive after a marker with older event timestamps");
            report.put("writer_pending_bytes_at_stop",pendingBytes.get());
            report.put("writer_peak_pending_bytes",peakPendingBytes.get());
            report.put("writer_max_queue_delay_ms",maxQueueDelayMs.get());
            report.put("writer_failure",writerFailure.isEmpty()?org.json.JSONObject.NULL:writerFailure);
            report.put("session_startup_phase",startupPhase);
            report.put("session_remote_startup_duration_ms",
                    startupRequestedElapsedMs>=0 && startupReadyElapsedMs>=startupRequestedElapsedMs?
                        startupReadyElapsedMs-startupRequestedElapsedMs:org.json.JSONObject.NULL);
            report.put("startup_duration_scope",
                    "elapsed from app foreground-service request to Shizuku remote.start reply; null if unconfirmed");
            report.put("backpressure_notice","Logcat ring buffer losses cannot be detected perfectly; zero dropped local batches does not prove zero OS buffer loss");
            report.put("performance_statistics",sessionMetrics.toJson());
            report.put("game_process_exit_cause","unknown unless explicitly supported by exit evidence");
            if(!stopExitEvidence.isEmpty()){
                try {
                    org.json.JSONObject finalEvidence=new org.json.JSONObject(stopExitEvidence);
                    report.put("stop_time_android_process_exit_info",finalEvidence);
                    if(finalEvidence.has("final_error_groups"))
                        report.put("final_error_category_breakdown",
                                finalEvidence.getJSONObject("final_error_groups"));
                    if(finalEvidence.has("final_game_milestones"))
                        report.put("final_game_milestones",
                                finalEvidence.getJSONObject("final_game_milestones"));
                    if(finalEvidence.has("final_render_failure_breakdown"))
                        report.put("final_render_failure_breakdown",
                                finalEvidence.getJSONObject("final_render_failure_breakdown"));
                    if(finalEvidence.has("final_game_log_lines"))
                        report.put("final_game_log_lines",
                                finalEvidence.getLong("final_game_log_lines"));
                    report.put("final_totals_scope",
                            "remote reader observed lines; Android Logcat ring losses remain unknown");
                }catch(org.json.JSONException e){report.put("stop_time_exit_info_status","unreadable");}
            }
            String raw=Config.prefs(this).getString("metrics_last","");
            if(!raw.trim().isEmpty()) {
                try{report.put("last_sample",new org.json.JSONObject(raw.trim()));}
                catch(org.json.JSONException e){report.put("last_sample_error","invalid JSON");}
            }
            String exit=Config.prefs(this).getString("last_exit_history_sample","");
            if(!exit.trim().isEmpty()) {
                try{report.put("last_game_exit_evidence",new org.json.JSONObject(exit.trim()));}
                catch(org.json.JSONException e){report.put("exit_evidence_error","invalid JSON");}
            }
            Uri file=DocumentsContract.createDocument(getContentResolver(),sessionFolder,
                    "application/json","session-summary.json");
            if(file==null)return;
            try(OutputStream stream=getContentResolver().openOutputStream(file,"w")) {
                if(stream==null)return;
                stream.write(report.toString(2).getBytes(StandardCharsets.UTF_8));
                stream.flush();
            }
            fileUris.add(file.toString());
            Config.prefs(this).edit().putString("files",new JSONArray(fileUris).toString()).apply();
        }catch(Exception ignored){
            // An optional summary must never conceal the actual stop reason.
        }
    }

    private synchronized void halt(String status) {
        if(stopping)return;
        // Drain the remote reader's last batch BEFORE disabling our Binder sink.
        stopping=true;
        if(remote!=null) {
            try{remote.stop();}catch(Exception ignored){}
            // Exit info can appear after the final 3-second telemetry sample;
            // request it while still connected to the Shizuku shell process.
            try{stopExitEvidence=remote.finalExitEvidence();}
            catch(Exception error){stopExitEvidence="{\"status\":\"binder_unavailable\"}";}
            remote=null;
        }
        active=false;
        Thread thread=writerThread;
        if(thread!=null && thread!=Thread.currentThread()){
            // Allow enough time to flush the full bounded queue. Never discard
            // silently: if a slow provider prevents draining, record the gap.
            try{thread.join(18000);}catch(InterruptedException e){Thread.currentThread().interrupt();}
            if(thread.isAlive()){
                writerFailure="queue drain exceeded 18 seconds; output may be incomplete";
                failedBatches.incrementAndGet();
                status+=" • WRITER DRAIN INCOMPLETE";
            }
            writerThread=null;
        }
        if(args!=null) try { Shizuku.unbindUserService(args,connection,true); }
        catch(Exception ignored){}
        synchronized(writeLock) {
            if(output!=null) { try { output.flush(); output.close(); } catch(Exception ignored){} output=null; }
            if(metricsOutput!=null) { try { metricsOutput.flush(); metricsOutput.close(); } catch(Exception ignored){} metricsOutput=null; }
        }
        writeSessionSummary(status);
        Config.prefs(this).edit()
                .putLong("writer_pending_bytes",pendingBytes.get())
                .putLong("writer_max_lag_ms",maxQueueDelayMs.get())
                .putLong("writer_failed_batches",failedBatches.get()).apply();
        saveStatus(status+" • "+(totalBytes/1024)+" KiB saved");
        stopForeground(STOP_FOREGROUND_REMOVE);
    }

    @Override public void onDestroy() {
        // onDestroy is a main-thread callback; no 18-second writer join here.
        if(active || starting){
            if(!lifecycle.isShutdown())
                lifecycle.execute(()->halt("Recorder service stopped"));
        }
        lifecycle.shutdown(); // queued startup/stop tasks still finish in FIFO order
        super.onDestroy();
    }
    @Override public IBinder onBind(Intent intent){return null;}
}
