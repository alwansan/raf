"""Private independent slot-to-parameter/resource-bound HLSL admission.

Consume only a trusted in-process source-byte witness and translation replay
from the SAME independently authorized immutable object/segments and snapshots.
This does not acquire source, grant rights, certify semantics, or install.
The historical compose reader is positional; reject any positional mismatch
rather than silently relabel a record. Do not publish private witness contents.
"""
import base64
from hashlib import sha256

from tools.gt_next23b_source_program_admission.audit import canonical, same, table_ranges
from scripts.a12_shader_parameter_decode import parse_parameter_blob
from scripts.b25_foam_cb_namebridge import original_name_registry
from scripts.gt_resource_register_contract import texture_sampler_bindings
from scripts.gt_original_921_cb_layout import bind_constant_buffers, constant_buffer_lanes
from scripts.gt_original_921_resource_rebind import rebind_resources
from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers
from scripts.gt_original_921_keyword_routes import keyword_routes

def need(ok, reason):
    if not ok:
        raise ValueError("next23b_bound_stage_" + reason)

def sha(data):
    return sha256(data).hexdigest()

def key(row, ordinal="bucket_ordinal"):
    fields = ("subshader","pass","stage","player_bucket",ordinal)
    values = tuple(row[k] for k in fields)
    need(all(type(v) is int and v >= 0 for v in values)
         and values[2] in (0,1), "unsupported_slot_coordinate")
    return values

