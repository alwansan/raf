package com.alwansan.lograf;
import org.json.*;
import android.os.SystemClock;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.TimeUnit;

/** Bounded, low-frequency supplemental metrics. No media or private db reads. */
final class ResourceDetails {
    private final Map<String,long[]> previous=new HashMap<>();
    private final Map<String,long[]> threads=new HashMap<>();
    private long threadAt=-1,networkAt=-1,lastThreadSample=-1,lastPing=-1,lastDisk=-1;
    private JSONObject cachedThreads=new JSONObject(),ping=new JSONObject(),disk=new JSONObject();
    private static String read(String path,int limit)throws IOException{
        try(InputStream in=new FileInputStream(path)){byte[] b=new byte[limit];int n=in.read(b);return n<=0?"":new String(b,0,n,StandardCharsets.UTF_8);}
    }
    private void rate(JSONObject x,String prefix,String key,int pid,long now)throws JSONException{
        long val=x.optLong(key,-1);String k=prefix+key;long[] old=previous.get(k);
        Object v=JSONObject.NULL;
        if(val>=0&&pid>0){if(old!=null&&old[0]==pid&&now>old[1]&&val>=old[2])v=(val-old[2])*1000L/(now-old[1]);previous.put(k,new long[]{pid,now,val});}
        else previous.remove(k);
        x.put(key.replace("_bytes","_bytes_per_second").replace("io_",""),v);
    }
    void enrich(JSONObject row,int pid,int worker,long now,long hz)throws JSONException{
        rate(row,"main:","process_io_read_bytes",pid,now);rate(row,"main:","process_io_write_bytes",pid,now);
        JSONObject dl=row.optJSONObject("filedownloader");if(dl!=null){rate(dl,"worker:","io_read_bytes",worker,now);rate(dl,"worker:","io_write_bytes",worker,now);}
        long total=new File("/storage/emulated/0").getTotalSpace();
        row.put("device_storage_total_bytes",total>0?total:JSONObject.NULL);
        long free=row.optLong("device_storage_free_bytes",-1);
        row.put("device_storage_used_bytes",total>0&&free>=0&&free<=total?total-free:JSONObject.NULL);
        if(lastThreadSample<0||now-lastThreadSample>=15000){lastThreadSample=now;cachedThreads=top(pid,worker,now,hz);}
        row.put("top_thread_cpu",cachedThreads).put("top_thread_sample_age_ms",now-lastThreadSample);
        if(lastDisk<0||now-lastDisk>=15000){lastDisk=now;disk=readDisk();}
        row.put("device_diskstats",disk).put("diskstats_sample_age_ms",now-lastDisk);
        if(lastPing<0||now-lastPing>=60000){lastPing=now;ping=pingGateway();}
        row.put("gateway_ping",ping).put("gateway_ping_sample_age_ms",now-lastPing);
    }
    private JSONObject top(int main,int worker,long now,long hz)throws JSONException{
        JSONObject out=new JSONObject();Map<String,long[]> next=new HashMap<>();
        for(int pid:new int[]{main,worker}){
            if(pid<=0)continue;
            File[] files=new File("/proc/"+pid+"/task").listFiles();if(files==null){out.put(pid==main?"main":"filedownloader",JSONObject.NULL);continue;}
            Arrays.sort(files,Comparator.comparing(File::getName));ArrayList<JSONObject> samples=new ArrayList<>();
            int done=0;for(File f:files){if(done++>=256)break;try{
                String stat=read(new File(f,"stat").getPath(),2048);int a=stat.indexOf('('),b=stat.lastIndexOf(')');if(a<0||b<a)continue;
                String[] s=stat.substring(b+2).trim().split("\\s+");if(s.length<20)continue;
                long ticks=Long.parseLong(s[11])+Long.parseLong(s[12]),start=Long.parseLong(s[19]);String k=pid+":"+f.getName()+":"+start;
                long[] old=threads.get(k);next.put(k,new long[]{ticks,now});
                if(old==null||now<=old[1]||ticks<old[0])continue;
                String name=stat.substring(a+1,b);int tid=Integer.parseInt(f.getName());
                String group=tid==pid?"main":name.matches("(?i).*(render|hwui).*")?"render":name.matches("(?i).*(binder).*")?"binder":name.matches("(?i).*(gc|heap|jit).*")?"runtime":name.matches("(?i).*(okhttp|download|ffmpeg|cinemana|pool|worker).*")?"worker":"other";
                samples.add(new JSONObject().put("tid",tid).put("category",group).put("cpu_percent_one_core",Math.round(10000000.0*(ticks-old[0])/hz/(now-old[1]))/100.0));
            }catch(Exception ignored){}}
            samples.sort((x,y)->Double.compare(y.optDouble("cpu_percent_one_core"),x.optDouble("cpu_percent_one_core")));
            JSONArray arr=new JSONArray();for(int i=0;i<Math.min(6,samples.size());i++)arr.put(samples.get(i));
            out.put(pid==main?"main":"filedownloader",new JSONObject().put("threads_total",files.length).put("capped",files.length>256).put("top",arr));
        }
        threads.clear();threads.putAll(next);return out;
    }
    private JSONObject readDisk()throws JSONException{
        JSONObject o=new JSONObject();JSONArray devices=new JSONArray();try{
            String text=read("/proc/diskstats",32768);for(String line:text.split("\\n")){
                String[] a=line.trim().split("\\s+");if(a.length<14||devices.length()>=16)continue;
                if(!a[2].matches("(sd[a-z]+|mmcblk[0-9]+|nvme[0-9]+n[0-9]+|dm-[0-9]+)"))continue;
                devices.put(new JSONObject().put("device",a[2]).put("read_sectors",Long.parseLong(a[5])).put("write_sectors",Long.parseLong(a[9])).put("io_ms",Long.parseLong(a[12])));
            }
            o.put("devices",devices).put("status",devices.length()>0?"available":"unavailable").put("note","Device-wide cumulative counters; layers may overlap; do not sum.");
        }catch(Exception e){o.put("status","unavailable:"+e.getClass().getSimpleName());}return o;
    }
    private String cmd(int ms,String... args)throws Exception{
        Process p=new ProcessBuilder(args).redirectErrorStream(true).start();try{
            if(!p.waitFor(ms,TimeUnit.MILLISECONDS)){p.destroyForcibly();return "";}
            try(InputStream in=p.getInputStream()){byte[] b=new byte[4096];int n=in.read(b);return n<=0?"":new String(b,0,n,StandardCharsets.UTF_8);}
        }finally{p.destroy();}
    }
    private JSONObject pingGateway()throws JSONException{
        JSONObject o=new JSONObject().put("scope","local IPv4 gateway only; not Cinemana server RTT").put("rtt_ms",JSONObject.NULL);
        try{
            String routes=cmd(600,"ip","route","show","default");
            java.util.regex.Matcher m=java.util.regex.Pattern.compile("(?m)^default via ([0-9.]+) ").matcher(routes);
            if(!m.find()){o.put("status","gateway_unavailable");return o;}
            String raw=cmd(1500,"ping","-c","1","-W","1",m.group(1));
            java.util.regex.Matcher rt=java.util.regex.Pattern.compile("time[=<]([0-9.]+)\\s*ms").matcher(raw);
            if(rt.find())o.put("rtt_ms",Double.parseDouble(rt.group(1))).put("status","reply");else o.put("status","no_reply_or_denied");
        }catch(Exception e){o.put("status","unavailable");}return o;
    }
}
