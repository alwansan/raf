package com.alwansan.lograf;

import android.os.SystemClock;
import android.system.Os;
import android.system.OsConstants;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.IntSupplier;

/**
 * Low-frequency, game-specific metrics from the Shizuku shell process.
 * Unavailable counters are null, never fabricated zero. No game private files
 * are read. No heavyweight graphics profiler is enabled.
 */
public final class PerformanceSampler implements Runnable {
    interface Emitter { void emit(String jsonLine); }
    private final String target;
    private final IntSupplier pidSupplier;
    private final AtomicBoolean running;
    private final Emitter emitter;
    private int previousPid=-1;
    private long previousTicks=-1, previousAt=-1, previousPresent=-1, previousFrameAt=-1;
    private long pssLast=0, batteryLast=0, layersLast=0, thermalLast=0;
    private Long pssCache=null;
    private int pssPid=-1;
    private int lastObservedPid=-1;
    private Integer batteryLevel=null, batteryStatus=null, thermalStatus=null;
    private Double batteryTemp=null;
    private String surfaceLayer=null;
    private long sample=0;
    private static final String GPU="/sys/class/kgsl/kgsl-3d0/";
    private final long ticksPerSecond;
    private final int cpuCount=Math.max(1,Runtime.getRuntime().availableProcessors());

    PerformanceSampler(String target, IntSupplier pidSupplier, AtomicBoolean running, Emitter emitter) {
        this.target=target; this.pidSupplier=pidSupplier; this.running=running; this.emitter=emitter;
        long ticks=100;
        try { ticks=Os.sysconf(OsConstants._SC_CLK_TCK); } catch(Throwable ignored) {}
        ticksPerSecond=Math.max(1,ticks);
    }

    @Override public void run() {
        while(running.get() && !Thread.currentThread().isInterrupted()) {
            try { emitter.emit(sample()+"\n"); }
            catch(Throwable err) {
                try { emitter.emit("{\"source\":\"lograf\",\"error\":\"telemetry_exception\",\"type\":\""+
                        err.getClass().getSimpleName()+"\"}\n"); } catch(Throwable ignored){}
            }
            try { Thread.sleep(3000); } catch(InterruptedException e) { Thread.currentThread().interrupt(); break; }
        }
    }

