package com.alwansan.gfxlab;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.provider.MediaStore;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Android 10+ scoped-storage ZIP export via MediaStore.Downloads.
 * No root, no MANAGE_EXTERNAL_STORAGE permission, no broad storage access.
 * The MediaStore row is pending until the complete ZIP is flushed and verified.
 */
public final class GfxDownloadsBridge {
    private static final String DESTINATION = "Download/Games/cl/test/g/";

    private GfxDownloadsBridge() {}

    public static String exportZip(Activity activity, String sourcePath, String outputName)
            throws IOException {
        if (activity == null) throw new IOException("ANDROID_ACTIVITY_MISSING");
        if (Build.VERSION.SDK_INT < 29)
            throw new IOException("MEDIASTORE_DOWNLOADS_REQUIRES_ANDROID_API29");
        if (sourcePath == null || outputName == null || !outputName.matches("[A-Za-z0-9_.-]+\\.zip"))
            throw new IOException("INVALID_EXPORT_ZIP_FILENAME");
        File source = new File(sourcePath);
        if (!source.isFile() || source.length() == 0L)
            throw new IOException("PRIVATE_ZIP_FILE_NOT_FOUND");

        ContentResolver resolver = activity.getContentResolver();
        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, outputName);
        values.put(MediaStore.MediaColumns.MIME_TYPE, "application/zip");
        values.put(MediaStore.MediaColumns.RELATIVE_PATH, DESTINATION);
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);

        Uri uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
        if (uri == null) throw new IOException("MEDIASTORE_INSERT_RETURNED_NULL");
        boolean committed = false;
        try {
            try (InputStream input = new FileInputStream(source);
                 OutputStream output = resolver.openOutputStream(uri, "w")) {
                if (output == null) throw new IOException("MEDIASTORE_OUTPUT_STREAM_NULL");
                byte[] buffer = new byte[64 * 1024];
                int read;
                while ((read = input.read(buffer)) >= 0) {
                    if (read > 0) output.write(buffer, 0, read);
                }
                output.flush();
            }
            values.clear();
            values.put(MediaStore.MediaColumns.IS_PENDING, 0);
            if (resolver.update(uri, values, null, null) < 1)
                throw new IOException("MEDIASTORE_PUBLISH_PENDING_FAILED");

            // Fail closed if the ROM moved the file to an unexpected directory
            // or truncated the content. Never claim the user-requested path on
            // insert+write success alone.
            String actualPath = null;
            long size = -1L;
            try (Cursor cursor = resolver.query(uri,
                    new String[] { MediaStore.MediaColumns.RELATIVE_PATH,
                                   MediaStore.MediaColumns.SIZE }, null, null, null)) {
                if (cursor == null || !cursor.moveToFirst())
                    throw new IOException("MEDIASTORE_DESTINATION_VERIFICATION_FAILED");
                actualPath = cursor.getString(0);
                size = cursor.getLong(1);
            }
            if (actualPath == null ||
                !DESTINATION.equals(actualPath.endsWith("/") ? actualPath : actualPath + "/"))
                throw new IOException("MEDIASTORE_WRONG_TARGET_PATH:" + actualPath);
            if (size != source.length())
                throw new IOException("MEDIASTORE_EXPORTED_ZIP_TRUNCATED");
            committed = true;
            return uri.toString();
        } finally {
            if (!committed) {
                try { resolver.delete(uri, null, null); }
                catch (RuntimeException ignored) {}
            }
        }
    }
}
