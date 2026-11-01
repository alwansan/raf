package com.alwansan.lograf;

import android.Manifest;
import android.app.Activity;
import android.content.*;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.*;
import android.provider.DocumentsContract;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Locale;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import org.json.JSONArray;
import org.json.JSONObject;
import rikka.shizuku.Shizuku;

public final class MainActivity extends Activity {
    private static final int PICK_FOLDER=201;
    private static final int SHIZUKU_REQUEST=202;
    private boolean pendingStart=false;
    private TextView status, folderLabel, performanceLabel;
    private Button start, stop, share;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final Runnable refresh=new Runnable(){
        @Override public void run(){ update(); handler.postDelayed(this,1100); }
    };
    private final Shizuku.OnRequestPermissionResultListener permissionListener=(code, result)->{
        if(code==SHIZUKU_REQUEST) runOnUiThread(()-> {
            if(result==PackageManager.PERMISSION_GRANTED) { if(pendingStart) startCapture(); else message("Shizuku permitted ✓"); }
            else message("Shizuku permission denied");
            pendingStart=false;
        });
    };

    private TextView title(String text,int sp){
        TextView v=new TextView(this);
        v.setText(text); v.setTextSize(sp); v.setPadding(0,12,0,12);
        return v;
    }
    private Button button(String label){
        Button b=new Button(this); b.setAllCaps(false); b.setText(label);
        b.setMinHeight(56); return b;
    }

