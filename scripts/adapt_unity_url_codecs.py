#!/usr/bin/env python3
"""Map recovered single-string URL form codecs to Unity's .NET Standard API.
Only changes the two original HttpUtility codec call forms in Raft_Network.
Never changes scene assets, source metadata, transport or save behavior.
"""
import argparse
from pathlib import Path
import re

CALL=re.compile(r"(?<![\w.])HttpUtility\.(UrlEncode|UrlDecode)\s*\(")

def repair(project: Path, *, apply: bool) -> dict:
    source=project/"Assets/Scripts/Assembly-CSharp/Raft_Network.cs"
    text=source.read_text(encoding="utf8")
    updated,count=CALL.subn(lambda m: "System.Net.WebUtility."+m.group(1)+"(",text)
    if re.search(r"\bHttpUtility\s*\.",updated):
        raise ValueError("Unrecognized HttpUtility call; inspect original overload before adapting")
    if not count and "System.Net.WebUtility." not in text:
        raise ValueError("Expected original or already adapted URL codec calls")
    if apply and count:
        source.write_text(updated,encoding="utf8")
    result={"url_codec_calls_adapted":count,"applied":apply}
    print("Unity URL codec compatibility:",result)
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--project",required=True,type=Path)
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    repair(args.project,apply=args.apply)
