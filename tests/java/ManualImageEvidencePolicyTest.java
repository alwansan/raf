package com.alwansan.raftlab;

import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.zip.CRC32;
import java.util.zip.DeflaterOutputStream;

public final class ManualImageEvidencePolicyTest {
    private static int assertions=0;
    private static void yes(boolean ok,String label){
        assertions++;
        if(!ok)throw new AssertionError(label);
    }
    private static void rejected(byte[] bytes,String name){
        try{
            ManualImageEvidencePolicy.inspect(bytes);
            throw new AssertionError("Accepted bad image: "+name);
        }catch(IOException expected){assertions++;}
    }
    private static void chunk(DataOutputStream out,String type,byte[] data)throws Exception{
        out.writeInt(data.length);
        byte[] name=type.getBytes(java.nio.charset.StandardCharsets.US_ASCII);
        out.write(name);
        out.write(data);
        CRC32 c=new CRC32();c.update(name);c.update(data);
        out.writeInt((int)c.getValue());
    }
    private static byte[] image(int width,int height)throws Exception{
        ByteArrayOutputStream encoded=new ByteArrayOutputStream();
        DataOutputStream out=new DataOutputStream(encoded);
        out.write(new byte[]{(byte)137,80,78,71,13,10,26,10});
        ByteArrayOutputStream header=new ByteArrayOutputStream();
        DataOutputStream ihdr=new DataOutputStream(header);
        ihdr.writeInt(width);ihdr.writeInt(height);ihdr.write(new byte[]{8,6,0,0,0});
        chunk(out,"IHDR",header.toByteArray());
        ByteArrayOutputStream deflated=new ByteArrayOutputStream();
        try(DeflaterOutputStream zip=new DeflaterOutputStream(deflated)){
            zip.write(new byte[]{0,(byte)255,0,0,(byte)255});
        }
        chunk(out,"IDAT",deflated.toByteArray());
        chunk(out,"IEND",new byte[0]);
        out.flush();
        return encoded.toByteArray();
    }
    private static byte[] webp()throws Exception{
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        bytes.write("RIFF".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
        bytes.write(new byte[]{14,0,0,0});
        bytes.write("WEBPVP8 ".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
        bytes.write(new byte[]{2,0,0,0,9,8});
        return bytes.toByteArray();
    }
    public static void main(String[] args)throws Exception{
        byte[] good=image(1,1);
        ManualImageEvidencePolicy.Info p=ManualImageEvidencePolicy.inspect(good);
        yes("image/png".equals(p.mime)&&".png".equals(p.suffix),"valid PNG");
        byte[] fakeHead=Arrays.copyOf(good,12);rejected(fakeHead,"header only");
        rejected(Arrays.copyOf(good,good.length-12),"missing IEND");
        byte[] withTail=Arrays.copyOf(good,good.length+1);
        rejected(withTail,"trailing bytes after IEND");
        byte[] changed=good.clone();changed[29]^=1;
        rejected(changed,"IHDR CRC");
        rejected(image(20000,1),"oversized width");
        rejected(image(8000,8000),"pixel count");
        byte[] missing=good.clone();missing[36]=0;
        rejected(missing,"corrupt IDAT chunk length");
        byte[] badJpeg=new byte[]{(byte)255,(byte)216,0,1,2};
        rejected(badJpeg,"missing JPEG EOI");
        byte[] jpeg=new byte[20];
        jpeg[0]=(byte)255;jpeg[1]=(byte)216;
        jpeg[18]=(byte)255;jpeg[19]=(byte)217;
        yes("image/jpeg".equals(ManualImageEvidencePolicy.inspect(jpeg).mime),
                "JPEG container gate; Android pixel decode is still mandatory");
        byte[] webp=webp();
        yes("image/webp".equals(ManualImageEvidencePolicy.inspect(webp).mime),
                "WebP RIFF gate; Android pixel decode is still mandatory");
        byte[] badWebp=webp.clone();badWebp[4]=13;rejected(badWebp,"WebP length");
        byte[] truncated=Arrays.copyOf(webp,webp.length-1);
        rejected(truncated,"WebP truncated");
        rejected(new byte[20],"random header");
        System.out.println("PASS: "+assertions+
                " bounded image container assertions (Android BitmapFactory separately required)");
    }
}
