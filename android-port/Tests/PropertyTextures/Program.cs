using System;
using System.IO;
using RaftAndroid.Editor;

public static class Program
{
    private static int passed;
    private static void Reject(Action action)
    {
        try { action(); }
        catch (InvalidDataException) { passed++; return; }
        throw new Exception("Unsafe property table accepted.");
    }

    public static void Main()
    {
        var values = new float[32 * 32 * 4];
        values[0] = -3.25f; values[1] = 4000.5f; values[2] = 0.000001f; values[3] = -0.0f;
        byte[] raw = PropertyTextureCore.Encode(32, values);
        if (raw.Length != values.Length * 4 || BitConverter.ToSingle(raw, 0) != -3.25f ||
            BitConverter.ToSingle(raw, 4) != 4000.5f || BitConverter.ToSingle(raw, 8) != 0.000001f)
            throw new Exception("Original out-of-range/fractional float values were altered.");
        passed++;
        if (values[1] != 4000.5f) throw new Exception("Source array was modified.");
        passed++;
        PropertyTextureCore.RequireEqual(raw, (byte[])raw.Clone()); passed++;
        var corrupt = (byte[])raw.Clone(); corrupt[3] ^= 1;
        Reject(() => PropertyTextureCore.RequireEqual(raw, corrupt));
        Reject(() => PropertyTextureCore.RequireEqual(raw, new byte[1]));
        Reject(() => PropertyTextureCore.Encode(0, values));
        Reject(() => PropertyTextureCore.Encode(257, values));
        Reject(() => PropertyTextureCore.Encode(32, new float[512]));
        Reject(() => PropertyTextureCore.Encode(32, null));
        values[2] = float.NaN; Reject(() => PropertyTextureCore.Encode(32, values));
        values[2] = float.PositiveInfinity; Reject(() => PropertyTextureCore.Encode(32, values));
        values[2] = float.NegativeInfinity; Reject(() => PropertyTextureCore.Encode(32, values));
        if (PropertyTextureCore.Encode(256, new float[256 * 32 * 4]).Length != 131072)
            throw new Exception("Larger original table lost dimensions.");
        passed++;
        Console.WriteLine("Property texture data safety: " + passed + " checks passed (not Unity GPU validation).");
    }
}
