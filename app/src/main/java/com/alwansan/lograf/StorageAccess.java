package com.alwansan.lograf;
import android.content.Context;
import android.content.ContentResolver;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.DocumentsContract;
import java.io.*;

final class StorageAccess {
    static final File WORK=new File("/storage/emulated/0/Cinemana/work");
    static final File OUTPUT=new File("/storage/emulated/0/Download/Games/cl/Clog");
    static boolean direct(Context c) {
        return Build.VERSION.SDK_INT>=30 ? Environment.isExternalStorageManager()
                : c.checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)==android.content.pm.PackageManager.PERMISSION_GRANTED;
    }
    static boolean file(Uri u){return u!=null && "file".equals(u.getScheme());}
    static File outputFile(Uri u)throws IOException{
        File f=new File(u.getPath()).getCanonicalFile(),root=OUTPUT.getCanonicalFile();
        if(!f.equals(root)&&!f.getPath().startsWith(root.getPath()+File.separator))throw new IOException("Output outside CLog");
        return f;
    }
    static Uri base(ContentResolver r,Uri u)throws IOException{
        if(file(u)){File f=outputFile(u);if(!f.isDirectory()&&!f.mkdirs())throw new IOException("Cannot create CLog folder");return Uri.fromFile(f);}
        return DocumentsContract.buildDocumentUriUsingTree(u,DocumentsContract.getTreeDocumentId(u));
    }
    static Uri create(ContentResolver r,Uri parent,String mime,String name)throws IOException{
        if(!file(parent))return DocumentsContract.createDocument(r,parent,mime,name);
        if(name.contains("/")||name.contains("\\")||name.equals("..")||name.equals("."))throw new IOException("Invalid name");
        File f=outputFile(Uri.fromFile(new File(outputFile(parent),name)));
        if(DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)){if(!f.mkdir())throw new IOException("Cannot create session directory");}
        else if(!f.createNewFile())throw new IOException("Output already exists");
        return Uri.fromFile(f);
    }
    static OutputStream write(ContentResolver r,Uri u)throws IOException{
        return file(u)?new BufferedOutputStream(new FileOutputStream(outputFile(u)),65536):r.openOutputStream(u,"w");
    }
    static InputStream read(ContentResolver r,Uri u)throws IOException{
        return file(u)?new FileInputStream(outputFile(u)):r.openInputStream(u);
    }
    static String name(Uri u){return file(u)?new File(u.getPath()).getName():DocumentsContract.getDocumentId(u);}
    private StorageAccess(){}
}
