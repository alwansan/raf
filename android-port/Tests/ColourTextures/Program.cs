using System;
using RaftAndroid.Editor;

class Program
{
    static int checks;
    static void Expect(bool want, bool actual, string label)
    {
        checks++;
        if (want != actual) throw new Exception(label);
    }
    static void Main()
    {
        foreach (string format in new[] { "RGB24", "RGBA32", "ARGB32" })
        foreach (string extension in new[] { ".png", ".PNG", ".jpg", ".jpeg", ".tga", ".bmp" })
            Expect(true, AndroidColourTexturePolicy.ShouldCompress(true,true,false,false,extension,format),
                   "Uncompressed colour must retain dimensions but receive Android GPU compression");
        foreach (string format in new[] { "Automatic", "ASTC_4x4", "ASTC_6x6", "DXT1", "ETC2_RGBA8", "R8", "RGBAHalf", "", null })
            Expect(false, AndroidColourTexturePolicy.ShouldCompress(true,true,false,false,".png",format),
                   "Preserve already compressed, data, HDR and unknown formats");
        foreach (string extension in new[] { ".exr", ".hdr", ".asset", ".dds", "", null })
            Expect(false, AndroidColourTexturePolicy.ShouldCompress(true,true,false,false,extension,"RGBA32"),
                   "Unsupported source precision/identity must remain unchanged");
        Expect(false, AndroidColourTexturePolicy.ShouldCompress(false,true,false,false,".png","RGBA32"), "Special importer");
        Expect(false, AndroidColourTexturePolicy.ShouldCompress(true,false,false,false,".png","RGBA32"), "Linear data map");
        Expect(false, AndroidColourTexturePolicy.ShouldCompress(true,true,true,false,".png","RGBA32"), "Original Android override");
        Expect(false, AndroidColourTexturePolicy.ShouldCompress(true,true,false,true,".png","RGBA32"), "Font atlas dependency");
        Console.WriteLine("RAFT_COLOUR_TEXTURE_POLICY checks=" + checks + " actualUnityGPUImportVerified=false");
    }
}
