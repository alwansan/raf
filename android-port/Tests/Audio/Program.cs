using System;
using System.Collections.Generic;
using RaftAndroid.Audio;

class Program
{
    static int checks;
    static void Require(bool condition) { if (!condition) throw new Exception("Audio policy case failed: " + checks); checks++; }
    static void Main()
    {
        var calls = new List<string>();
        var startup = new FmodAndroidStartup();
        Action load = () => calls.Add("load");
        Action java = () => calls.Add("java");
        Func<uint> version = () => { calls.Add("version"); return FmodAndroidStartup.ExpectedVersion; };
        startup.Initialize(load, java, version);
        Require(string.Join(",", calls) == "load,java,version");
        Require(startup.Initialized);
        startup.Initialize(load, java, version);
        Require(calls.Count == 3);
        for (int failing = 0; failing < 3; failing++)
        {
            int stage = failing;
            calls.Clear();
            startup = new FmodAndroidStartup();
            try
            {
                startup.Initialize(() => { calls.Add("load"); if (stage == 0) throw new Exception(); },
                    () => { calls.Add("java"); if (stage == 1) throw new Exception(); },
                    () => { calls.Add("version"); throw new Exception(); });
                throw new Exception("Failure was swallowed");
            }
            catch (Exception) { Require(!startup.Initialized); Require(calls.Count == stage + 1); }
        }
        foreach (uint wrong in new uint[] { 0, 0x00020214, 0x00020221, 0x00020300 })
        {
            startup = new FmodAndroidStartup();
            bool rejected = false;
            try { startup.Initialize(() => {}, () => {}, () => wrong); }
            catch (InvalidOperationException) { rejected = true; }
            Require(rejected && !startup.Initialized);
        }
        startup = new FmodAndroidStartup();
        bool missingRejected = false;
        try { startup.Initialize(null, java, version); }
        catch (ArgumentNullException) { missingRejected = true; }
        Require(missingRejected && !startup.Initialized);
        Console.WriteLine("RAFT_FMOD_STARTUP_POLICY checks=" + checks + " passed=true actualUnityDeviceExecution=false");
    }
}
