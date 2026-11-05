"""B43: fail-closed same-export Material keyword fidelity; no raw data in output."""
import argparse
import json
from pathlib import Path
import re
from scripts.verify_export_lineage import GUID, HEADER, document_key, identity, pointer
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS

FIELDS=("m_ValidKeywords","m_InvalidKeywords","disabledShaderPasses")
FIELD=re.compile(r"^  (m_ValidKeywords|m_InvalidKeywords|disabledShaderPasses):[ \t]*(.*)$")
NEXT=re.compile(r"^  [A-Za-z_][A-Za-z0-9_]*:")
ITEM=re.compile(r"^  (?:  )?-[ \t]+(.+?)[ \t]*$")
NAME=re.compile(r"^[A-Za-z0-9_./+:-]+$")
ENGINE={"0000000000000000e000000000000000","0000000000000000f000000000000000"}
FONT="AssetRipper.Export.UnityProjects.Miscellaneous.FontAssetExportCollection"

class GuardError(ValueError): pass

def scalar(s):
    s=s.strip()
    if s.startswith("'") and s.endswith("'"): s=s[1:-1].replace("''","'")
    elif s.startswith('"') and s.endswith('"'):
        try: s=json.loads(s)
        except ValueError as exc: raise GuardError("invalid_keyword_scalar") from exc
    if not isinstance(s,str) or not NAME.fullmatch(s): raise GuardError("unsupported_keyword_scalar")
    return s

def parse_fields(body):
    lines=body.splitlines()
    found={}
    for i,line in enumerate(lines):
        m=FIELD.fullmatch(line)
        if not m: continue
        key,inline=m.groups()
        if key in found: raise GuardError("duplicate_keyword_field")
        if inline:
            if inline.strip()!="[]": raise GuardError("unsupported_inline_keyword_list")
            found[key]=()
            continue
        items=[]
        for line in lines[i+1:]:
            if NEXT.match(line) or not line.strip(): break
            m=ITEM.fullmatch(line)
            if not m: raise GuardError("malformed_keyword_list")
            items.append(scalar(m[1]))
        if not items: raise GuardError("ambiguous_empty_keyword_field")
        found[key]=tuple(sorted(items))
    if set(found)!=set(FIELDS): raise GuardError("missing_keyword_fields")
    return tuple(found[k] for k in FIELDS)

def source_materials(root, *, selected_owners=None):
    """Full original B43 mode or explicitly SHA-allowed bounded source mode.

    Do not replace original payload authentication with a filename check.
    Reject arbitrary/empty scoped selections before loading optional UnityPy.
    """
    root=Path(root)
    if root.is_symlink(): raise GuardError("unsafe_original_root")
    if selected_owners is None:
        pins=SHADER_OWNERS
    else:
        from scripts.b05_verify_material_texenv_bindings import B05_SMALL_OWNER_PINS
        try:
            names=set(selected_owners)
        except TypeError:
            raise GuardError("unapproved_original_material_owner") from None
        if not names or not names.issubset(B05_SMALL_OWNER_PINS):
            raise GuardError("unapproved_original_material_owner")
        pins={name:B05_SMALL_OWNER_PINS[name] for name in sorted(names)}
    import UnityPy
    out={}
    for name,pin in pins.items():
        path=root/"Raft_Data"/name
        if path.is_symlink() or not path.is_file() or fingerprint(path)!=pin:
            raise GuardError("original_byte_pin_mismatch")
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name!="Material": continue
            key=(name,int(obj.path_id))
            if key in out: raise GuardError("duplicate_original_material")
            data=obj.read_typetree()
            if not all(k in data and isinstance(data[k],list) and
                       all(isinstance(v,str) for v in data[k]) for k in FIELDS):
                raise GuardError("unknown_original_keyword_schema")
            out[key]=tuple(tuple(sorted(data[k])) for k in FIELDS)
    if not out: raise GuardError("no_original_materials")
    return out