    @Override protected void onCreate(Bundle state){
        super.onCreate(state);
        getWindow().setStatusBarColor(0xff10212d);
        getWindow().setNavigationBarColor(0xff10212d);
        ScrollView scroll=new ScrollView(this);
        LinearLayout layout=new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int dp=(int)(18*getResources().getDisplayMetrics().density);
        layout.setPadding(dp,dp,dp,dp);
        scroll.addView(layout);

        TextView head=title("LogRaft  •  مسجل تشخيص لعبة Raft",23);
        head.setTextColor(0xff163c52);
        layout.addView(head);
        layout.addView(title("مخصص للعبة com.alwansan.raft.androidtest. يلتقط Unity / Java / IL2CPP / FMOD / GPU عند ظهورها في Logcat، مع أحداث النظام المرتبطة باللعبة.",15));
        folderLabel=title("",14); layout.addView(folderLabel);

        Button folder=button("1  •  اختر مجلد حفظ اللوقات");
        folder.setOnClickListener(v-> {
            Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|
                     Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
            startActivityForResult(i,PICK_FOLDER);
        });
        layout.addView(folder);

        Button permission=button("2  •  تخويل Shizuku");
        permission.setOnClickListener(v->requestShizuku(false));
        layout.addView(permission);

        start=button("3  •  ابدأ التسجيل قبل فتح Raft");
        start.setOnClickListener(v->requestShizuku(true));
        layout.addView(start);

        Button launch=button("افتح لعبة Raft");
        launch.setOnClickListener(v->{
            Intent i=getPackageManager().getLaunchIntentForPackage(Config.PACKAGE);
            if(i==null) message("Raft ليست مثبتة بالحزمة المحددة");
            else startActivity(i);
        });
        layout.addView(launch);

        Button marker=button("علّم لحظة حدوث مشكلة (Marker)");
        marker.setOnClickListener(v->{
            startService(new Intent(this,CaptureService.class).setAction(CaptureService.MARK));
            message("Issue marker requested");
        });
        layout.addView(marker);

        stop=button("إيقاف التسجيل وحفظ الملفات");
        stop.setOnClickListener(v-> {
            startService(new Intent(this,CaptureService.class).setAction(CaptureService.STOP));
            message("Stopping recording; saving log files");
        });
        layout.addView(stop);

        share=button("إنشاء ZIP ومشاركته من آخر جلسة");
        share.setOnClickListener(v-> exportZip());
        layout.addView(share);

        status=title("جاهز",15);
        status.setTextIsSelectable(true); layout.addView(status);
        performanceLabel=title("القياسات: بانتظار بدء التسجيل",15);
        performanceLabel.setTextIsSelectable(true); layout.addView(performanceLabel);
        layout.addView(title("تنبيه: التسجيل مستمر أثناء تشغيل Raft حتى تتوقف الخدمة أو يوقفها أندرويد. لا يمكن ضمان سجلات لم تُصدرها اللعبة أو اختفت قبل بدء التسجيل. قد تحتوي الملفات على معلومات حساسة؛ راجعها قبل النشر.",13));
        setContentView(scroll);

        try { Shizuku.addRequestPermissionResultListener(permissionListener); }
        catch(Throwable t){ message("Shizuku API error: "+t.getMessage()); }
        if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},301);
        handler.post(refresh);
    }

    private void requestShizuku(boolean thenStart){
        try {
            if(!Shizuku.pingBinder()) { message("شغّل Shizuku أولاً من تطبيق Shizuku"); return; }
            if(Shizuku.isPreV11()) { message("Shizuku API 11+ required"); return; }
            if(Shizuku.checkSelfPermission()==PackageManager.PERMISSION_GRANTED){
                if(thenStart) startCapture(); else message("Shizuku permitted ✓");
                return;
            }
            if(Shizuku.shouldShowRequestPermissionRationale()){
                message("شغّل صلاحية LogRaft داخل إعدادات Shizuku");
                return;
            }
            // Only auto-start after the permission request if the user pressed Start.
            pendingStart=thenStart;
            Shizuku.requestPermission(SHIZUKU_REQUEST);
        }catch(Throwable e){message("Shizuku: "+e);}
    }
    private void startCapture(){
        if(Config.folder(this)==null){message("اختر المجلد أولاً");return;}
        try {
            Intent i=new Intent(this,CaptureService.class).setAction(CaptureService.START);
            startForegroundService(i);
            message("Starting recorder...");
        } catch(Exception e){message("Start failed: "+e);}
    }

    private void update(){
        if(status==null) return;
        Uri u=Config.folder(this);
        folderLabel.setText("مجلد الحفظ: "+(u==null ? "لم يتم التحديد" : u.toString()));
        String text=Config.prefs(this).getString("status","جاهز");
        boolean recording=Config.prefs(this).getBoolean("recording",false);
        status.setText("الحالة: "+text+"\nالمشروع: Raft\nالتسجيل: "+(recording?"نشط":"متوقف")+
                "\nالحجم المسجل: "+(Config.prefs(this).getLong("bytes",0)/1024)+" KiB");
        start.setEnabled(!recording); stop.setEnabled(recording);
        String raw=Config.prefs(this).getString("metrics_last","");
        if(!raw.isEmpty()) try {
            JSONObject m=new JSONObject(raw.trim());
            performanceLabel.setText("قراءات Raft المباشرة (تتحدث كل 3 ثوانٍ):"+
                "\\nCPU process: "+metric(m,"process_cpu_percent_one_core","% of one core")+
                "\\nRAM RSS: "+metric(m,"process_rss_kb","KiB")+
                "\\nRAM PSS: "+metric(m,"process_pss_kb","KiB")+
                "\\nAvailable RAM: "+metric(m,"device_mem_available_kb","KiB")+
                "\\nGPU busy (device-wide): "+metric(m,"gpu_busy_percent","%")+
                "\\nCPU frequencies: "+frequencySummary(m)+
                "\\nFree storage: "+storageSummary(m)+
                "\\nGPU clock: "+metric(m,"gpu_clock_hz","Hz")+
                "\\nDisplayed FPS estimate: "+metric(m,"presented_fps_estimate","fps")+
                "\\nBattery: "+metric(m,"battery_level_percent","%")+
                "\\nBattery temp: "+metric(m,"battery_temp_c","°C")+
                "\\nThermal status code: "+metric(m,"thermal_status_code","")+
                "\\nLogcat game lines: "+metric(m,"game_log_lines","")+
                "\\nSystem event lines: "+metric(m,"system_context_lines","")+
                "\\nStream reconnects (potential gaps): "+metric(m,"logcat_reconnects","")+
                "\\nGame state: "+m.optString("state","unknown"));
        } catch(Exception ignored){performanceLabel.setText("Metrics awaiting valid sample");}
    }

    private String frequencySummary(JSONObject obj) {
        JSONArray a=obj.optJSONArray("cpu_frequency_khz_by_core");
        if(a==null || a.length()==0)return "غير متاح";
        StringBuilder b=new StringBuilder();
        for(int i=0;i<Math.min(a.length(),16);i++){
            if(i>0)b.append(", ");
            Object f=a.opt(i);
            b.append("C").append(i).append("=");
            if(f instanceof Number)b.append(((Number)f).longValue()/1000).append("MHz");
            else b.append("?");
        }
        return b.toString();
    }

    private String storageSummary(JSONObject m){
        Object value=m.opt("device_storage_free_bytes");
        if(!(value instanceof Number))return "غير متاح";
        long free=((Number)value).longValue();
        return (free/1048576)+" MiB"+(free<536870912L?" — مساحة منخفضة!":"");
    }

    private String metric(JSONObject obj,String key,String unit) {
        Object value=obj.opt(key);
        return value==null || value==JSONObject.NULL?"غير متاح":value+" "+unit;
    }

    private void message(String text) { Toast.makeText(this,text,Toast.LENGTH_LONG).show(); }

    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if(request==PICK_FOLDER && result==RESULT_OK && data!=null && data.getData()!=null){
            Uri u=data.getData();
            try {
                getContentResolver().takePersistableUriPermission(u,Intent.FLAG_GRANT_READ_URI_PERMISSION|
                        Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                Config.prefs(this).edit().putString("folder",u.toString()).apply();
                update();
            } catch(Exception e){message("Folder permission failed: "+e);}
        }
    }

    private void exportZip(){
        if(Config.prefs(this).getBoolean("recording",false)){
            message("أوقف التسجيل قبل المشاركة حتى تكتمل الملفات");return;
        }
        String raw=Config.prefs(this).getString("files","[]");
        String dir=Config.prefs(this).getString("sessionFolder","");
        if(dir.isEmpty()){message("لا توجد جلسة محفوظة");return;}
        share.setEnabled(false);
        message("Creating ZIP in selected folder...");
        new Thread(()->{
            try {
                JSONArray files=new JSONArray(raw);
                if(files.length()==0)throw new IOException("Empty session");
                Uri parent=Uri.parse(dir);
                String zipName="LogRaft-"+System.currentTimeMillis()+".zip";
                Uri outputUri=DocumentsContract.createDocument(getContentResolver(),parent,"application/zip",zipName);
                if(outputUri==null)throw new IOException("ZIP creation failed");
                try (OutputStream stream=getContentResolver().openOutputStream(outputUri,"w");
                     ZipOutputStream zip=new ZipOutputStream(stream)) {
                    if(stream==null)throw new IOException("ZIP cannot be opened");
                    byte[] buffer=new byte[65536];
                    for(int i=0;i<files.length();i++){
                        Uri file=Uri.parse(files.getString(i));
                        String name=DocumentsContract.getDocumentId(file);
                        name=name.substring(name.lastIndexOf('/')+1).replace('\\','_');
                        zip.putNextEntry(new ZipEntry(String.format(Locale.US,"%04d-",i)+name));
                        try(InputStream input=getContentResolver().openInputStream(file)){
                            if(input==null) throw new IOException("Cannot read "+file);
                            int read;
                            while((read=input.read(buffer))!=-1)zip.write(buffer,0,read);
                        }
                        zip.closeEntry();
                    }
                }
                runOnUiThread(()-> {
                    Intent shareIntent=new Intent(Intent.ACTION_SEND);
                    shareIntent.setType("application/zip");
                    shareIntent.putExtra(Intent.EXTRA_STREAM,outputUri);
                    shareIntent.setClipData(ClipData.newRawUri("LogRaft",outputUri));
                    shareIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    startActivity(Intent.createChooser(shareIntent,"Share Raft logs"));
                    share.setEnabled(true);
                });
            }catch(Exception e){runOnUiThread(()->{
                share.setEnabled(true); message("ZIP error: "+e.getMessage());
            });}
        },"lograf-zip").start();
    }

    @Override protected void onDestroy(){
        handler.removeCallbacks(refresh);
        Shizuku.removeRequestPermissionResultListener(permissionListener);
        super.onDestroy();
    }
}
