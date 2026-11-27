"""Windows-only authoring: compile new HLSL using system D3DCompiler_47."""
import ctypes as c
import hashlib
import json
import os
from pathlib import Path
import sys

SOURCES = {
    "vertex": ("vs_5_0", "float4 main(float4 p : POSITION) : SV_Position { return p; }\n"),
    "fragment_a": ("ps_5_0", "float4 main() : SV_Target { return float4(0.125, 0.25, 0.5, 1.0); }\n"),
    "fragment_b": ("ps_5_0", "float4 main() : SV_Target { return float4(0.75, 0.5, 0.25, 1.0); }\n"),
}

def sha(b): return hashlib.sha256(b).hexdigest()

def blob_bytes(ptr):
    table = c.cast(ptr, c.POINTER(c.POINTER(c.c_void_p))).contents
    get_ptr = c.WINFUNCTYPE(c.c_void_p,c.c_void_p)(table[3])
    get_size = c.WINFUNCTYPE(c.c_size_t,c.c_void_p)(table[4])
    release = c.WINFUNCTYPE(c.c_ulong,c.c_void_p)(table[2])
    try:
        return c.string_at(get_ptr(ptr),get_size(ptr))
    finally:
        release(ptr)

def main():
    out=Path(sys.argv[1]); out.mkdir()
    dll=Path(os.environ["SystemRoot"])/"System32"/"d3dcompiler_47.dll"
    d3d=c.WinDLL(str(dll))
    compile=d3d.D3DCompile
    compile.argtypes=[c.c_void_p,c.c_size_t,c.c_char_p,c.c_void_p,c.c_void_p,
                      c.c_char_p,c.c_char_p,c.c_uint,c.c_uint,
                      c.POINTER(c.c_void_p),c.POINTER(c.c_void_p)]
    compile.restype=c.c_long
    report={"compiler":"Windows system D3DCompile", "dll_sha256":sha(dll.read_bytes()),
            "flags1":0,"flags2":0,"programs":{}}
    for name,(profile,source) in SOURCES.items():
        raw=source.encode("ascii")
        buf=c.create_string_buffer(raw)
        code,error=c.c_void_p(),c.c_void_p()
        result=compile(buf,len(raw),(name+".hlsl").encode(),None,None,b"main",
                       profile.encode(),0,0,c.byref(code),c.byref(error))
        messages=blob_bytes(error) if error.value else b""
        if result!=0 or not code.value:
            raise RuntimeError("authored D3DCompile failed: "+messages.decode(errors="replace"))
        data=blob_bytes(code)
        assert data.startswith(b"DXBC")
        (out/(name+".hlsl")).write_bytes(raw)
        (out/(name+".dxbc")).write_bytes(data)
        report["programs"][name]={"profile":profile,"source_sha256":sha(raw),
                                   "dxbc_sha256":sha(data),"dxbc_bytes":len(data)}
    (out/"fixture.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("AUTHORED_DXBC_COMPILED",len(report["programs"]))

if __name__=="__main__":
    main()
