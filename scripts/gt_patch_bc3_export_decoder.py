"""Repair BC3 four-color mode in the pinned public exporter scratch checkout.

Observed actual DXT5 decoder incorrectly uses the BC1 three-color palette
for RGB565 c0 < c1. BC3 always uses four colors independently of alpha.
Normalize only the decoder's temporary RGB blocks, not source bytes:
swap endpoints and xor each 2-bit selector with 1. Equal endpoints collapse
all selectors to endpoint 0. Leave alpha, DXT1/DXT3/Crunch, and the original
source/mips untouched. No runtime or other format equivalence claimed.
"""
import argparse
import hashlib
import json
from pathlib import Path

PIN="f8cec77003d86fa3d6ad1a04002927733a1986a6"
PATH="Source/AssetRipper.Export.Modules.Textures/TextureConverter.cs"
ANCHOR=b"""\t\t\tcase TextureFormat.DXT5:
\t\t\tcase TextureFormat.DXT5Crunched:
\t\t\t\tDxtDecoder.DecompressDXT5<TColor, TChannelValue>(inputSpan, width, height, outputSpan);
\t\t\t\treturn true;"""
REPLACEMENT=b"""\t\t\tcase TextureFormat.DXT5:
\t\t\t\tlong topBytes = 16L * ((width + 3L) / 4) * ((height + 3L) / 4);
\t\t\t\tif (width <= 0 || height <= 0 || topBytes > inputSpan.Length)
\t\t\t\t\treturn false;
\t\t\t\tDxtDecoder.DecompressDXT5<TColor, TChannelValue>(
\t\t\t\t\tRaftNormalizeBC3ColorBlocks(inputSpan, (int)topBytes), width, height, outputSpan);
\t\t\t\treturn true;

\t\t\tcase TextureFormat.DXT5Crunched:
\t\t\t\tDxtDecoder.DecompressDXT5<TColor, TChannelValue>(inputSpan, width, height, outputSpan);
\t\t\t\treturn true;"""
METHOD_ANCHOR=b"\tprivate static bool TryDecodeTexture<TColor, TChannelValue>("
METHOD=b"""\t// BC3 RGB always has four colors, even when c0 <= c1.
\t// The pinned dependency uses a BC1 palette for that endpoint order.
\t// Canonicalize a private top-mip copy; do not mutate any input bytes.
\tprivate static ReadOnlySpan<byte> RaftNormalizeBC3ColorBlocks(ReadOnlySpan<byte> input, int topBytes)
\t{
\t\tbyte[]? normalized = null;
\t\tfor (int i = 0; i < topBytes; i += 16)
\t\t{
\t\t\tint c0 = input[i + 8] | (input[i + 9] << 8);
\t\t\tint c1 = input[i + 10] | (input[i + 11] << 8);
\t\t\tif (c0 > c1)
\t\t\t\tcontinue;
\t\t\tnormalized ??= input[..topBytes].ToArray();
\t\t\tif (c0 == c1)
\t\t\t{
\t\t\t\t// All four BC3 RGB entries are exactly the same endpoint.
\t\t\t\tArray.Clear(normalized, i + 12, 4);
\t\t\t}
\t\t\telse
\t\t\t{
\t\t\t\tnormalized[i + 8] = input[i + 10];
\t\t\t\tnormalized[i + 9] = input[i + 11];
\t\t\t\tnormalized[i + 10] = input[i + 8];
\t\t\t\tnormalized[i + 11] = input[i + 9];
\t\t\t\tfor (int j = 12; j < 16; j++)
\t\t\t\t\tnormalized[i + j] = (byte)(input[i + j] ^ 0x55);
\t\t\t}
\t\t}
\t\tif (normalized is null)
\t\t\treturn input;
\t\treturn normalized;
\t}

"""

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def repair(raw):
    if git_blob(raw)!=PIN:
        raise ValueError("pinned_BC3_TextureConverter_changed")
    if raw.count(ANCHOR)!=1 or raw.count(METHOD_ANCHOR)!=1:
        raise ValueError("ambiguous_BC3_patch_anchor")
    return raw.replace(ANCHOR,REPLACEMENT).replace(METHOD_ANCHOR,METHOD+METHOD_ANCHOR)

def patch(root):
    p=root/PATH
    raw=p.read_bytes();fixed=repair(raw)
    p.write_bytes(fixed)
    return {"status":"PATCHED_PINNED_DXT5_DECODER_ONLY","original_git_blob":git_blob(raw),
            "original_sha256":hashlib.sha256(raw).hexdigest(),"patched_sha256":hashlib.sha256(fixed).hexdigest(),
            "patch_script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source_asset_bytes_modified":False,"DXT1_DXT3_Crunched_changed":False}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--tool-source",type=Path,required=True)
    args=p.parse_args();print(json.dumps(patch(args.tool_source),sort_keys=True))
