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
import org.json.JSONArray;
import rikka.shizuku.Shizuku;

public final class CaptureService extends Service {
    public static final String START="com.alwansan.clog.START";
    public static final String STOP="com.alwansan.clog.STOP";
    public static final String MARK="com.alwansan.clog.MARK";
    private static final String CHANNEL="record";
    private static final int NOTIFICATION=11;
    private static final long SEGMENT_BYTES=32L*1024*1024;
    private final Object writeLock = new Object();
    private OutputStream output, metricsOutput;
    private long metricsSegmentBytes;
    private int metricsPart;
    private static final long METRICS_SEGMENT_BYTES=8L*1024*1024;
    private Uri folder, sessionFolder;
    private final ArrayList<String> fileUris = new ArrayList<>();
    private long segmentBytes, totalBytes, lastStatus;
    private int part;
    private volatile boolean active;
    private volatile boolean failed, stopping;
    private IRemoteLog remote;
    private String session;
    private Shizuku.UserServiceArgs args;
    private final java.util.concurrent.atomic.AtomicBoolean workLogRunning=new java.util.concurrent.atomic.AtomicBoolean(false);
    private Thread workLogThread;

    private final ILogSink.Stub sink = new ILogSink.Stub() {
        @Override public void onBatch(String source, String content) {
            if (!active) return;
            synchronized(writeLock) {
                if (!active) return;
                try {
                    if ("METRICS".equals(source)) {
                        byte[] data=content.getBytes(StandardCharsets.UTF_8);
                        if(metricsOutput==null || metricsSegmentBytes+data.length>METRICS_SEGMENT_BYTES)openMetricSegment();
                        metricsOutput.write(data); metricsOutput.flush();
                        android.content.SharedPreferences.Editor editor=Config.prefs(CaptureService.this).edit()
                                .putString("metrics_last",content);
                        if(content.contains("\"exit_history_status\"")) {
                            editor.putString("last_exit_history_sample",content);
                            try {
                                editor.putString("exit_history_status",
                                        new org.json.JSONObject(content.trim()).optString("exit_history_status",""));
                            } catch(org.json.JSONException ignored){}
                        }
                        editor.apply();
                        metricsSegmentBytes+=data.length; totalBytes+=data.length;
                    } else {
                        byte[] bytes = ("[" + source + "]\n" + content).getBytes(StandardCharsets.UTF_8);
                        if (output==null || segmentBytes + bytes.length > SEGMENT_BYTES) openSegment();
                        output.write(bytes);
                        segmentBytes += bytes.length; totalBytes += bytes.length;
                        if (System.currentTimeMillis() - lastStatus > 1500) output.flush();
                    }
                    if (System.currentTimeMillis() - lastStatus > 1500) saveStatus("Recording Cinemana • " + (totalBytes/1024) + " KiB");
                } catch (Exception e) { fatal("Storage write failed: " + e); }
            }
        }
        @Override public void onFailure(String message) {
            synchronized (writeLock) {
                if (active) {
                    try {
                        byte[] bytes = ("[RECORDER WARNING] " + message + "\n").getBytes(StandardCharsets.UTF_8);
                        if (output != null) { output.write(bytes); output.flush(); }
                    } catch (Exception ignored) {}
                }
            }
            saveStatus("Warning: " + message);
        }
    };

    private final ServiceConnection connection=new ServiceConnection() {
        @Override public void onServiceConnected(ComponentName c, IBinder binder) {
            try {
                remote=IRemoteLog.Stub.asInterface(binder);
                ApplicationInfo info=getPackageManager().getApplicationInfo(Config.PACKAGE,0);
                remote.start(info.uid,Config.PACKAGE,sink);
                saveStatus("Recording: " + Config.PACKAGE + " (UID " + info.uid + ")");
            } catch (Exception e) { fatal("Cannot start privileged capture: " + e); }
        }
        @Override public void onServiceDisconnected(ComponentName c) {
            remote=null;
            if(active && !stopping) fatal("Shizuku disconnected; capture ended. Reconnect and restart.");
        }
    };

