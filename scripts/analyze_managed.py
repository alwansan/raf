#!/usr/bin/env python3
"""Static-only .NET/Mono metadata audit of Raft: no assembly execution or source export."""
import collections
import json
from pathlib import Path
import sys

import dnfile

FEATURES = {
    "player": ("player", "movement", "swim", "jump", "character", "controller"),
    "raft": ("raft", "sail", "anchor", "engine", "paddle", "steering", "foundation"),
    "ocean": ("ocean", "water", "wave", "weather", "buoyancy", "current"),
    "world_islands": ("world", "island", "terrain", "biome", "spawn", "procedural"),
    "survival": ("hunger", "thirst", "oxygen", "health", "damage", "status"),
    "items_crafting": ("inventory", "item", "craft", "recipe", "equipment", "pickup", "storage"),
    "building": ("build", "construct", "placement", "structure", "repair"),
    "ai_entities": ("shark", "animal", "ai", "enemy", "npc", "boss"),
    "multiplayer": ("network", "steam", "multiplayer", "lobby", "remote", "client", "server", "host", "rpc", "session"),
    "save_loading": ("save", "load", "serialize", "worlddata", "persist"),
    "ui_input": ("input", "ui", "menu", "hud", "keybind", "cursor", "mouse"),
    "audio": ("audio", "sound", "music", "fmod"),
    "platform": ("steam", "playfab", "party", "purchasing", "achievement", "auth"),
}

def table_rows(metadata, name):
    table = getattr(metadata, name, None)
    return list(getattr(table, "rows", None) or [])


def name(x):
    return str(x or "")


def analyze(path):
    pe = dnfile.dnPE(str(path))
    if not getattr(pe, "net", None) or not getattr(pe.net, "mdtables", None):
        raise ValueError("not a parseable managed .NET assembly")
    md = pe.net.mdtables
    types = []
    for row in table_rows(md, "TypeDef"):
        full = ".".join(filter(None, [name(getattr(row, "TypeNamespace", "")), name(getattr(row, "TypeName", ""))]))
        if full and full != "<Module>":
            types.append(full)
    counts = {}
    hits = {}
    for feature, needles in FEATURES.items():
        matches = sorted({t for t in types if any(s in t.lower() for s in needles)})
        counts[feature] = len(matches)
        hits[feature] = matches[:32]
    namespaces = collections.Counter(t.rsplit(".", 1)[0] if "." in t else "<global>" for t in types)
    refs = []
    for row in table_rows(md, "AssemblyRef"):
        refs.append(name(getattr(row, "Name", "")))
    modules = [name(getattr(row, "Name", "")) for row in table_rows(md, "ModuleRef")]
    pinvokes = []
    for row in table_rows(md, "ImplMap"):
        scope = getattr(row, "ImportScope", None)
        target = getattr(scope, "row", None) if scope is not None else None
        pinvokes.append({"name": name(getattr(row, "ImportName", "")),
                         "module": name(getattr(target, "Name", ""))})
    return {
        "file": str(path),
        "managed": True,
        "type_count": len(types),
        "method_count": len(table_rows(md, "MethodDef")),
        "field_count": len(table_rows(md, "Field")),
        "assembly_references": sorted(set(refs)),
        "native_module_references": sorted(set(modules)),
        "pinvoke_declarations": pinvokes[:150],
        "pinvoke_count": len(pinvokes),
        "namespace_counts_top_50": namespaces.most_common(50),
        "feature_keyword_matches": counts,
        "feature_class_samples": hits,
        "caveat": "Class names are search hints, not proof of functionality or Android compatibility.",
    }


def main():
    path = Path("Raft/Raft_Data/Managed/Assembly-CSharp.dll")
    if not path.exists():
        raise FileNotFoundError(path)
    report = analyze(path)
    out = Path("out/managed-analysis.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("assembly:", report["file"], "| types:", report["type_count"],
          "| methods:", report["method_count"], "| fields:", report["field_count"])
    print("Assembly references:", ", ".join(report["assembly_references"]))
    print("Native module references:", ", ".join(report["native_module_references"]))
    print("P/Invoke declarations:", report["pinvoke_count"])
    print("Feature matches:", report["feature_keyword_matches"])
    print("Network class samples:", report["feature_class_samples"]["multiplayer"][:28])
    print("Raft class samples:", report["feature_class_samples"]["raft"][:20])
    print("Save class samples:", report["feature_class_samples"]["save_loading"][:20])
    print("Native imports by module:", dict(collections.Counter(item["module"] for item in report["pinvoke_declarations"])))
    print("Report:", out)


if __name__ == "__main__":
    sys.exit(main())
