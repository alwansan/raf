package com.alwansan.raftlab;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.zip.CRC32;

/**
 * A bounded container gate for screenshots explicitly selected by the owner.
 * This is not visual approval: Android BitmapFactory must also decode pixels.
 * No external content, executable code, or caller-provided path is loaded.
 */
public final class ManualImageEvidencePolicy {
    private ManualImageEvidencePolicy() {}
    public static final int MAX_BYTES=20*1024*1024;
    public static final long MAX_PIXELS=40_000_000L;
    public static final int MAX_DIMENSION=16384;

    public static final class Info {
        public final String mime;
        public final String suffix;
        private Info(String mime,String suffix){this.mime=mime;this.suffix=suffix;}
    }

    public static Info inspect(byte[] b)throws IOException{
        if(b==null||b.length<12||b.length>MAX_BYTES)
            throw new IOException("Image bytes missing or exceed 20 MiB");
        if(matches(b,0,new byte[]{(byte)137,80,78,71,13,10,26,10}))
            return inspectPng(b);
        if((b[0]&255)==255&&(b[1]&255)==216){
            if(b.length<16||(b[b.length-2]&255)!=255||(b[b.length-1]&255)!=217)
                throw new IOException("JPEG has no complete end marker");
            return new Info("image/jpeg",".jpg");
        }
        if(ascii(b,0,"RIFF")&&ascii(b,8,"WEBP"))
            return inspectWebp(b);
        throw new IOException("Expected complete PNG, JPEG or WebP image");
    }

    private static Info inspectPng(byte[] b)throws IOException{
        int offset=8;
        boolean ihdr=false,idat=false;
        while(offset<b.length){
            if(b.length-offset<12)throw new IOException("Truncated PNG chunk header");
            long rawSize=u32be(b,offset);
            if(rawSize>b.length-offset-12L)
                throw new IOException("Truncated PNG chunk payload");
            int size=(int)rawSize;
            for(int i=0;i<4;i++){
                int c=b[offset+4+i]&255;
                if(!((c>=65&&c<=90)||(c>=97&&c<=122)))
                    throw new IOException("Invalid PNG chunk type");
            }
            String type=new String(b,offset+4,4,StandardCharsets.US_ASCII);
            CRC32 crc=new CRC32();
            crc.update(b,offset+4,size+4);
            if(crc.getValue()!=u32be(b,offset+8+size))
                throw new IOException("PNG chunk CRC mismatch");
            if(!ihdr&&!type.equals("IHDR"))
                throw new IOException("PNG must begin with IHDR");
            if(type.equals("IHDR")){
                if(ihdr||size!=13)throw new IOException("Invalid duplicate PNG IHDR");
                long width=u32be(b,offset+8),height=u32be(b,offset+12);
                if(width==0||height==0||width>MAX_DIMENSION||height>MAX_DIMENSION
                        ||width*height>MAX_PIXELS)
                    throw new IOException("PNG dimensions exceed safe bounds");
                int bit=b[offset+16]&255,color=b[offset+17]&255;
                boolean valid=(color==0&&(bit==1||bit==2||bit==4||bit==8||bit==16))
                        ||(color==2&&(bit==8||bit==16))
                        ||(color==3&&(bit==1||bit==2||bit==4||bit==8))
                        ||(color==4&&(bit==8||bit==16))
                        ||(color==6&&(bit==8||bit==16));
                if(!valid||(b[offset+18]&255)!=0||(b[offset+19]&255)!=0
                        ||(b[offset+20]&255)>1)
                    throw new IOException("Unsupported PNG format");
                ihdr=true;
            }else if(type.equals("IDAT")){
                if(size>0)idat=true;
            }else if(type.equals("IEND")){
                if(size!=0||!idat||offset+12!=b.length)
                    throw new IOException("PNG IEND missing, invalid or has trailing bytes");
                return new Info("image/png",".png");
            }
            offset+=12+size;
        }
        throw new IOException("PNG missing terminal IEND");
    }

    private static Info inspectWebp(byte[] b)throws IOException{
        if(b.length<20||u32le(b,4)+8L!=b.length)
            throw new IOException("Invalid WebP RIFF declared length");
        int offset=12;
        boolean imageChunk=false;
        while(offset<b.length){
            if(b.length-offset<8)throw new IOException("Truncated WebP chunk");
            long size=u32le(b,offset+4);
            long padded=size+(size&1L);
            if(padded>b.length-offset-8L)
                throw new IOException("Truncated WebP payload");
            if(ascii(b,offset,"VP8 ")||ascii(b,offset,"VP8L")||ascii(b,offset,"VP8X"))
                imageChunk=true;
            offset+=(int)(8+padded);
        }
        if(!imageChunk||offset!=b.length)throw new IOException("WebP image payload missing");
        return new Info("image/webp",".webp");
    }

    private static long u32be(byte[] b,int at){
        return ((long)(b[at]&255)<<24)|((long)(b[at+1]&255)<<16)
                |((long)(b[at+2]&255)<<8)|(b[at+3]&255);
    }
    private static long u32le(byte[] b,int at){
        return (b[at]&255L)|((b[at+1]&255L)<<8)
                |((b[at+2]&255L)<<16)|((b[at+3]&255L)<<24);
    }
    private static boolean matches(byte[] b,int at,byte[] prefix){
        if(at+prefix.length>b.length)return false;
        for(int i=0;i<prefix.length;i++)if(b[at+i]!=prefix[i])return false;
        return true;
    }
    private static boolean ascii(byte[] b,int at,String s){
        if(at+s.length()>b.length)return false;
        for(int i=0;i<s.length();i++)if(b[at+i]!=(byte)s.charAt(i))return false;
        return true;
    }
}