def verify_slots(*, manifest, parsed, segments, source_witness, translation_proof,
                 programs, parameter_packet, bound_files, route_packet,
                 expected_counts):
    """Join exact private records to the independent original table and code.

    expected_counts is supplied by the caller's independently known profile.
    The public NEXT23b entry below fixes it; smaller fixtures do not prove it.
    Snapshot maps contain bytes (not paths). The upstream trusted reader must
    ensure they are quiescent and from the same object, not packet assertions.
    Recompute using existing source-format decoders/rebind algorithms; this is
    independent input replay, NOT an independent implementation of semantics.
    """
    need(type(manifest) is dict and manifest.get("unpaired")==[]
         and same(parsed,manifest.get("original_shader_ParsedForm_full_private"))
         and source_witness.get("parsed_form_sha256")==sha(canonical(parsed)),
         "parsed_form_commitment")
    pairs=manifest["paired"]
    passes=manifest["original_passes"]
    need(len(pairs)==sum(expected_counts) and len(passes)==len(expected_counts)
         and len(parsed["m_SubShaders"])==1
         and len(parsed["m_SubShaders"][0]["m_Passes"])==len(expected_counts),
         "pass_population")
    counts=[0]*len(expected_counts)
    trusted={}
    for row in source_witness["slots"]:
        k=key(row)
        need(k not in trusted,"duplicate_source_slot")
        trusted[k]=row
    need(len(trusted)==2*len(pairs),"source_slot_population")
    need(type(parameter_packet) is dict and set(parameter_packet)=={
         "stage_records","decoded_original_named_layouts","blobs_base64"},
         "parameter_packet_schema")
    records=parameter_packet["stage_records"]
    need(type(records) is list and len(records)==len(trusted)
         and set(bound_files)==set(range(len(records))),"record_population")
    need(set(programs)==set(translation_proof)=={r["program_ref"] for r in trusted.values()},
         "program_population")
    ranges=table_ranges(segments)
    layouts, raw_by_index, checked_programs, seen, witness = {}, {}, {}, set(), []
    for pair_index,pair in enumerate(pairs):
        p=pair["pass"]
        need(type(p) is int and 0<=p<len(counts) and type(pair["subshader"]) is int
             and pair["subshader"]==0,"pair_owner")
        counts[p]+=1
        actual_pass=parsed["m_SubShaders"][0]["m_Passes"][p]
        copied=passes[p]
        need(copied["subshader"]==0 and copied["pass"]==p
             and same(copied["original_state"],actual_pass["m_State"])
             and same(copied["original_name_indices"],actual_pass["m_NameIndices"]),
             "pass_metadata")
        names=original_name_registry(actual_pass["m_NameIndices"])
        for offset,(lane,stage,field,copyfield) in enumerate((
              ("vs",1,"progVertex","original_vertex_program"),
              ("fs",0,"progFragment","original_fragment_program"))):
            row=pair[lane]
            program=actual_pass[field]
            need(same(program,copied[copyfield]),"stage_table")
            k=key(dict(row,subshader=0,**{"pass":p},stage=stage))
            need(k in trusted and k not in seen,"source_slot_join")
            seen.add(k)
            original=trusted[k]
            _,_,_,bucket,ordinal=k
            meta=program["m_PlayerSubPrograms"][bucket][ordinal]
            need(same(meta,row["original_variant_metadata"])
                 and original["metadata_sha256"]==sha(canonical(meta))
                 and original["blob_index"]==meta["m_BlobIndex"]
                 and same(original["keyword_indices"],meta["m_KeywordIndices"])
                 and original["program_ref"]==row["program_ref"],"slot_program_metadata")
            ref=row["program_ref"]
            if ref not in checked_programs:
                proof=translation_proof[ref]
                snap=programs[ref]
                need(type(snap) is dict and set(snap)=={"source.dxbc","private.hlsl"}
                     and all(type(v) is bytes and len(v)>0 for v in snap.values())
                     and proof["stage"]==stage
                     and proof["source_dxbc_sha256"]==original["dxbc_sha256"]
                     and sha(snap["source.dxbc"])==original["dxbc_sha256"]
                     and sha(snap["private.hlsl"])==proof["hlsl_sha256"],
                     "translated_input_commitment")
                checked_programs[ref]=(stage,original["dxbc_sha256"])
            need(checked_programs[ref]==(stage,original["dxbc_sha256"]), "reused_program_identity")
            index=program["m_ParameterBlobIndices"][bucket][ordinal]
            need(type(index) is int and 0<=index<len(ranges),"parameter_index")
            seg,at,size=ranges[index]
            if index not in layouts:
                raw=segments[seg][at:at+size]
                decoded={}
                parse_parameter_blob(raw,private_layout=decoded)
                layouts[index]=decoded
                raw_by_index[index]=raw
            decoded=layouts[index]
            source=programs[ref]["private.hlsl"].decode("utf-8")
            common=program["m_CommonParameters"]
            bindings=texture_sampler_bindings(source,common,names,decoded["resources"])
            buffers=bind_constant_buffers(source,common,names,decoded)
            for buffer in buffers:
                buffer["original_named_lanes"]=constant_buffer_lanes(buffer)
            expected={"subshader":0,"pass":p,"stage":stage,"player_bucket":bucket,
                      "ordinal":ordinal,"original_parameter_blob_index":index,
                      "source_texture_sampler_bindings":bindings,
                      "source_constant_buffer_layouts":buffers}
            pos=pair_index*2+offset
            need(same(records[pos],expected),"parameter_record_slot_or_payload_mismatch")
            expected_bound=rebind_resources(source,bindings)
            expected_named=rebind_constant_buffers(expected_bound,buffers)
            files=bound_files[pos]
            need(type(files) is dict and set(files)=={"resource-bound.hlsl","named-constant-buffers.hlsl"}
                 and files["resource-bound.hlsl"]==expected_bound.encode("utf-8"),
                 "resource_bound_bytes_mismatch")
            need(files["named-constant-buffers.hlsl"]==expected_named.encode("utf-8"),
                 "named_cb_bytes_mismatch")
            witness.append({"slot":list(k),"legacy_directory_ordinal":pos,
                "program_ref":ref,"keyword_indices":list(meta["m_KeywordIndices"]),
                "dxbc_sha256":original["dxbc_sha256"],"parameter_blob_index":index,
                "parameter_segment":seg,"parameter_offset":at,"parameter_bytes":size,
                "parameter_sha256":sha(raw_by_index[index]),
                "record_sha256":sha(canonical(expected)),
                "resource_bound_sha256":sha(expected_bound.encode("utf-8")),
                "named_cb_sha256":sha(expected_named.encode("utf-8"))})
    need(tuple(counts)==tuple(expected_counts) and seen==set(trusted),"source_slot_coverage")
    expected_routes,_=keyword_routes(parsed,pairs,[],passes)
    need(same(expected_routes,route_packet),"route_packet_identity")
    # These are actual independently sliced records, not packet-supplied hashes.
    need(same(parameter_packet["decoded_original_named_layouts"],
              {str(i):v for i,v in layouts.items()}),"decoded_layout_drift")
    need(same(parameter_packet["blobs_base64"],{str(i):base64.b64encode(raw).decode("ascii")
              for i,raw in raw_by_index.items()}),"parameter_blob_bytes_drift")
    return witness, {"status":"PASS_SLOT_PARAMETER_AND_BOUND_HLSL_BYTE_JOIN_ONLY",
         "routes_by_pass":counts,"stage_slots":len(witness),"programs":len(checked_programs),
         "parameter_blobs":len(layouts),"authorization_verified":False,
         "compiler_or_semantic_equivalence_verified":False,
         "compiled_unity_route_identity_verified":False,"production_install_allowed":False}

def verify_next23b(**inputs):
    """Exact NEXT23b consumer; authorized original inputs still required."""
    need(len(inputs["translation_proof"])==134,"next23b_program_population")
    return verify_slots(**inputs,expected_counts=(512,4,128,512))
