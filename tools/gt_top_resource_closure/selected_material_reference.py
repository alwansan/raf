"""Source-bound isolated Material pointer differential; never an original shader draw."""
import re
from scripts import gt_particle108_local_texture_document as native
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs

SHADER_GUID="784438f4bc7c4d82bd487c26472c7925"
WRONG_GUID="f2d4b6fe6ed24464b7f440bcd315292e"
CASES=("type3","type2","wrong_guid","wrong_fileid")

def require(ok):
    if not ok: raise ValueError("selected_material_reference_diagnostic_anchor")

def make_variants(body,prop,guid,fid,kind):
    require(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}",prop) is not None)
    require(re.fullmatch(r"[0-9a-f]{32}",guid) is not None and guid not in (SHADER_GUID,WRONG_GUID))
    require(fid==18700000 and kind==3)
    parsed=native.strict_mapping(body)
    original=parsed["Material"]
    props=original["m_SavedProperties"]["m_TexEnvs"]
    before=normalize_texenvs(props,exported=True)
    require(prop in before and before[prop][0]==(fid,guid,kind))
    # Substitute only the original shader pointer for a diagnostic 2DArray
    # declaration with the exact saved property name. Never claim its code
    # or the other five original slots were exercised in this diagnostic.
    shader_pattern=r"(?m)^(  m_Shader: )\{fileID: 4800000, guid: [0-9a-f]{32}, type: 3\}([ \t]*)$"
    require(len(re.findall(shader_pattern,body))==1)
    base=re.sub(shader_pattern,lambda m:m[1]+"{fileID: 4800000, guid: "+SHADER_GUID+", type: 3}"+m[2],body)
    ptr_pattern=r"(?m)^(\s*m_Texture: )\{fileID: 18700000, guid: "+guid+r", type: 3\}([ \t]*)$"
    require(len(re.findall(ptr_pattern,base))==1)
    cases={"type3":(fid,guid,3),"type2":(fid,guid,2),"wrong_guid":(fid,WRONG_GUID,2),"wrong_fileid":(fid+1,guid,2)}
    results={}
    for case,(f,g,k) in cases.items():
        value=re.sub(ptr_pattern,lambda m:m[1]+f"{{fileID: {f}, guid: {g}, type: {k}}}"+m[2],base)
        candidate=native.strict_mapping(value)["Material"]
        after=normalize_texenvs(candidate["m_SavedProperties"]["m_TexEnvs"],exported=True)
        expected=dict(before);expected[prop]=((f,g,k),before[prop][1])
        require(after==expected)
        # Compare full parsed documents after reversing just the intended
        # pointer and diagnostic shader differences.
        restored=re.sub(r"(?m)^(\s*m_Texture: )\{fileID: "+str(f)+r", guid: "+g+r", type: "+str(k)+r"\}([ \t]*)$",
                        lambda m:m[1]+f"{{fileID: {fid}, guid: {guid}, type: 3}}"+m[2],value)
        restored_doc=native.strict_mapping(restored)["Material"]
        restored_doc["m_Shader"]=original["m_Shader"]
        require(restored_doc==original)
        results[case]=value
    require(sum(x!=y for x,y in zip(results["type3"],results["type2"],strict=True))==1)
    return results

def stage(root,cfg,body,prop,guid,fid,kind,material_fid):
    from tools.gt_top_resource_closure.selected_array_native import sha
    require(material_fid==2100000)
    variants=make_variants(body,prop,guid,fid,kind)
    head="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &"+str(material_fid)
    cfg["material_property"]=prop
    cfg["material_variant_hashes"]=[]
    cfg["reference_shader_guid"]=SHADER_GUID
    cfg["reference_wrong_guid"]=WRONG_GUID
    for name in CASES:
        raw=(head+variants[name]).encode()
        (root/("material-"+name+".bytes")).write_bytes(raw)
        cfg["material_variant_hashes"].append(sha(raw))
    shader=('Shader "Hidden/GTSelectedPointer" { Properties { '+prop+' ("GT", 2DArray) = "" {} } SubShader { Pass {} } }\n').encode()
    (root/"material-probe-shader.bytes").write_bytes(shader)
    cfg["material_shader_hash"]=sha(shader)
