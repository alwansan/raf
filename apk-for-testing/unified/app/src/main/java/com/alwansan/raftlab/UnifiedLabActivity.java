package com.alwansan.raftlab;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.os.*;
import android.provider.MediaStore;
import android.view.View;
import android.widget.*;
import android.content.pm.PackageInfo;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.text.SimpleDateFormat;
import java.util.*;

/**
 * One shared APK, five workers, embedded/importable DATA ONLY testpack.
 * Auto-run only when a real compiled-in driver returns an observation.
 * A mouse click, another app's screenshot, or visual correctness cannot be simulated.
 */
public final class UnifiedLabActivity extends Activity {
    private static final int LOAD_PACK=401, PICK_SCREENSHOT=402, PICK_FILE=403, AUTO_CASE=404, MANUAL_CASE=405;
    private static final int MAX_PACK=262144;
    private final ArrayList<JSONObject> tests=new ArrayList<>();
    private final ArrayList<JSONObject> pending=new ArrayList<>();
    private final ArrayList<JSONObject> schedule=new ArrayList<>();
    private final Handler handler=new Handler(Looper.getMainLooper());
    private SharedPreferences state;
    private LinearLayout content,workerButtons,pendingButtons;
    private TextView title,summary,caseDetail;
    private EditText comment;
    private JSONObject currentManual, activeAuto;
    private int at=0;
    private boolean running=false,waitingForChild=false,forceRerun=false;
    private boolean fileDigestBusy=false;
    private Thread fileDigestThread;
    private String session,packId="unloaded",packSha="unknown";
    private File privateLog;
    private Uri logExport,summaryExport;
    private String screenshotCase;
    private final ArrayList<String> recent=new ArrayList<>();

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        session=new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.US).format(new Date())+"-"+SystemClock.elapsedRealtime();
        File dir=new File(getFilesDir(),"shared-team-sessions");
        if(!dir.exists()&&!dir.mkdirs())throw new IllegalStateException("Private log path unavailable");
        privateLog=new File(dir,"events-"+session+".jsonl");
        state=getSharedPreferences("verified-results-v2",MODE_PRIVATE);
        makeUi();
        try(InputStream in=getAssets().open("team-testpack.json")){loadPack(readLimited(in));}
        catch(Exception e){log("manifest_load_error",e.toString());show("Cannot load embedded pack: "+e.getMessage());}
        log("start","package="+getPackageName()+" version="+BuildConfig.VERSION_NAME+" code="+BuildConfig.VERSION_CODE+
            " source="+BuildConfig.SOURCE_SHA+" Android="+Build.VERSION.SDK_INT+" model="+Build.MODEL);
        drawHome();
    }

    void makeUi(){
        getWindow().getDecorView().setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        ScrollView scroll=new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        content=new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        content.setPadding(18,16,18,30);
        scroll.addView(content);
        title=text("مختبر رافت الموحد — T1 إلى T5");
        title.setTextSize(21);
        content.addView(title);
        summary=text("الاختبارات محفوظة داخل التطبيق؛ لا تحتاج استيراد ملف قديم.");
        content.addView(summary);
        content.addView(text("١) اضغط «تشغيل الاختبارات التلقائية» للفحوص الممكنة. ٢) اختر اختبارًا يدويًا من «طلبات تحتاج تدخلك». ٣) اكتب ما شاهدته ثم احفظ النتيجة. ٤) صدّر الملفات وارفعها إلى GitHub: alwansan/CL → test."));
        content.addView(text("الأزرار التالية خاصة بمختبر الاختبار فقط، ولا تتحكم تلقائيًا بلعبة Raft الخارجية."));
        LinearLayout controls=new LinearLayout(this);
        controls.setOrientation(LinearLayout.VERTICAL);
        content.addView(controls);
        addButton(controls,"▶ تشغيل الاختبارات التلقائية لكل الفريق",v->autoRun(null));
        addButton(controls,"↻ إعادة الاختبارات التلقائية بالقوة",v->autoRun(null,true));
        addButton(controls,"استيراد حزمة الاختبارات (اختياري)",v->pick(LOAD_PACK,"application/json"));
        addButton(controls,"📤 تصدير السجلات والنتائج",v->export());
        content.addView(text("اختبارات الفرق — اضغط اسم الفريق لعرض الحالات أو «تشغيل» للفحص الآلي:"));
        workerButtons=new LinearLayout(this);
        workerButtons.setOrientation(LinearLayout.VERTICAL);
        workerButtons.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        content.addView(workerButtons);
        content.addView(text("طلبات تحتاج تدخلك — اضغط اسم الاختبار أدناه لفتح تعليماته:"));
        pendingButtons=new LinearLayout(this);
        pendingButtons.setOrientation(LinearLayout.VERTICAL);
        pendingButtons.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        content.addView(pendingButtons);
        content.addView(text("الاختبار المحدد وتعليماته:"));
        caseDetail=text("اختر اختبارًا من قائمة الطلبات بالأعلى لعرض الخطوات بالعربية.");
        content.addView(caseDetail);
        comment=new EditText(this);
        comment.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        comment.setHint("اكتب ما شاهدته فعلًا، أو الخطأ الذي ظهر، أو وصف الصورة");
        comment.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);
        comment.setMinLines(2);
        content.addView(comment);
        LinearLayout actions=new LinearLayout(this);
        actions.setOrientation(LinearLayout.VERTICAL);
        content.addView(actions);
        addButton(actions,"▶ تنفيذ الاختبار الذي اخترته",v->launchManualCase());
        addButton(actions,"✔ نجاح حسب مشاهدتي (بعد كتابة ملاحظة)",v->manualResult("USER_PASS"));
        addButton(actions,"✖ فشل حسب مشاهدتي (بعد كتابة ملاحظة)",v->manualResult("USER_FAIL"));
        addButton(actions,"إرفاق صورة دليل من الهاتف",v->{
            if(currentManual==null){show("اختر اختبارًا من قائمة الطلبات أولًا");return;}
            screenshotCase=currentManual.optString("id");pick(PICK_SCREENSHOT,"image/*");
        });
        LinearLayout nav=new LinearLayout(this);
        nav.setOrientation(LinearLayout.VERTICAL);
        content.addView(nav);
        addButton(nav,"الانتقال إلى الاختبار التالي",v->nextPending());
        addButton(nav,"الإنهاء والعودة إلى قائمة الاختبارات",v->{currentManual=null;drawHome();});
        content.addView(text("مكان رفع نتائج الاختبار بعد التصدير: github.com/alwansan/CL/tree/main/test"));
        setContentView(scroll);
    }
    TextView text(String s){
        TextView t=new TextView(this);
        t.setTextSize(16);
        t.setTextDirection(View.TEXT_DIRECTION_FIRST_STRONG);
        t.setGravity(android.view.Gravity.RIGHT);
        t.setPadding(8,12,8,12);
        t.setText(s);
        return t;
    }
    void addButton(LinearLayout bar,String label,View.OnClickListener f){
        Button btn=new Button(this);
        btn.setAllCaps(false);
        btn.setTextSize(14);
        btn.setText(label);
        LinearLayout.LayoutParams params=bar.getOrientation()==LinearLayout.VERTICAL
            ?new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT)
            :new LinearLayout.LayoutParams(0,LinearLayout.LayoutParams.WRAP_CONTENT,1f);
        params.setMargins(1,2,1,2);
        bar.addView(btn,params);
        btn.setOnClickListener(f);
    }
    void show(String m){summary.setText(m);}
    byte[] readLimited(InputStream stream)throws IOException{
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] block=new byte[8192];int n,emptyReads=0;
        while((n=stream.read(block))!=-1){
            if(n==0){
                if(++emptyReads>=16)throw new IOException("Pack provider returned repeated empty reads");
                continue;
            }
            emptyReads=0;
            if(bytes.size()+n>MAX_PACK)throw new IOException("Pack over 256KiB");
            bytes.write(block,0,n);
        }
        return bytes.toByteArray();
    }
    static String digest(byte[] a){
        try{byte[] raw=MessageDigest.getInstance("SHA-256").digest(a);StringBuilder s=new StringBuilder();
            for(byte x:raw)s.append(String.format(Locale.US,"%02x",x&255));return s.toString();
        }catch(Exception e){throw new IllegalStateException(e);}
    }
    boolean isSafeCase(JSONObject t)throws JSONException{
        String id=t.getString("id"),who=t.getString("worker"),driver=t.getString("driver");
        if(!id.matches("T[1-5]-[0-9]{2,3}")||!id.startsWith(who+"-"))return false;
        int rev=t.getInt("revision");if(rev<1||rev>100000)return false;
        String mode=t.getString("mode"),screen=t.getString("screenshot");
        if(!Arrays.asList("auto","assisted","manual").contains(mode)||
           !Arrays.asList("none","auto","manual","optional").contains(screen))return false;
        if(!t.has("title")||!t.has("instructions")||!t.has("expected"))return false;
        for(String k:new String[]{"title","instructions","expected"})
            if(t.getString(k).isEmpty()||t.getString(k).length()>1200)return false;
        if(driver.equals("t1_compute"))return id.matches("T1-0[1-4]")&&mode.equals("auto");
        if(driver.equals("t2_gles"))return id.matches("T2-0[1-4]")&&mode.equals("auto");
        if(driver.equals("t3_visual"))return id.matches("T3-0[1-6]")&&mode.equals("assisted");
        if(driver.equals("system_identity"))return who.equals("T5")&&mode.equals("auto");
        if(driver.equals("mouse_manual"))return who.equals("T4")&&mode.equals("manual");
        if(driver.equals("file_sha256"))return mode.equals("manual");
        return driver.equals("note_manual")&&mode.equals("manual");
    }
    void loadPack(byte[] bytes)throws Exception{
        JSONObject pack=new JSONObject(new String(bytes,StandardCharsets.UTF_8));
        if(pack.getInt("schema_version")!=2)throw new IOException("Requires schema v2");
        String id=pack.getString("pack_id");
        if(!id.matches("[a-z0-9][a-z0-9._-]{0,79}"))throw new IOException("Unsafe pack ID");
        JSONArray list=pack.getJSONArray("tests");
        if(list.length()<1||list.length()>100)throw new IOException("Requires 1..100 cases");
        HashSet<String> used=new HashSet<>();ArrayList<JSONObject> fresh=new ArrayList<>();
        for(int i=0;i<list.length();i++){
            JSONObject t=list.getJSONObject(i);
            if(!isSafeCase(t)||!used.add(t.getString("id")))throw new IOException("Unsafe or duplicate case at index "+i);
            fresh.add(t);
        }
        tests.clear();tests.addAll(fresh);packId=id;packSha=digest(bytes);
        log("team_pack_loaded","id="+id+" sha256="+packSha+" cases="+tests.size());
        refreshPending();
    }
    String fingerprint(JSONObject t){
        String driver=t.optString("driver"),worker=t.optString("worker");
        String driverSha="unknown";
        if(worker.equals("T1"))driverSha=BuildConfig.T1_DRIVER_SHA;
        if(worker.equals("T2"))driverSha=BuildConfig.T2_DRIVER_SHA;
        if(worker.equals("T3"))driverSha=BuildConfig.T3_DRIVER_SHA;
        if(worker.equals("T4"))driverSha=BuildConfig.T4_DRIVER_SHA;
        if(worker.equals("T5"))driverSha=BuildConfig.T5_DRIVER_SHA;
        // A package version bump or another worker's unrelated change does NOT
        // invalidate existing case evidence; changing this worker's source DOES.
        String input=t.toString()+"|driver-sha="+driverSha+
          "|device="+android.os.Build.FINGERPRINT+"|type="+driver;
        return digest(input.getBytes(StandardCharsets.UTF_8));
    }
    JSONObject saved(JSONObject c){
        try{return new JSONObject(state.getString("test_"+c.optString("id"),"{}"));}
        catch(Exception e){return new JSONObject();}
    }
    boolean screenshotValid(String uri){
        if(uri==null||uri.isEmpty())return false;
        try(InputStream in=getContentResolver().openInputStream(Uri.parse(uri))){return in!=null&&in.read()!=-1;}
        catch(Exception e){return false;}
    }
    boolean screenshotRequired(JSONObject c){return Arrays.asList("auto","manual").contains(c.optString("screenshot"));}
    boolean reusable(JSONObject c){
        JSONObject old=saved(c);
        return UnifiedResultPolicy.reusable(old.optString("status"),
            fingerprint(c).equals(old.optString("fingerprint")),
            screenshotRequired(c),screenshotValid(old.optString("image_uri")));
    }
    boolean screenRequiredValid(JSONObject c,String uri){
        return !screenshotRequired(c)||screenshotValid(uri);
    }
    void store(JSONObject c,String status,String observed,String imageUri){
        try{
            JSONObject record=new JSONObject();
            record.put("id",c.getString("id"));record.put("worker",c.getString("worker"));
            record.put("status",status);record.put("fingerprint",fingerprint(c));
            record.put("observed",observed);record.put("image_uri",imageUri==null?"":imageUri);
            record.put("utc_ms",System.currentTimeMillis());record.put("pack_sha256",packSha);
            state.edit().putString("test_"+c.getString("id"),record.toString()).apply();
            log("case_result",record.toString());refreshPending();
        }catch(Exception e){log("store_error",e.toString());}
    }
    void refreshPending(){
        pending.clear();
        for(JSONObject c:tests){
            String status=saved(c).optString("status");
            if(UnifiedResultPolicy.pending(c.optString("mode"),status,reusable(c)))
                pending.add(c);
        }
    }
    void drawHome(){
        refreshPending();workerButtons.removeAllViews();pendingButtons.removeAllViews();
        show("الحزمة: "+packId+" — عدد الاختبارات "+tests.size()+" — تحتاج تدخلك: "+pending.size()+"؛ النتائج السابقة تُحفظ ولا تُعدّ نجاحًا بلا دليل.");
        for(int i=1;i<=5;i++){
            String worker="T"+i;int n=0,done=0;
            for(JSONObject c:tests)if(worker.equals(c.optString("worker"))){
                n++;if(UnifiedResultPolicy.passed(saved(c).optString("status"),reusable(c)))done++;
            }
            final String w=worker;
            LinearLayout row=new LinearLayout(this);workerButtons.addView(row);
            addButton(row,"فريق "+w+" ("+done+"/"+n+" ناجح)",v->showWorker(w));
            addButton(row,"تشغيل "+w+" تلقائيًا",v->autoRun(w));
        }
        for(JSONObject c:pending){
            String id=c.optString("id");String label=id+" — "+ArabicLabStrings.title(id,c.optString("title"))+" ["+ArabicLabStrings.status(saved(c).optString("status"))+"]";
            addButton(pendingButtons,label,v->openPending(c));
        }
        if(pending.isEmpty())pendingButtons.addView(text("لا توجد طلبات معلّقة حاليًا؛ الفحوص الآلية قد تنتهي دون الحاجة لتدخل."));
    }
    void showWorker(String worker){
        StringBuilder s=new StringBuilder("الفريق "+worker+" — الاختبارات:\n");
        for(JSONObject c:tests)if(worker.equals(c.optString("worker"))){
            s.append(c.optString("id")).append(": ").append(ArabicLabStrings.title(c.optString("id"),c.optString("title")))
             .append(" / ").append(ArabicLabStrings.status(saved(c).optString("status"))).append('\n');
        }
        caseDetail.setText(s.toString());
    }
    void autoRun(String worker){autoRun(worker,false);}
    void autoRun(String worker,boolean force){
        if(running||waitingForChild){show("يوجد اختبار تلقائي يعمل بالفعل؛ لا تبدأ تنفيذًا ثانيًا الآن");return;}
        schedule.clear();
        for(JSONObject c:tests)if(worker==null||worker.equals(c.optString("worker")))schedule.add(c);
        at=0;running=true;forceRerun=force;
        log("auto_start","worker="+(worker==null?"ALL":worker)+" total="+schedule.size()+" force="+force);
        runNext();
    }
    void runNext(){
        if(!running)return;
        if(at>=schedule.size()){running=false;forceRerun=false;activeAuto=null;log("auto_complete","count="+schedule.size());export();drawHome();return;}
        JSONObject c=schedule.get(at++);
        // Forced GPU/visual reruns must not erase already reviewed manual/file evidence.
        if(reusable(c)&&(!forceRerun||"manual".equals(c.optString("mode")))){
            log("auto_reuse",c.optString("id")+" status="+saved(c).optString("status")+" "+fingerprint(c));
            runNext();return;
        }
        String id=c.optString("id"),driver=c.optString("driver");
        activeAuto=c;
        show("جارٍ الفحص التلقائي "+at+"/"+schedule.size()+" — "+id+" "+ArabicLabStrings.title(id,c.optString("title")));
        log("auto_case_start",id+" driver="+driver);
        if(c.optString("mode").equals("manual")){
            store(c,"NEEDS_INPUT","User action, mouse/file or judgment is required",null);runNext();return;
        }
        if(driver.equals("system_identity")){
            String signer=signerSha256();
            String observed="package="+getPackageName()+" version="+BuildConfig.VERSION_NAME+
                " versionCode="+BuildConfig.VERSION_CODE+" signingCertSha256="+signer+
                " api="+Build.VERSION.SDK_INT+" abi="+Build.SUPPORTED_ABIS[0];
            boolean valid="com.alwansan.raft.lab.shared".equals(getPackageName())&&signer.matches("[a-f0-9]{64}");
            store(c,valid?"PASS":"FAIL",observed,null);runNext();return;
        }
        Intent i;
        if(driver.equals("t1_compute")){i=new Intent(this,MainActivity.class);i.putExtra("mini_worker","T1");}
        else if(driver.equals("t2_gles"))i=new Intent(this,T2GpuActivity.class);
        else if(driver.equals("t3_visual"))i=new Intent().setClassName(this,"com.alwansan.raft.t3lab.T3LabActivity");
        else{store(c,"BLOCKED","No compiled-in safe driver",null);runNext();return;}
        i.putExtra("auto_case_id",id);i.putExtra("shared_session",session);
        waitingForChild=true;
        startActivityForResult(i,AUTO_CASE);
        final String expected=id;
        handler.postDelayed(()->{
            if(waitingForChild&&activeAuto!=null&&expected.equals(activeAuto.optString("id")))
                show("Driver "+expected+" still running; press Back if stuck. Never mark PASS on timeout.");
        },18000);
    }
    @Override protected void onActivityResult(int req,int result,Intent data){
        super.onActivityResult(req,result,data);
        if(req==AUTO_CASE){
            if(!waitingForChild)return;
            waitingForChild=false;
            if(activeAuto==null){runNext();return;}
            String expected=activeAuto.optString("id");
            String actual=data==null?"":data.getStringExtra("case_id");
            String status=data==null?"BLOCKED":data.getStringExtra("status");
            String observed=data==null?"Activity cancelled":data.getStringExtra("observed");
            String uri=data==null?null:data.getStringExtra("screenshot_uri");
            if(result!=RESULT_OK||!expected.equals(actual)){
                store(activeAuto,"BLOCKED","Mismatched/cancelled child activity; no proof of execution",null);
            }else{
                if(!Arrays.asList("PASS","FAIL","EVIDENCE_READY","NEEDS_SCREENSHOT").contains(status))
                    status="BLOCKED";
                if(status.equals("EVIDENCE_READY")&&!screenshotValid(uri))status="NEEDS_SCREENSHOT";
                store(activeAuto,status,observed==null?"No observation":observed,uri);
            }
            activeAuto=null;runNext();return;
        }
        if(req==MANUAL_CASE){
            if(currentManual!=null&&data!=null&&currentManual.optString("id").equals(data.getStringExtra("case_id"))){
                String observed=data.getStringExtra("observed");
                String st=data.getStringExtra("status");
                if(!"EVIDENCE_READY".equals(st))st="NEEDS_INPUT";
                store(currentManual,st,observed==null?"No event":observed,null);
                show("Input evidence captured. Review the result and mark PASS/FAIL if appropriate.");
            }
            return;
        }
        if(result!=RESULT_OK||data==null||data.getData()==null)return;
        Uri uri=data.getData();
        try{
            if(req==LOAD_PACK){try(InputStream in=getContentResolver().openInputStream(uri)){
                if(in==null)throw new IOException("Unreadable pack");
                loadPack(readLimited(in));drawHome();}}
            else if(req==PICK_SCREENSHOT)attachScreenshot(uri);
            else if(req==PICK_FILE)hashFile(uri);
        }catch(Exception e){log("picker_error",e.toString());show("خطأ قراءة الملف: "+e.getMessage());}
    }
    void openPending(JSONObject c){
        currentManual=c;comment.setText("");
        String pic=screenshotRequired(c)?"صورة الدليل مطلوبة":"الصورة اختيارية";
        String id=c.optString("id");
        caseDetail.setText(id+" — "+ArabicLabStrings.title(id,c.optString("title"))+
            "\nالخطوات: "+ArabicLabStrings.instructions(id,c.optString("instructions"))+
            "\nالمتوقع: "+ArabicLabStrings.expected(id,c.optString("expected"))+
            "\n"+pic+"\nالحالة السابقة: "+ArabicLabStrings.status(saved(c).optString("status")));
        if("file_sha256".equals(c.optString("driver"))){
            pick(PICK_FILE,"*/*");
        }else if("t3_visual".equals(c.optString("driver"))&&
                "NEEDS_SCREENSHOT".equals(saved(c).optString("status"))){
            show("فشل التقاط صورة T3. أرفق لقطة حقيقية من نافذة المختبر أو أعد تشغيل فحوص T3 الآلية.");
        }else show("اقرأ الخطوات أعلاه؛ اكتب ما شاهدته، وأرفق الصورة إذا كانت مطلوبة، ثم اختر نجاحًا أو فشلًا حقيقيًا.");
    }
    void nextPending(){
        refreshPending();
        if(pending.isEmpty()){currentManual=null;drawHome();return;}
        int i=currentManual==null?-1:pending.indexOf(currentManual);
        if(i<0||i+1>=pending.size()){currentManual=null;drawHome();return;}
        openPending(pending.get(i+1));
    }
    void launchManualCase(){
        if(currentManual==null){show("اختر اختبارًا من قسم الطلبات أولًا");return;}
        String driver=currentManual.optString("driver");
        if(driver.equals("mouse_manual")){
            Intent intent=new Intent(this,MainActivity.class);
            intent.putExtra("mini_worker","T4");
            intent.putExtra("manual_case_id",currentManual.optString("id"));
            intent.putExtra("shared_session",session);
            startActivityForResult(intent,MANUAL_CASE);
        }else if(driver.equals("file_sha256"))pick(PICK_FILE,"*/*");
        else if(driver.equals("t3_visual")){
            show("شغّل فحص T3 الآلي مجددًا للحصول على صورة حقيقية أو أرفق صورة التقطتها.");
        }else {
            show("هذا الاختبار يحتاج تشغيل اللعبة أو قراءة ملف أو مشاهدة حالة فعلية؛ اكتب الأدلة في الملاحظة.");
        }
    }
    void manualResult(String decision){
        if(currentManual==null){show("اختر اختبارًا من قائمة الطلبات أولًا");return;}
        JSONObject old=saved(currentManual);
        String uri=old.optString("image_uri");
        if("USER_PASS".equals(decision)&&screenshotRequired(currentManual)&&!screenshotValid(uri)){
            show("الصورة المطلوبة غير موجودة؛ أرفق صورة حقيقية قبل اعتماد النجاح.");return;
        }
        String observation=comment.getText().toString().trim();
        if(observation.isEmpty()){show("اكتب أولًا ما شاهدته فعليًا أو رسالة الخطأ قبل تسجيل النتيجة.");return;}
        if(observation.length()>900)observation=observation.substring(0,900);
        store(currentManual,decision,"OWNER_REPORTED: "+observation+"; driver_observed="+old.optString("observed"),uri);
        export();nextPending();
    }
    String signerSha256(){
        try{
            android.content.pm.PackageInfo p;
            android.content.pm.Signature[] certs;
            if(Build.VERSION.SDK_INT>=28){
                p=getPackageManager().getPackageInfo(getPackageName(),
                    android.content.pm.PackageManager.GET_SIGNING_CERTIFICATES);
                certs=p.signingInfo==null?null:p.signingInfo.getApkContentsSigners();
            }else{
                p=getPackageManager().getPackageInfo(getPackageName(),
                    android.content.pm.PackageManager.GET_SIGNATURES);
                certs=p.signatures;
            }
            return certs!=null&&certs.length>0?digest(certs[0].toByteArray()):"unavailable";
        }catch(Exception e){log("signer_error",e.getClass().getSimpleName());return "unavailable";}
    }
    void pick(int request,String type){
        Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        intent.setType(type);startActivityForResult(intent,request);
    }
    void attachScreenshot(Uri picked)throws Exception{
        if(currentManual==null||!screenshotCase.equals(currentManual.optString("id")))
            throw new IOException("Screenshot target changed");
        byte[] bytes;
        try(InputStream in=getContentResolver().openInputStream(picked)){
            if(in==null)throw new IOException("Unreadable screenshot");
            ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[8192];int n,emptyReads=0;
            while((n=in.read(buf))!=-1){
                if(n==0){
                    if(++emptyReads>=16)throw new IOException("Image provider returned repeated empty reads");
                    continue;
                }
                emptyReads=0;
                if(out.size()+n>20*1024*1024)throw new IOException("Image over 20MiB");
                out.write(buf,0,n);
            }
            bytes=out.toByteArray();
        }
        // Validate recognizable PNG/JPEG/WEBP header; do not accept arbitrary executable data.
        boolean png=bytes.length>8&&(bytes[0]&255)==137&&bytes[1]==80&&bytes[2]==78&&bytes[3]==71;
        boolean jpeg=bytes.length>3&&(bytes[0]&255)==255&&(bytes[1]&255)==216;
        boolean webp=bytes.length>12&&new String(bytes,0,4,StandardCharsets.US_ASCII).equals("RIFF")&&
            new String(bytes,8,4,StandardCharsets.US_ASCII).equals("WEBP");
        if(!png&&!jpeg&&!webp)throw new IOException("Expected PNG/JPEG/WEBP");
        String name=currentManual.optString("id")+"-attached-"+System.currentTimeMillis()+(png?".png":jpeg?".jpg":".webp");
        Uri own=writeMedia(name,png?"image/png":jpeg?"image/jpeg":"image/webp",bytes);
        JSONObject old=saved(currentManual);
        store(currentManual,"EVIDENCE_READY",old.optString("observed")+" screenshot_sha256="+digest(bytes),own.toString());
        show("تم إرفاق الصورة. راجعها ثم اختر نجاحًا أو فشلًا واضغط التالي.");
    }
    void hashFile(Uri input){
        if(currentManual==null||!"file_sha256".equals(currentManual.optString("driver")))return;
        if(fileDigestBusy){show("حساب بصمة الملف يعمل بالفعل؛ أكمله قبل اختيار ملف آخر.");return;}
        fileDigestBusy=true;
        final JSONObject c=currentManual;
        log("file_sha_start","case="+c.optString("id"));
        show("يجري حساب بصمة SHA256 للملف في الخلفية (حتى 16 GiB). أبقِ التطبيق مفتوحًا.");
        fileDigestThread=new Thread(()->{
            try(InputStream in=getContentResolver().openInputStream(input)){
                StreamSha256.Result result=StreamSha256.digest(in,bytes->{
                    final long mib=bytes/(1024L*1024L);
                    runOnUiThread(()->show("جارٍ حساب SHA256: "+mib+" ميغابايت — أبقِ التطبيق مفتوحًا"));
                });
                final String observed="bytes="+result.bytes+" sha256="+result.hex;
                runOnUiThread(()->{
                    store(c,"EVIDENCE_READY",observed,null);
                    fileDigestBusy=false;
                    show(observed+" — قارن البصمة ببصمة مرجعية لنفس الملف، ثم سجّل نجاحًا أو فشلًا");
                });
            }catch(Exception ex){
                final String error=ex.getClass().getSimpleName()+": "+ex.getMessage();
                runOnUiThread(()->{
                    store(c,"BLOCKED","No digest: "+error,null);
                    fileDigestBusy=false;
                    show("فشل حساب SHA256؛ لا يمكن اعتماد بصمة غير مكتملة: "+error);
                });
            }
        },"team-file-sha256");
        fileDigestThread.start();
    }
    Uri writeMedia(String name,String mime,byte[] bytes)throws Exception{
        if(Build.VERSION.SDK_INT<29)throw new IOException("Use Android10+ MediaStore");
        ContentValues v=new ContentValues();v.put(MediaStore.Downloads.DISPLAY_NAME,name);
        v.put(MediaStore.Downloads.MIME_TYPE,mime);
        v.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/Games/cl/test/shared-"+session+"/");
        Uri uri=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
        if(uri==null)throw new IOException("MediaStore insert refused");
        try(OutputStream out=getContentResolver().openOutputStream(uri,"wt")){
            if(out==null)throw new IOException("MediaStore stream refused");
            out.write(bytes);out.flush();
        }
        return uri;
    }
    void log(String event,String payload){
        try{
            JSONObject j=new JSONObject();j.put("time_ms",System.currentTimeMillis());j.put("session",session);
            j.put("apk",BuildConfig.VERSION_NAME);j.put("source",BuildConfig.SOURCE_SHA);
            j.put("pack_sha256",packSha);j.put("event",event);j.put("detail",payload);
            try(OutputStream out=new FileOutputStream(privateLog,true)){
                out.write((j.toString()+"\n").getBytes(StandardCharsets.UTF_8));}
        }catch(Exception e){android.util.Log.e("RaftTeamLab","Log failed",e);}
    }
    void export(){
        try{
            log("export_start","session="+session);
            if(logExport==null){
                byte[] bytes=readFile(privateLog);logExport=writeMedia(privateLog.getName(),"application/x-ndjson",bytes);
            }else{try(InputStream in=new FileInputStream(privateLog);OutputStream out=getContentResolver().openOutputStream(logExport,"wt")){
                if(out==null)throw new IOException("No output stream");byte[] buf=new byte[16384];int n;
                while((n=in.read(buf))>=0)out.write(buf,0,n);out.flush();}
            }
            JSONObject sum=new JSONObject();sum.put("session",session);sum.put("pack_id",packId);
            sum.put("pack_sha256",packSha);sum.put("app_source",BuildConfig.SOURCE_SHA);
            JSONArray cases=new JSONArray();for(JSONObject c:tests){
                JSONObject item=new JSONObject();item.put("case_id",c.getString("id"));item.put("worker",c.getString("worker"));
                item.put("revision",c.getInt("revision"));item.put("result",saved(c));cases.put(item);
            }
            sum.put("results",cases);
            byte[] json=(sum.toString(2)+"\n").getBytes(StandardCharsets.UTF_8);
            if(summaryExport==null)summaryExport=writeMedia("summary-"+session+".json","application/json",json);
            else try(OutputStream out=getContentResolver().openOutputStream(summaryExport,"wt")){out.write(json);out.flush();}
            show("تم حفظ events.jsonl وsummary.json داخل Download/Games/cl/test/shared-"+session+"/");
        }catch(Exception e){log("export_error",e.toString());
            show("تعذر تصدير السجلات؛ بقيت البيانات محفوظة داخل التطبيق. "+e.getClass().getSimpleName());}
    }
    static byte[] readFile(File f)throws IOException{
        try(InputStream in=new FileInputStream(f);ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[16384];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return out.toByteArray();}
    }
    @Override protected void onStop(){super.onStop();export();}
    @Override protected void onDestroy(){
        if(fileDigestThread!=null&&fileDigestThread.isAlive())fileDigestThread.interrupt();
        super.onDestroy();
    }
}
