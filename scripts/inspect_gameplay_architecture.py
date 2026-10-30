#!/usr/bin/env python3
"""Inventory Mono symbols for architecture research. Never loads or executes DLL code."""
from pathlib import Path
import json
import re
import collections
import sys
import dnfile

PATH=Path("Raft/Raft_Data/Managed/Assembly-CSharp.dll")
OUT=Path("out/gameplay-symbol-map.json")
PATTERNS={
    "network": re.compile(r"network|multiplayer|lobby|steam|party|host|remote|client|session",re.I),
    "save": re.compile(r"save|load|persist|worlddata|serializer|backup|restore",re.I),
    "raft": re.compile(r"raft|anchor|sail|engine|steering|foundation|block_",re.I),
    "input": re.compile(r"input|keybind|control|cursor|playercontroller",re.I),
    "platform": re.compile(r"steam|playfab|xbox|party|auth|purchasing|achievement",re.I),
    "ocean": re.compile(r"ocean|water|wave|buoyancy|shark",re.I),
}
INTERESTING=re.compile(r"Network|Steam|Party|Save|World|Player|Raft|GameManager|MainMenu|Offline",re.I)
def s(x): return str(x or "")
def owned_methods(row):
    """dnfile TypeDef.MethodList contains indexing objects when metadata is healthy."""
    refs=getattr(row,"MethodList",None) or []
    names=[]
    for ref in refs:
        try:
            m=ref.row
        except Exception:
            m=None
        if m:
            names.append(s(getattr(m,"Name","")))
    return names

def main():
    if not PATH.is_file(): raise FileNotFoundError(PATH)
    pe=dnfile.dnPE(str(PATH))
    md=pe.net.mdtables
    rows=list(md.TypeDef.rows or [])
    catalog=[]
    for row in rows:
        n=s(getattr(row,"TypeName",""))
        ns=s(getattr(row,"TypeNamespace",""))
        if not n or n=="<Module>": continue
        name=f"{ns}.{n}" if ns else n
        methods=owned_methods(row)
        catalog.append({"type":name,"methods":methods})
    domains={}
    for cat,rx in PATTERNS.items():
        picked=[x for x in catalog if rx.search(x["type"])]
        # Prefer direct named classes; compiler-generated iterator classes are separately counted
        normal=[x for x in picked if not x["type"].split(".")[-1].startswith("<")]
        domains[cat]={
            "type_matches":len(picked),
            "nongenerated_type_matches":len(normal),
            "non_generated_examples":[{"name":x["type"],"method_count":len(x["methods"])}
                for x in normal[:80]]
        }
    key_types=[
        x for x in catalog
        if INTERESTING.search(x["type"])
           and not x["type"].split(".")[-1].startswith("<")
    ]
    # Return only shallow structural facts, not decompiled code.
    report={
        "input":str(PATH),
        "type_count":len(catalog),
        "typed_method_count":sum(len(x["methods"]) for x in catalog),
        "domains":domains,
        "focus_types":[{"name":x["type"],"method_names":x["methods"][:35],
                        "method_count":len(x["methods"])} for x in key_types[:250]],
        "comment":"Class/method names are metadata. These are not traced IL call sites."
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("Total type count:",report["type_count"])
    print("Assigned method definitions:",report["typed_method_count"])
    print("Per-domain matches:",{k:(v["type_matches"],v["nongenerated_type_matches"])
                                 for k,v in domains.items()})
    for term in ("network","save","platform","raft"):
        names=[v["name"] for v in domains[term]["non_generated_examples"]]
        print("Focus type candidates",term,":",names[:50])
    for target in ("Network","NetworkManager","Raft_Network","SaveAndLoad",
                   "SteamManager","GameManager","SaveWorld"):
        matches=[x for x in report["focus_types"] if x["name"].split(".")[-1].lower()==target.lower()]
        for x in matches: print("Exact named",target,":",x)
    print("Structured symbol map retained only on ephemeral runner:",OUT)
if __name__=="__main__":
    sys.exit(main())