    @Override public void onCreate(){
        super.onCreate();
        NotificationChannel channel=new NotificationChannel(CHANNEL,"CLog recording",NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("Continuous Cinemana diagnostics");
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
                .setContentTitle("CLog • recording").setContentText("Cinemana log streaming into your chosen folder")
                .setSmallIcon(android.R.drawable.stat_notify_sync).setContentIntent(open)
                .addAction(android.R.drawable.ic_menu_edit,"Mark issue",markPi)
                .addAction(android.R.drawable.ic_menu_close_clear_cancel,"Stop",stopPi)
                .setOngoing(true).build();
    }

    @Override public int onStartCommand(Intent intent,int flags,int startId) {
        if(intent != null && MARK.equals(intent.getAction())) {
            appendMarker();
            return START_NOT_STICKY;
        }
        if(intent != null && STOP.equals(intent.getAction())) {
            halt("Stopped by user");
            stopSelf();
            return START_NOT_STICKY;
        }
        if (active) return START_STICKY;
        boolean recovering=intent==null;
        if(recovering && !Config.prefs(this).getBoolean("recording",false)){
            stopSelf();return START_NOT_STICKY;
        }
        try {
            startForeground(NOTIFICATION,notification());
            Uri selected=Config.folder(this);
            if(selected==null) throw new IOException("Select a recording folder first");
            if(!Shizuku.pingBinder() ||
                    Shizuku.checkSelfPermission()!=PackageManager.PERMISSION_GRANTED) {
                throw new SecurityException("Shizuku is not running or not permitted");
            }
            folder=selected;
            session = new SimpleDateFormat("yyyyMMdd-HHmmss-SSS",Locale.US).format(new Date());
            Uri base=DocumentsContract.buildDocumentUriUsingTree(folder,DocumentsContract.getTreeDocumentId(folder));
            sessionFolder=DocumentsContract.createDocument(getContentResolver(),base,
                    DocumentsContract.Document.MIME_TYPE_DIR,"CLog-"+session);
            if(sessionFolder==null) throw new IOException("Folder creation failed");
            active=true; stopping=false; failed=false; totalBytes=0; metricsSegmentBytes=0; part=0; metricsPart=0;
            fileUris.clear();
            Config.prefs(this).edit().remove("metrics_last").remove("last_exit_history_sample").remove("exit_history_status").apply();
            String metadata="CLog "+BuildConfig.VERSION_NAME+"\nTarget="+Config.PACKAGE+
                    "\nRecoveryRestart="+recovering+
                    "\nStart="+new Date()+"\nBuild="+Build.MANUFACTURER+" "+Build.MODEL+
                    "\nVersionCode="+BuildConfig.VERSION_CODE+
                    "\nAndroid="+Build.VERSION.RELEASE+" API="+Build.VERSION.SDK_INT+
                    "\nCollector=Shizuku shell/root UID; no root required\n"+
                    "Capture=Cinemana UID plus Cinemana-associated system/crash events\n"+
                    "Note=Logs only when emitted; cannot capture internal unlogged state\n"+
                    "Telemetry=3s sampling CPU process, process/system memory, KGSL GPU, thermal, battery, SurfaceFlinger displayed frames\n"+
                    "Missing metrics are null, not measured zeros. Game-internal FPS needs Unity logging.\n"+
                    "Warnings=Low available RAM, raw log flood, and suspected presented-frame stalls are heuristic indicators.\n";
            Uri meta=DocumentsContract.createDocument(getContentResolver(),sessionFolder,"text/plain","session-info.txt");
            if(meta==null) throw new IOException("Metadata creation failed");
            try(OutputStream out=getContentResolver().openOutputStream(meta,"w")){
                if(out==null) throw new IOException("Cannot write metadata");
                out.write(metadata.getBytes(StandardCharsets.UTF_8));
            }
            fileUris.add(meta.toString());
            openSegment();
            openMetricSegment();
            saveStatus("Preparing Shizuku logger...");
            Uri internal=Config.workLogsFolder(this);
            if(internal!=null){
                workLogRunning.set(true);
                workLogThread=new Thread(()->new CinemanaWorkLogCollector(
                        getContentResolver(),internal,sessionFolder,workLogRunning,
                        new CinemanaWorkLogCollector.Listener(){
                            @Override public void onNewFile(Uri file){
                                synchronized(writeLock){
                                    fileUris.add(file.toString());
                                    Config.prefs(CaptureService.this).edit()
                                            .putString("files",new JSONArray(fileUris).toString()).apply();
                                }
                            }
                            @Override public void onIssue(String issue){
                                try{sink.onFailure(issue);}
                                catch(android.os.RemoteException ignored){}
                            }
                        }).run(),"clog-saf-app-logs");
                workLogThread.setPriority(Thread.MIN_PRIORITY);
                workLogThread.start();
            }
            args=new Shizuku.UserServiceArgs(new ComponentName(getPackageName(),RemoteLogService.class.getName()))
                .daemon(false).processNameSuffix("lograf").debuggable(false).version(1);
            Shizuku.bindUserService(args,connection);
            return START_STICKY;
        } catch(Exception e) {
            fatal("Startup failed: " + e);
            stopSelf();
            return START_NOT_STICKY;
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
        synchronized(writeLock) {
            if(!active || output==null)return;
            try {
                String marker="[USER MARKER] "+new Date().toString()+" : User noticed an issue while playing Cinemana\n";
                byte[] data=marker.getBytes(StandardCharsets.UTF_8);
                if(segmentBytes+data.length>SEGMENT_BYTES)openSegment();
                output.write(data);output.flush();segmentBytes+=data.length;totalBytes+=data.length;
                saveStatus("Issue marker saved at "+new Date());
            }catch(Exception e){fatal("Cannot save marker: "+e);}
        }
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
        if(now-lastStatus<1300 && status.startsWith("Recording Cinemana")) return;
        lastStatus=now;
        Config.prefs(this).edit().putString("status",status)
                .putBoolean("recording",active)
                .putLong("bytes",totalBytes).apply();
    }

    private void fatal(String message) {
        if(failed) return;
        failed=true;
        saveStatus(message);
        new Handler(Looper.getMainLooper()).post(() -> {
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
            report.put("internal_work_log_capture_enabled",Config.workLogsFolder(this)!=null);
            report.put("internal_source_access","user-selected read-only SAF; source files never edited");
            report.put("game_process_exit_cause","unknown unless explicitly supported by exit evidence");
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

    private void halt(String status) {
        workLogRunning.set(false);
        if(workLogThread!=null)workLogThread.interrupt();
        // Drain the remote reader's last batch BEFORE disabling our Binder sink.
        stopping=true;
        if(remote!=null) {
            try { remote.stop(); } catch(Exception ignored){}
            remote=null;
        }
        if(workLogThread!=null && workLogThread!=Thread.currentThread()){
            try{workLogThread.join(1200);}
            catch(InterruptedException e){Thread.currentThread().interrupt();}
            workLogThread=null;
        }
        active=false;
        if(args!=null) try { Shizuku.unbindUserService(args,connection,true); }
        catch(Exception ignored){}
        synchronized(writeLock) {
            if(output!=null) { try { output.flush(); output.close(); } catch(Exception ignored){} output=null; }
            if(metricsOutput!=null) { try { metricsOutput.flush(); metricsOutput.close(); } catch(Exception ignored){} metricsOutput=null; }
        }
        writeSessionSummary(status);
        saveStatus(status+" • "+(totalBytes/1024)+" KiB saved");
        stopForeground(STOP_FOREGROUND_REMOVE);
    }

    @Override public void onDestroy() {
        if(active) halt("Recorder service stopped");
        super.onDestroy();
    }
    @Override public IBinder onBind(Intent intent){return null;}
}
