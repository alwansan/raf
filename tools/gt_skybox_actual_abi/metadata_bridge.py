"""Private Unity metadata to decoded descriptor/member bridge; aggregate evidence only.

Direct descriptor index joins are observations, not a declaration of Unity's
undocumented packing. Alternate packed-index views are diagnostic only.
"""
import struct
from collections import Counter

def require(ok,reason):
    if not ok:raise ValueError(reason)

KINDS=("ubos","separate_images","separate_samplers","textures","images","ssbos",
       "storage_images","subpass_inputs","acceleration_structures")
VIEWS={"direct":lambda n:n,"low8":lambda n:n&255,"low16":lambda n:n&65535,
       "high8":lambda n:(n>>8)&255,"high16":lambda n:(n>>16)&65535}

def debug_op_counts(data):
    require(len(data)>=20 and len(data)%4==0 and data[:4]==b"\x03\x02\x23\x07","spirv_header")
    words=struct.unpack("<"+"I"*(len(data)//4),data)
    i=5;counts=Counter()
    while i<len(words):
        width,op=divmod(words[i],1<<16)
        require(width>0 and i+width<=len(words),"spirv_instruction")
        if op in (5,6):counts[op]+=1
        i+=width
    return {"op_name":counts[5],"op_member_name":counts[6]}

def member_shape(m):
    return (m.get("type"),tuple(m.get("array",[])),m.get("array_stride"),
            m.get("matrix_stride"),bool(m.get("row_major",False)))

def reflected_slots(ref):
    result=[]
    seen=set()
    for kind in KINDS:
        for r in ref.get(kind,[]):
            coord=(r.get("set"),r.get("binding"))
            require(all(type(x) is int and x>=0 for x in coord),"invalid_descriptor_coordinate")
            require(coord not in seen,"duplicate_descriptor_coordinate")
            seen.add(coord)
            row={"kind":kind,"set":coord[0],"binding":coord[1],"type":r.get("type"),
                 "array":tuple(r.get("array",[]))}
            if kind=="ubos":
                row["members"]=ref["types"][r["type"]]["members"]
                row["block_size"]=r.get("block_size")
            result.append(row)
    return result

def full_metadata(program,row,entries,names):
    from scripts.a12_shader_parameter_decode import parse_parameter_blob
    common=program.get("m_CommonParameters")
    require(type(common) is dict,"common_parameter_schema")
    groups={};buffers={};textures={};explicit_samplers={}
    def group(owner,size=None):
        g=groups.setdefault(owner,{"size":None,"members":{}})
        if size is not None:
            require(g["size"] is None or g["size"]==size,"metadata_group_size_conflict")
            g["size"]=size
        return g
    def member(owner,name,offset):
        g=group(owner)
        require(name not in g["members"],"duplicate_member")
        require(type(offset) is int and offset>=0,"member_offset")
        g["members"][name]=offset
    def binding(target,name,value):
        require(name not in target,"duplicate_binding")
        require(type(value) is int and value>=0,"invalid_binding")
        target[name]=value
    for b in common.get("m_ConstantBuffers",[]):
        owner=names[b["m_NameIndex"]];group(owner,b.get("m_Size"))
        for key in ("m_VectorParams","m_MatrixParams","m_StructParams"):
            for m in b.get(key,[]):member(owner,names[m["m_NameIndex"]],m["m_Index"])
    for b in common.get("m_ConstantBufferBindings",[]):
        binding(buffers,names[b["m_NameIndex"]],b["m_Index"])
    for t in common.get("m_TextureParams",[]):
        name=names[t["m_NameIndex"]]
        require(name not in textures,"duplicate_texture")
        textures[name]=(t["m_Index"],t["m_SamplerIndex"])
    bucket,ordinal,_=row
    indices=program.get("m_ParameterBlobIndices",[])
    variant=False
    if indices and bucket is not None:
        idx=indices[bucket][ordinal]
        require(type(idx) is int and 0<=idx<len(entries),"parameter_index")
        layout={}
        parse_parameter_blob(entries[idx][1],private_layout=layout)
        variant=True
        for g in layout["groups"]:
            group(g["name"],g["used_size"])
            for m in g["members"]+g["structs"]:member(g["name"],m["name"],m["index"])
        for r in layout["resources"]:
            name=r["name"];n=r["index"]
            if r["kind"]==0:
                pair=(n,r["extra_value"])
                require(name not in textures or textures[name]==pair,"texture_metadata_conflict")
                textures[name]=pair
            elif r["kind"]==1:
                require(name not in buffers or buffers[name]==n,"buffer_metadata_conflict")
                buffers[name]=n
            elif r["kind"]==4:
                require(name not in explicit_samplers or explicit_samplers[name]==n,"sampler_metadata_conflict")
                explicit_samplers[name]=n
    return {"groups":groups,"buffers":buffers,"textures":textures,
            "explicit_samplers":explicit_samplers,"variant":variant}

def unique_slots(slots,kind,index,view):
    if type(index) is not int or index<0:return []
    n=VIEWS[view](index)
    return [r for r in slots if r["kind"]==kind and r["binding"]==n]

def source_member_records(layouts,stage,static_ref):
    from tools.gt_skybox_offset_differential import audit as d
    refs={}
    for u in static_ref.get("ubos",[]):
        owner=u["name"]
        for m in static_ref["types"][u["type"]]["members"]:
            k=(owner,m["name"])
            require(k not in refs,"duplicate_source_member")
            refs[k]=m
    result=[]
    for b in layouts:
        owner=d.source_buffer_name(b,stage)
        for m in b["members"]+b["structs"]:
            key=(owner,m["name"])
            require(key in refs and refs[key]["offset"]==m["index"],"source_member_reference")
            result.append((b["name"],owner,m["name"],m["index"],member_shape(refs[key])))
    return result

def member_join(expected,metadata,slots,view):
    """Never match unnamed SPIR-V by name-only, ordinal-only or nearest offset."""
    counts=Counter()
    candidates={}
    for old_owner,alias,name,source_offset,shape in expected:
        counts["expected"]+=1
        named=[(owner,g["members"][name]) for owner,g in metadata["groups"].items() if name in g["members"]]
        if not named:
            counts["missing_serialized_name"]+=1;continue
        counts["serialized_name_present"]+=1
        matches=[]
        for owner,offset in named:
            if owner not in metadata["buffers"]:continue
            for slot in unique_slots(slots,"ubos",metadata["buffers"][owner],view):
                for m in slot["members"]:
                    if m["offset"]==offset and member_shape(m)==shape:
                        matches.append((owner,offset,slot["set"],slot["binding"]))
        if not matches:
            counts["no_descriptor_offset_shape_join"]+=1;continue
        if len(matches)!=1:
            counts["ambiguous_join"]+=1;continue
        owner,offset,set_id,binding=matches[0]
        key=(set_id,binding,offset)
        candidates.setdefault(key,[]).append((owner,offset,source_offset,old_owner,alias))
    for joined in candidates.values():
        if len(joined)!=1:
            counts["non_injective_join"]+=len(joined);continue
        owner,offset,source_offset,old_owner,alias=joined[0]
        counts["unique_descriptor_offset_shape_join"]+=1
        counts["original_offset_preserved"]+=int(offset==source_offset)
        counts["original_offset_relocated"]+=int(offset!=source_offset)
        counts["original_or_generated_owner_preserved"]+=int(owner in (old_owner,alias))
    keys=("expected","serialized_name_present","missing_serialized_name","no_descriptor_offset_shape_join",
          "ambiguous_join","non_injective_join","unique_descriptor_offset_shape_join",
          "original_offset_preserved","original_offset_relocated","original_or_generated_owner_preserved")
    return {k:counts[k] for k in keys}

def resource_join(expected,source_ref,metadata,slots,view):
    from tools.gt_skybox_offset_differential import audit as d
    resources=d.resources(source_ref);counts=Counter();matched={}
    for e in expected:
        counts["expected"]+=1
        tex=e["source_texture_name"]
        kind="separate_images" if e["kind"]=="t" else "separate_samplers"
        name=tex if e["kind"]=="t" else "sampler"+tex
        c=resources.get((kind,name))
        if c is None:
            counts["source_resource_schema_unresolved"]+=1;continue
        pair=metadata["textures"].get(tex)
        if pair is None:
            counts["missing_serialized_texture_name"]+=1;continue
        index=pair[0] if e["kind"]=="t" else pair[1]
        found=[r for r in unique_slots(slots,kind,index,view) if (r["type"],r["array"])==c]
        if len(found)!=1:
            counts["missing_or_ambiguous_descriptor_type"]+=1;continue
        key=(found[0]["set"],found[0]["binding"])
        matched.setdefault(key,[]).append(name)
    for rows in matched.values():
        if len(rows)==1:counts["unique_descriptor_type_join"]+=1
        else:counts["non_injective_join"]+=len(rows)
    keys=("expected","source_resource_schema_unresolved","missing_serialized_texture_name",
          "missing_or_ambiguous_descriptor_type","unique_descriptor_type_join","non_injective_join")
    return {k:counts[k] for k in keys}

def block_binding_census(metadata,slots,view):
    b=metadata["buffers"];g=metadata["groups"]
    matched={}
    shape_ok=0
    for name,index in b.items():
        rs=unique_slots(slots,"ubos",index,view)
        if len(rs)!=1:continue
        r=rs[0];matched.setdefault((r["set"],r["binding"]),[]).append(name)
        if name in g:
            offsets={m["offset"] for m in r["members"]}
            shape_ok+=int(set(g[name]["members"].values())<=offsets)
    return dict(serialized_buffers=len(b),reflected_ubos=sum(r["kind"]=="ubos" for r in slots),
                groups_with_members=sum(bool(x["members"]) for x in g.values()),
                groups_with_binding=sum(name in b for name in g),
                unique_descriptor_candidates=sum(len(v)==1 for v in matched.values()),
                ambiguous_descriptor_candidates=sum(len(v)>1 for v in matched.values()),
                full_group_offset_subset_candidates=shape_ok)

def view_profiles(layouts,stage,named,static_ref,source_ref,metadata,actual):
    expected=source_member_records(layouts,stage,static_ref)
    slots=reflected_slots(actual)
    result={}
    for view in VIEWS:
        result[view]={"numeric":member_join(expected,metadata,slots,view),
                      "resources":resource_join(named,source_ref,metadata,slots,view),
                      "buffers":block_binding_census(metadata,slots,view)}
    return dict(views=result,variant_blob_decoded=metadata["variant"],
                direct_binding_index_is_not_runtime_proof=True,
                packed_views_are_diagnostic_only=True)