    private JSONObject sample() throws Exception {
        long now=SystemClock.elapsedRealtime();
        int pid=pidSupplier.getAsInt();
        JSONObject row=new JSONObject();
        row.put("schema",1).put("source","lograf_shell").put("timestamp_unix_ms",System.currentTimeMillis())
                .put("elapsed_ms",now).put("sample",++sample).put("package",target)
                .put("pid",pid>0?pid:JSONObject.NULL).put("cpu_cores_online",cpuCount);
        if(pid!=lastObservedPid) {
            row.put("process_transition",pid>0?"game_started":lastObservedPid>0?"game_exited":"none");
            row.put("previous_pid",lastObservedPid>0?lastObservedPid:JSONObject.NULL);
            if(pid!=pssPid){pssCache=null;pssPid=-1;pssLast=0;}
            surfaceLayer=null;layersLast=0;previousPresent=-1;
            lastObservedPid=pid;
        }
        if(pid<=0) {
            row.put("state","game_not_running");
            previousPid=-1; previousTicks=-1; previousAt=-1; previousPresent=-1;
        } else {
            row.put("state","game_running");
            JSONObject cpu;
            try { cpu=cpuUsage(pid,now); }
            catch(Exception e) { cpu=new JSONObject(); row.put("process_cpu_error",e.getClass().getSimpleName()); }
            row.put("process_cpu_percent_one_core",cpu.opt("core_pct") == null?JSONObject.NULL:cpu.opt("core_pct"));
            row.put("process_cpu_percent_all_cores",cpu.opt("device_pct")==null?JSONObject.NULL:cpu.opt("device_pct"));
            row.put("process_cpu_source","/proc/pid/stat utime+stime / elapsed wall time");
            JSONObject proc=processStatus(pid);
            row.put("process_rss_kb",proc.opt("VmRSS")==null?JSONObject.NULL:proc.opt("VmRSS"));
            row.put("process_rss_peak_kb",proc.opt("VmHWM")==null?JSONObject.NULL:proc.opt("VmHWM"));
            row.put("process_threads",proc.opt("Threads")==null?JSONObject.NULL:proc.opt("Threads"));
            if(now-pssLast>15000 || pssPid!=pid) {
                pssLast=now; pssPid=pid; pssCache=readPss(pid);
            }
            long rss=proc.optLong("VmRSS",-1);
            boolean validPss=pssCache!=null && (rss<0 || pssCache<=rss+8192);
            row.put("process_pss_kb",validPss?pssCache:JSONObject.NULL);
            row.put("pss_validated_against_rss",validPss);
            row.put("pss_sample_age_ms",pssCache==null?JSONObject.NULL:Math.max(0,now-pssLast));
            row.put("memory_sources","/proc/pid/status; dumpsys meminfo pid when available");
            JSONObject io=processIo(pid);
            row.put("process_io_read_bytes",io.opt("read_bytes")==null?JSONObject.NULL:io.opt("read_bytes"));
            row.put("process_io_write_bytes",io.opt("write_bytes")==null?JSONObject.NULL:io.opt("write_bytes"));
        }
        long storageFree=new File("/storage/emulated/0").getUsableSpace();
        row.put("device_storage_free_bytes",storageFree>0?storageFree:JSONObject.NULL);
        JSONObject sys=procMeminfo();
        row.put("device_mem_available_kb",sys.opt("MemAvailable")==null?JSONObject.NULL:sys.opt("MemAvailable"));
        row.put("device_mem_total_kb",sys.opt("MemTotal")==null?JSONObject.NULL:sys.opt("MemTotal"));
        row.put("system_load_1min",loadAverage());
        row.put("cpu_frequency_khz_by_core",cpuFrequencies());
        JSONObject gpu=gpuMetrics();
        row.put("gpu_busy_percent",gpu.opt("busy")==null?JSONObject.NULL:gpu.opt("busy"));
        row.put("gpu_clock_hz",gpu.opt("clock")==null?JSONObject.NULL:gpu.opt("clock"));
        row.put("gpu_utilization_source","KGSL system-wide busy/total, if shell-readable");
        String gpuModel=readOptional(GPU+"gpu_model",256);
        row.put("gpu_model",gpuModel==null?JSONObject.NULL:gpuModel);
        if(now-batteryLast>14000){ batteryLast=now; battery(); }
        row.put("battery_level_percent",batteryLevel==null?JSONObject.NULL:batteryLevel)
                .put("battery_temp_c",batteryTemp==null?JSONObject.NULL:batteryTemp)
                .put("battery_status_code",batteryStatus==null?JSONObject.NULL:batteryStatus);
        if(now-thermalLast>20000){thermalLast=now; thermalStatus=readThermalStatus();}
        row.put("thermal_status_code",thermalStatus==null?JSONObject.NULL:thermalStatus);
        if(pid>0 && now-layersLast>25000){layersLast=now; discoverSurface();}
        Double fps=pid>0?presentedFps(now):null;
        row.put("presented_fps_estimate",fps==null?JSONObject.NULL:fps);
        row.put("fps_method","SurfaceFlinger --latency game SurfaceView (NOT Unity Update FPS)");
        row.put("fps_surface",surfaceLayer==null?JSONObject.NULL:surfaceLayer);
        row.put("unity_frame_cpu_ms",JSONObject.NULL).put("unity_frame_gpu_ms",JSONObject.NULL);
        row.put("unity_frame_timing_reason","Requires game-side Unity FrameTimingManager diagnostics");
        return row;
    }

    private JSONObject cpuUsage(int pid,long now) throws Exception {
        JSONObject o=new JSONObject();
        String stat=readFile("/proc/"+pid+"/stat",2048);
        int end=stat.lastIndexOf(')');
        if(end<0 || stat.length()<end+8) return o;
        String[] fields=stat.substring(end+2).trim().split("\\s+");
        if(fields.length<22) return o;
        // After "pid (comm) ", fields[0] is Linux /proc stat field #3 (state).
        long ticks=Long.parseLong(fields[11])+Long.parseLong(fields[12]);
        if(pid==previousPid && previousTicks>=0 && now>previousAt && ticks>=previousTicks){
            double elapsedMs=now-previousAt;
            double consumedMs=(ticks-previousTicks)*1000.0/ticksPerSecond;
            double percent=100.0*consumedMs/elapsedMs;
            if(Double.isFinite(percent) && percent>=0){
                o.put("core_pct",round(percent)).put("device_pct",round(percent/cpuCount));
            }
        }
        previousPid=pid;previousTicks=ticks;previousAt=now;
        return o;
    }

