"""CPU-only audit of authenticated Dx11FFT integer lookup storage; no shader export."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def inspect(path):
    raw=Path(path).read_text(encoding="utf-8-sig").replace("\r\n","\n")
    if hashlib.sha256(raw.encode()).hexdigest()!="8aa32937d4235f0f1ae0a180b8099fd647558689ad65208a9f37956c69e90fb0":
        raise ValueError("Unknown original Dx11FFT source")
    rows=[]
    for n in (32,64,128,256,512,1024,2048):
        changed=sum(struct.unpack("<e",struct.pack("<e",float(i)))[0]!=i for i in range(2*n))
        if changed != (1024 if n==2048 else 0):
            raise AssertionError("Integer binary16 precision control failed")
        rows.append({"resolution":n,"integer_entries":2*n,"changed_binary16_entries":changed})
    return {"rows":rows,"actual_gpu_or_texture_format_verified":False,
            "normalized_coordinate_model_applicable_to_this_integer_table":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    print(json.dumps(inspect(p.parse_args().source),sort_keys=True))