def exported_materials(project):
    assets=Path(project)/"Assets"
    if not assets.is_dir() or assets.is_symlink() or any(p.is_symlink() for p in assets.parents):
        raise GuardError("unsafe_export_root")
    paths=sorted(assets.rglob("*"))
    if any(p.is_symlink() for p in paths): raise GuardError("symlinked_export")
    out={}
    for path in paths:
        if not path.is_file() or path.suffix not in {".mat",".asset",".prefab",".unity"}: continue
        if path.stat().st_size>256*1024*1024: raise GuardError("oversized_export_yaml")
        with path.open("rb") as f:
            if not f.read(16).lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"): continue
        txt=path.read_text("utf-8-sig")
        heads=list(HEADER.finditer(txt))
        if not any(h[1]=="21" for h in heads): continue
        meta=Path(str(path)+".meta")
        if meta.is_symlink() or not meta.is_file(): raise GuardError("missing_export_meta")
        gids=GUID.findall(meta.read_text("utf-8-sig"))
        if len(gids)!=1: raise GuardError("ambiguous_export_guid")
        for i,h in enumerate(heads):
            if h[1]!="21": continue
            anchor=re.search(r"&(-?\d+)",h[0])
            if not anchor: raise GuardError("missing_material_anchor")
            key=(int(anchor[1]),gids[0].lower())
            if key in out: raise GuardError("duplicate_material_document")
            end=heads[i+1].start() if i+1<len(heads) else len(txt)
            out[key]=parse_fields(txt[h.end():end])
    if not out: raise GuardError("no_exported_materials")
    return out

def compare(trace,originals,exported):
    if (not isinstance(trace,dict) or trace.get("schema_version")!=1 or
        not isinstance(trace.get("export_instance"),str) or
        not re.fullmatch("[0-9a-f]{32}",trace["export_instance"]) or
        not isinstance(trace.get("objects"),list)):
        raise GuardError("invalid_same_instance_trace")
    seen,assign=set(),{}
    redirects=fonts=0
    for row in trace["objects"]:
        if not isinstance(row,dict) or row.get("class_id") not in (21,48):
            raise GuardError("malformed_trace_row")
        if row["class_id"]==48: continue
        src=identity(row["source"])
        if src in seen: raise GuardError("duplicate_trace_source")
        seen.add(src)
        if src not in originals:
            if row.get("collection_type")==FONT:
                fonts+=1
                continue
            raise GuardError("unknown_trace_material")
        dest=pointer(row["export"])
        if row.get("exportable") is False:
            if dest[1] not in ENGINE or dest[2]!="0":
                raise GuardError("unjustified_material_redirect")
            redirects+=1
            continue
        if row.get("collection_type")==FONT:
            fonts+=1
            continue
        key=document_key(dest)
        if key in assign: raise GuardError("duplicate_export_pointer")
        assign[key]=src
    if seen & set(originals)!=set(originals):
        raise GuardError("missing_original_in_trace")
    if set(assign)!=set(exported):
        raise GuardError("export_document_identity_mismatch")
    if any(originals[src]!=exported[key] for key,src in assign.items()):
        raise GuardError("keyword_or_disabled_pass_mismatch")
    return {"status":"MATCH","source_objects":len(originals),
            "export_documents":len(exported),"predefined_redirects":redirects,
            "implicit_font_exclusions":fonts,"keyword_state_equal":True,
            "shader_program_or_variant_equivalence_verified":False,
            "unity_or_device_verified":False,"ready_for_build":False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ("source","private-trace","project","out"): p.add_argument("--"+flag,required=True,type=Path)
    args=p.parse_args(argv)
    if args.out.resolve().is_relative_to(args.project.resolve()):
        raise SystemExit("Output must be outside project")
    try:
        result=compare(json.loads(args.private_trace.read_text("utf-8")),
                       source_materials(args.source),exported_materials(args.project))
    except Exception as e:
        result={"status":"REJECTED","error_code":str(e) if isinstance(e,GuardError) else "unsupported_input",
                "keyword_state_equal":False,"ready_for_build":False}
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n","utf-8")
    print("RAFT_B43_MATERIAL_KEYWORDS "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="MATCH" else 2

if __name__=="__main__": raise SystemExit(main())