    private JSONObject processStatus(int pid){
        JSONObject o=new JSONObject();
        try {
            String s=readFile("/proc/"+pid+"/status",16384);
            for(String line:s.split("\\n")){
                for(String key:new String[]{"VmRSS","VmHWM","Threads"}){
                    if(line.startsWith(key+":")){
                        String[] v=line.substring(key.length()+1).trim().split("\\s+");
                        o.put(key,Long.parseLong(v[0]));
                    }
                }
            }
        }catch(Exception ignored){}
        return o;
    }

    private JSONObject processIo(int pid) {
        JSONObject o=new JSONObject();
        try{
            for(String line:readFile("/proc/"+pid+"/io",4096).split("\\n")){
                if(line.startsWith("read_bytes:") || line.startsWith("write_bytes:")){
                    String[] pair=line.split(":");
                    o.put(pair[0].trim(),Long.parseLong(pair[1].trim()));
                }
            }
        }catch(Exception ignored){}
        return o;
    }

    private JSONObject procMeminfo() {
        JSONObject o=new JSONObject();
        try{
            for(String line:readFile("/proc/meminfo",6000).split("\\n")){
                if(line.startsWith("MemTotal:") || line.startsWith("MemAvailable:")){
                    String[] pair=line.split(":");
                    o.put(pair[0],Long.parseLong(pair[1].trim().split("\\s+")[0]));
                }
            }
        }catch(Exception ignored){}
        return o;
    }

    private Object loadAverage(){
        try { return round(Double.parseDouble(readFile("/proc/loadavg",200).trim().split("\\s+")[0])); }
        catch(Exception ignored){return JSONObject.NULL;}
    }

    private org.json.JSONArray cpuFrequencies(){
        org.json.JSONArray result=new org.json.JSONArray();
        for(int i=0;i<cpuCount;i++){
            String value=readOptional("/sys/devices/system/cpu/cpu"+i+"/cpufreq/scaling_cur_freq",80);
            try { result.put(value==null?JSONObject.NULL:Long.parseLong(value.trim())); }
            catch(Exception e){result.put(JSONObject.NULL);}
        }
        return result;
    }

    private static String readOptional(String path,int maxBytes){
        try {String s=readFile(path,maxBytes).trim(); return s.isEmpty()?null:s;}
        catch(Exception e){return null;}
    }

    private JSONObject gpuMetrics(){
        JSONObject o=new JSONObject();
        try{
            String[] busy=readFile(GPU+"gpubusy",100).trim().split("\\s+");
            if(busy.length>=2){
                long a=Long.parseLong(busy[0]),b=Long.parseLong(busy[1]);
                if(a>=0 && b>0 && a<=b)o.put("busy",round(100.0*a/b));
            }
        }catch(Exception ignored){}
        for(String candidate:new String[]{GPU+"gpuclk",GPU+"devfreq/cur_freq"}){
            try {
                long hz=Long.parseLong(readFile(candidate,100).trim());
                if(hz>0){o.put("clock",hz);break;}
            }catch(Exception ignored){}
        }
        return o;
    }

