#!/usr/bin/env python3
"""Audit selected original managed plugin assemblies without execution.

Names/counts only, never publish actual DLL bytes or private source. For
Unity Editor compatibility planning; not evidence of Android runtime support.
"""
import collections
from pathlib import Path
import dnfile

CANDIDATES=("FMODUnity.dll","FMODUnityResonance.dll","PlayFab.dll","PlayFab_o.dll",
            "Newtonsoft.Json.dll","com.rlabrecque.steamworks.net.dll",
            "Unity.Netcode.Runtime.dll","Unity.Netcode.Components.dll",
            "Unity.Networking.Transport.dll")
PATTERNS=("FMOD", "FMOD.Studio", "PlayFab.ClientModels","PlayFab.Json",
          "PlayFab.EventsModels","Steamworks","Unity.Netcode")
def table(pe,name):
    return list(getattr(getattr(pe.net.mdtables,name,None),"rows",None) or [])
def audit(root):
    for fn in CANDIDATES:
        path=root/fn
        if not path.is_file():
            print("candidate missing:",fn)
            continue
        pe=dnfile.dnPE(str(path))
        if not getattr(pe,"net",None):
            print("not managed:",fn);continue
        names=[str(getattr(t,"TypeNamespace",""))+"."+str(getattr(t,"TypeName","")) for t in table(pe,"TypeDef")]
        counts={p:sum(t.startswith(p+".") or t==p for t in names) for p in PATTERNS}
        refs=sorted(set(str(getattr(r,"Name","")) for r in table(pe,"AssemblyRef")))
        print("Managed assembly:",fn,"bytes:",path.stat().st_size,
              "types:",len(names),"found desired namespaces:",{k:v for k,v in counts.items() if v},
              "refs:",refs[:45])
if __name__=="__main__":
    audit(Path("Raft/Raft_Data/Managed"))
