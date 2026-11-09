package com.alwansan.raftlab;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Locale;

/** Non-invasive bounded keyword inventory for owner-selected BlackBox text.
 * Never records source log lines, paths, PIDs, account data or game content.
 */
public final class LocalOwnerLogEvidence {
    private static final int MAX_BYTES=4*1024*1024;
    private LocalOwnerLogEvidence() {}

    public static String summarize(InputStream stream)throws IOException {
        if(stream==null)throw new IOException("No selected text stream");
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        byte[] block=new byte[8192];
        int n,zero=0;
        while(out.size()<MAX_BYTES&&(n=stream.read(block,0,Math.min(block.length,MAX_BYTES-out.size())))!=-1){
            if(n==0){
                if(++zero>=16)throw new IOException("Provider returned repeated zero bytes");
                continue;
            }
            zero=0;out.write(block,0,n);
        }
        byte[] bytes=out.toByteArray();
        if(bytes.length==0)throw new IOException("Empty log file");
        String content=new String(bytes,StandardCharsets.ISO_8859_1).toLowerCase(Locale.ROOT);
        String[] keys={
            "ultimate_water_invalid_pass","water_fft_invalid_compute_kernel",
            "unity_cursor_rgba32_required","dx11fft",
            "main.91.com.alwansan.raft.androidtest.obb",
            "patch.91.com.alwansan.raft.androidtest.obb",
            "world has been loaded","having issues connecting"
        };
        StringBuilder b=new StringBuilder("📑 إحصاء جزئي دون نسخ السطور الأصلية من سجل BlackBox:\n");
        for(String key:keys)b.append(key).append(" = ").append(count(content,key)).append("\n");
        b.append("bytes_scanned=").append(bytes.length).append("؛ ");
        if(bytes.length==MAX_BYTES)b.append("اقتصر الفحص على أول 4 MiB؛ قد توجد أحداث أخرى بعد ذلك.\n");
        else b.append("انتهى الملف ضمن حد 4 MiB.\n");
        b.append("هذه أعداد ظهور نصوص، لا تقيس أخطاء لعبة Raft مباشرة، ولا تثبت أصلها أو نجاح أي حالة؛ لا يُرفع نص السجل تلقائيًا.");
        return b.toString();
    }
    private static int count(String text,String key){
        int found=0,at=0,pos;
        while((pos=text.indexOf(key,at))>=0){found++;at=pos+key.length();}
        return found;
    }
}
