"""Read-only identity coverage counts; never rename or substitute shaders."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path
PIN="5cb0f9c4d022d6054d179778b9b50a0301d6748eaf4abdedd21c93f0c30b10c5"
HEADER=re.compile(r'^\s*Shader\s+"([^"\r\n]+)"',re.M)
def inspect(root, archive):
    raw=Path(archive).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PIN: raise ValueError("Unknown vendor archive")
    vendor=set()
    with zipfile.ZipFile(archive) as z:
        for p in z.namelist():
            if p.endswith(".shader") and p.startswith(("DefaultResources/","DefaultResourcesExtra/")):
                m=HEADER.search(z.read(p).decode("utf-8-sig"))
                if m: vendor.add(m[1])
    if len(vendor)!=198: raise ValueError("Vendor identity count mismatch")
    counts=dict(files=0,empty=0,parseable=0,exact_vendor_matches=0,nonvendor=0)
    digest=hashlib.sha256()
    for p in sorted(Path(root).rglob("*.shader")):
        if p.is_symlink(): raise ValueError("Symlink shader")
        b=p.read_bytes();digest.update(hashlib.sha256(b).digest())
        counts["files"]+=1;counts["empty"]+=not b
        m=HEADER.search(b.decode("utf-8-sig",errors="replace"))
        if m:
            counts["parseable"]+=1
            counts["exact_vendor_matches"]+=m[1] in vendor
            counts["nonvendor"]+=m[1] not in vendor
    if not counts["files"]: raise ValueError("Empty shader inventory")
    return dict(counts=counts,vendor_identity_count=198,ordered_content_digest=digest.hexdigest(),
      lexical_header_counts_only=True,original_game_identity_authenticated=False,
      full_export_scope_verified=False,shader_names_or_sources_disclosed=False,source_modified=False)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--archive",required=True)
    a=p.parse_args();print(json.dumps(inspect(a.source,a.archive),sort_keys=True))