    private Long readPss(int pid){
        // Only collect scalar total PSS, never save a full process memory map.
        try {
            String raw=command(2000,65536,"dumpsys","meminfo",Integer.toString(pid));
            java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?m)^\\s*TOTAL PSS:\\s*([0-9,]+)").matcher(raw);
            if(m.find()) return Long.parseLong(m.group(1).replace(",",""));
            m=java.util.regex.Pattern.compile("(?m)^\\s*TOTAL\\s+([0-9,]+)\\s+").matcher(raw);
            if(m.find()) return Long.parseLong(m.group(1).replace(",",""));
        }catch(Exception ignored){}
        return null;
    }

    private void battery() {
        try {
            String text=command(1200,7000,"dumpsys","battery");
            Integer level=intKey(text,"level"), temp=intKey(text,"temperature");
            batteryLevel=level; batteryTemp=temp==null?null:temp/10.0;
            batteryStatus=intKey(text,"status");
        } catch(Exception ignored){}
    }

    private Integer readThermalStatus(){
        try{
            String text=command(1600,14000,"dumpsys","thermalservice");
            java.util.regex.Matcher m=java.util.regex.Pattern.compile(
                "(?im)^\\s*(?:Thermal Status|mStatus|Current Thermal Status):?\\s*([0-6])\\s*$").matcher(text);
            if(m.find())return Integer.parseInt(m.group(1));
        }catch(Exception ignored){}
        return null;
    }

    private static Integer intKey(String text,String key) {
        java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?m)^\\s*"+key+":\\s*(-?\\d+)").matcher(text);
        return m.find()?Integer.parseInt(m.group(1)):null;
    }

    private void discoverSurface(){
        try{
            String list=command(1400,240000,"dumpsys","SurfaceFlinger","--list");
            for(String line:list.split("\\n")){
                if(!line.contains(target) || !line.contains("SurfaceView") || line.contains("Background for"))continue;
                String name=line.trim();
                if(name.startsWith("RequestedLayerState{")){
                    name=name.substring("RequestedLayerState{".length());
                    int end=name.indexOf(" parentId=");
                    if(end>0)name=name.substring(0,end);
                    if(name.endsWith("}"))name=name.substring(0,name.length()-1);
                }
                if(name.isEmpty())continue;
                if(!name.equals(surfaceLayer)){previousPresent=-1;previousFrameAt=-1;}
                surfaceLayer=name;return;
            }
            surfaceLayer=null;
        } catch(Exception ignored){surfaceLayer=null;}
    }

    private Double presentedFps(long now){
        if(surfaceLayer==null || surfaceLayer.isEmpty())return null;
        try{
            String output=command(1400,20000,"dumpsys","SurfaceFlinger","--latency",surfaceLayer);
            String[] lines=output.trim().split("\\n");
            if(lines.length<3 || !lines[0].trim().matches("\\d+"))return null;
            long newest=-1;
            List<Long> presents=new ArrayList<>();
            for(int i=1;i<lines.length;i++){
                String[] parts=lines[i].trim().split("\\s+");
                if(parts.length!=3)continue;
                long stamp=Long.parseLong(parts[1]); // actual present timestamp, not ready-fence timestamp
                if(stamp>0 && stamp<Long.MAX_VALUE/2){
                    presents.add(stamp);
                    if(stamp>newest)newest=stamp;
                }
            }
            if(presents.size()<2)return null;
            if(newest==previousPresent){previousFrameAt=now;return 0.0;}
            // SurfaceFlinger only exposes a small RING BUFFER of recent frames
            // (often 128). Dividing 128 by our 3-second polling interval would
            // falsely report ~42fps for a real 60fps game. Compute the rate
            // from timestamp intervals instead, and require new presentation.
            if(previousPresent<0) {
                previousPresent=newest; previousFrameAt=now;
                return null; // first sample establishes baseline
            }
            if(newest<previousPresent){
                previousPresent=newest;previousFrameAt=now;
                return null; // layer recreated or counters reset
            }
            Collections.sort(presents);
            long earliest=Long.MAX_VALUE,latest=-1;
            int count=0;
            for(long stamp:presents){
                if(stamp<=0 || newest-stamp>2_000_000_000L)continue;
                if(stamp==latest)continue;
                if(earliest==Long.MAX_VALUE)earliest=stamp;
                latest=stamp;count++;
            }
            previousPresent=newest;previousFrameAt=now;
            if(count<3 || earliest>=latest)return null;
            double fps=1_000_000_000.0*(count-1)/(latest-earliest);
            return fps>0 && fps<300?round(fps):null;
        }catch(Exception ignored){}
        return null;
    }

    private static double round(double value){return Math.round(value*100.0)/100.0;}

    private static String readFile(String path,int limit) throws IOException {
        try(InputStream in=new FileInputStream(path);ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] buf=new byte[2048];int n;
            while((n=in.read(buf))!=-1){
                if(out.size()+n>limit)throw new IOException("Input too large: "+path);
                out.write(buf,0,n);
            }
            return out.toString("UTF-8");
        }
    }

    private static String command(long timeoutMs,int cap,String... args) throws Exception {
        Process proc=new ProcessBuilder(args).redirectErrorStream(true).start();
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        Thread reader=new Thread(()->{
            try(InputStream in=proc.getInputStream()){
                byte[] buf=new byte[8192];int n;
                while((n=in.read(buf))!=-1){
                    synchronized(out){if(out.size()<cap)out.write(buf,0,Math.min(n,cap-out.size()));}
                }
            }catch(IOException ignored){}
        },"lograf-command-drain");
        reader.setDaemon(true);
        reader.start();
        try{
            if(!proc.waitFor(timeoutMs,TimeUnit.MILLISECONDS)){
                proc.destroyForcibly();
                throw new IOException("command timed out: "+args[0]);
            }
            reader.join(250);
            synchronized(out){return out.toString("UTF-8");}
        }finally{proc.destroy();}
    }
}
