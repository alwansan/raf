"""Stage a source-free OpenGLCore dispatch-address canary."""
import argparse
from pathlib import Path

from scripts.t1_sourcefree_unity_fixture import ASSET_FILE, ASSET_PATH, construct


_DISPATCH_COMPUTE = """// Authored dispatch-address control.
#pragma kernel T1Canary
StructuredBuffer<uint> Input;
RWStructuredBuffer<uint> Output;
static uint3 DispatchId;
uint AddressOffset;
float CarrierScale;

struct EntryInput
{
    uint3 thread : SV_DispatchThreadID;
};

uint ViaGlobal()
{
    return Input[DispatchId.x];
}

uint ViaArgument(uint x)
{
    return Input[x];
}

[numthreads(64,1,1)]
void T1Canary(EntryInput input)
{
    DispatchId = input.thread;
    uint x = input.thread.x;
    uint address = ((x << 2) + x + AddressOffset) & 63u;
    precise float subnormal = asfloat(address) * CarrierScale;
    precise float normal = asfloat(0x3f800000u | address) * CarrierScale;
    Output[6 * x] = ViaGlobal();
    Output[6 * x + 1] = ViaArgument(x);
    Output[6 * x + 2] = address;
    Output[6 * x + 3] = asuint(asfloat(address));
    Output[6 * x + 4] = asuint(subnormal);
    Output[6 * x + 5] = asuint(normal);
}
"""

_DISPATCH_ASSERTIONS = """        Assert.That(SystemInfo.graphicsDeviceType,
            Is.EqualTo(UnityEngine.Rendering.GraphicsDeviceType.OpenGLCore));
        var input = new uint[64];
        for (uint i = 0; i < 64; i++)
            input[i] = 17U + 13U * i;
        var output = new uint[384];
        using (var inputBuffer = new ComputeBuffer(input.Length, sizeof(uint)))
        using (var outputBuffer = new ComputeBuffer(output.Length, sizeof(uint)))
        {
            inputBuffer.SetData(input);
            outputBuffer.SetData(output);
            shader.SetBuffer(kernel, "Input", inputBuffer);
            shader.SetBuffer(kernel, "Output", outputBuffer);
            shader.SetInt("AddressOffset", 11);
            shader.SetFloat("CarrierScale", 1.0f);
            shader.Dispatch(kernel, 1, 1, 1);
            outputBuffer.GetData(output);
        }
        int viaGlobalMismatches = 0, viaArgumentMismatches = 0;
        int integerMismatches = 0, bitcastMismatches = 0, subnormalMismatches = 0, normalMismatches = 0;
        for (int i = 0; i < input.Length; i++)
        {
            uint address = (uint)((i * 5 + 11) & 63);
            int row = 6 * i;
            if (output[row] != input[i]) viaGlobalMismatches++;
            if (output[row + 1] != input[i]) viaArgumentMismatches++;
            if (output[row + 2] != address) integerMismatches++;
            if (output[row + 3] != address) bitcastMismatches++;
            if (output[row + 4] != address) subnormalMismatches++;
            if (output[row + 5] != (0x3f800000U | address)) normalMismatches++;
        }
        string report = System.IO.Path.Combine(
            System.IO.Directory.GetParent(Application.dataPath).FullName, "dispatch-address-counts.txt");
        System.IO.File.WriteAllLines(report, new[] {
            integerMismatches.ToString(), bitcastMismatches.ToString(),
            subnormalMismatches.ToString(), normalMismatches.ToString()
        });
        Assert.That(integerMismatches, Is.Zero, "Bound integer shift/add/mask");
        Assert.That(normalMismatches, Is.Zero, "Normal float multiply control");
        Assert.That(viaArgumentMismatches, Is.Zero, "Explicit argument address control");
        Assert.That(viaGlobalMismatches, Is.Zero, "Structured input via static global");
"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    project = parser.parse_args().project
    construct(project)
    test = project / ASSET_PATH / ASSET_FILE
    source = test.read_text(encoding="utf-8")
    skip = "        if (!compute)\n            return; // Linux -nographics may expose a null graphics device."
    assertion = "        Assert.That(z, Is.EqualTo(1U));\n"
    if source.count(skip) != 1 or source.count(assertion) != 1:
        raise ValueError("Unexpected source-free fixture structure")
    test.write_text(source.replace(skip, "        Assert.That(compute, Is.True);")
                    .replace(assertion, assertion + _DISPATCH_ASSERTIONS), encoding="utf-8")
    (project / "Assets/T1Synthetic/FFTCanary.compute").write_text(_DISPATCH_COMPUTE, encoding="utf-8")


if __name__ == "__main__":
    main()
