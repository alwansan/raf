"""T2: original Foam DXBC t/s -> actual translated SPIR-V variable provenance.

Compile two deliberately different explicit vkd3d descriptor mappings for the
*same* SHA-pinned original DXBC and a default control. Only trust native t/s
register identity if source-specific SPIR-V IDs remain exactly stable and all
module words are identical after masking ONLY DescriptorSet/Binding literals.
Compare against B20's already SHA-authenticated private original.spv.
Never publish proprietary symbols or original compiled code.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from scripts.b20_private_foam_packet import ORIGINAL_STAGE_SHA
from scripts.t2_foam_member_abi import STAGES, _physical
from scripts.t2_foam_resource_abi import (
    ORIGINAL_TEXTURES_PER_STAGE, COMPILED_NUMERIC_RESOURCE_BINDINGS,
)

MAGIC = 0x07230203
MAX_BYTES = 2 * 1024 * 1024
MAX_ID = 2**20
MAX_INST = 150000
BIND = 33
SET = 34
SPV_OP_DECORATE = 71
SPV_OP_VARIABLE = 59
SPV_OP_POINTER = 32
SPV_OP_IMAGE = 25
SPV_OP_SAMPLER = 26
SPV_OP_STRUCT = 30


def interface_address(profile, kind, index):
    if profile not in ("A", "B") or kind not in ("image", "sampler", "cb"):
        raise ValueError("Invalid explicit DXBC interface identity")
    if type(index) is not int or not 0 <= index <= 5:
        raise ValueError("Invalid original DXBC resource register")
    if kind == "cb":
        return 0, index
    set_ = 3 if profile == "A" else 4
    if kind == "image":
        return set_, (11 if profile == "A" else 22) + 4 * index
    return set_, (41 if profile == "A" else 52) + 4 * index


def declared_spirv_interface(module):
    """Decode typed SPIR-V descriptor variables; only mask set/binding numbers.

    The complete remaining SPIR-V program, IDs, types, instructions, entrypoint,
    execution modes and decorations are byte-for-byte compared by callers.
    """
    if (not isinstance(module, bytes) or not 20 <= len(module) <= MAX_BYTES
            or len(module) % 4):
        raise ValueError("Invalid bounded SPIR-V original program")
    words = list(struct.unpack("<" + "I" * (len(module) // 4), module))
    if (words[0] != MAGIC or not 0 < words[3] <= MAX_ID or words[4] != 0):
        raise ValueError("SPIR-V module header drift")
    pointers, types, variables, decorators = {}, {}, {}, {}
    pos, instructions = 5, 0
    while pos < len(words):
        inst_len = words[pos] >> 16
        opcode = words[pos] & 0xffff
        if inst_len < 1 or inst_len > 1024 or pos + inst_len > len(words):
            raise ValueError("SPIR-V instruction length overflow")
        ins = words[pos + 1:pos + inst_len]
        instructions += 1
        if instructions > MAX_INST:
            raise ValueError("SPIR-V instruction count exceeded")
        if opcode in (SPV_OP_IMAGE, SPV_OP_SAMPLER, SPV_OP_STRUCT):
            if not ins or ins[0] in types:
                raise ValueError("Duplicate or missing SPIR-V resource type")
            types[ins[0]] = {SPV_OP_IMAGE:"image", SPV_OP_SAMPLER:"sampler",
                             SPV_OP_STRUCT:"struct"}[opcode]
        if opcode == SPV_OP_POINTER:
            if len(ins) != 3 or ins[0] in pointers:
                raise ValueError("Malformed SPIR-V pointer type")
            pointers[ins[0]] = (ins[1], ins[2])
        if opcode == SPV_OP_VARIABLE:
            if len(ins) not in (3, 4) or ins[1] in variables:
                raise ValueError("Invalid SPIR-V resource variable")
            variables[ins[1]] = (ins[0], ins[2])
        if opcode == SPV_OP_DECORATE and len(ins) >= 2 and ins[1] in (BIND, SET):
            if len(ins) != 3:
                raise ValueError("Non-scalar SPIR-V descriptor decoration")
            var_id, decoration, value = ins
            if not 0 < var_id < words[3] or value > 255:
                raise ValueError("Out-of-range SPIR-V descriptor decoration")
            row = decorators.setdefault(var_id, {})
            if decoration in row:
                raise ValueError("Duplicate SPIR-V Binding/DescriptorSet decoration")
            row[decoration] = value
            # ONLY the numeric value changes: do not mask instructions,
            # resource variable IDs, types, other decorations or names.
            words[pos + 3] = 0
        pos += inst_len
    if pos != len(words):
        raise ValueError("SPIR-V trailing bytes")
    result = {"image": {}, "sampler": {}, "cb": {}}
    for var_id, meta in decorators.items():
        if set(meta) != {SET, BIND} or var_id not in variables:
            raise ValueError("Incomplete/misdirected resource decoration")
        pointer_id, var_storage = variables[var_id]
        if pointer_id not in pointers:
            raise ValueError("Resource pointer type absent")
        ptr_storage, pointee = pointers[pointer_id]
        if var_storage != ptr_storage:
            raise ValueError("SPIR-V resource storage class drift")
        actual_type = types.get(pointee)
        if var_storage == 0 and actual_type in ("image", "sampler"):
            kind = actual_type
        elif var_storage == 2 and actual_type == "struct":
            kind = "cb"
        else:
            raise ValueError("Unknown SPIR-V descriptor variable category")
        location = meta[SET], meta[BIND]
        if location in result[kind]:
            raise ValueError("Repeated SPIR-V descriptor location within type")
        result[kind][location] = var_id
    return tuple(words), result


def verify_profile_identity(default_spv, a_spv, b_spv, packet_spv, count, cb_count):
    """Prove native t/s registers by two distinct interfaces, NOT name ordering."""
    if (type(count) is not int or not 0 <= count <= 5
            or type(cb_count) is not int or not 0 <= cb_count <= 3):
        raise ValueError("Invalid original Foam stage resource count")
    normalized = {}
    resources = {}
    for key, module in (("D", default_spv), ("A", a_spv),
                        ("B", b_spv), ("original", packet_spv)):
        normalized[key], resources[key] = declared_spirv_interface(module)
        if any(len(resources[key][c]) != expected
               for c, expected in (("image", count), ("sampler", count), ("cb", cb_count))):
            raise ValueError("SPIR-V typed resource cardinality drift")
    if normalized["A"] != normalized["B"]:
        raise ValueError("Explicit remap changed a non-descriptor SPIR-V program word")
    explicit_ids = {}
    for profile in ("A", "B"):
        got = resources[profile]
        expected = {kind:{interface_address(profile,kind,i) for i in range(n)}
                    for kind,n in (("image",count),("sampler",count),("cb",cb_count))}
        if any(set(got[kind]) != expected[kind] for kind in expected):
            raise ValueError("Explicit source register binding not honored")
        for kind, n in (("image",count),("sampler",count),("cb",cb_count)):
            for idx in range(n):
                source_key = (kind,idx)
                variable = got[kind][interface_address(profile,kind,idx)]
                if source_key in explicit_ids and explicit_ids[source_key] != variable:
                    raise ValueError("Original source register SPIR-V variable ID changed")
                explicit_ids[source_key] = variable
    # This is the strongest gate: no declaration-order, name, guessed affine
    # numeric binding offsets or synthetic caller-supplied provenance booleans.
    if normalized["D"] != normalized["A"]:
        raise ValueError("Default compiler program differs beyond descriptor bindings")
    if normalized["original"] != normalized["D"]:
        raise ValueError("Original B20 generated packet differs from current compiler graph")
    default_locs = {}
    for kind, locs in resources["D"].items():
        for location,var_id in locs.items():
            default_locs[(kind,var_id)] = location
    original_locs = {}
    for kind,locs in resources["original"].items():
        for location,var_id in locs.items():
            original_locs[(kind,var_id)] = location
    table = []
    for key, var_id in sorted(explicit_ids.items()):
        if (key[0],var_id) not in default_locs or (key[0],var_id) not in original_locs:
            raise ValueError("Source register variable ID missing in original/default SPIR-V")
        default_addr = default_locs[key[0],var_id]
        original_addr = original_locs[key[0],var_id]
        if default_addr != original_addr:
            raise ValueError("B20 original and default compiled resource address mismatch")
        table.append({
            "source_kind":key[0],
            "original_dxbc_register":key[1],
            "compiled_image_sampler_or_cb_set":default_addr[0],
            "compiled_binding":default_addr[1],
        })
    if len(table) != 2*count + cb_count:
        raise ValueError("Incomplete explicit→default SPIR-V resource role bijection")
    return {
        "source_native_dxbc_to_compiled_original_spirv_id_verified": True,
        "full_original_spirv_graph_equal_after_only_descriptor_literals_mask": True,
        "distinct_explicit_profiles_proven": 2,
        "source_register_to_default_compiled_descriptors": table,
        "original_material_upload_or_sampler_state_verified": False,
        "original_unity_shaderlab_import_or_adreno_pixels_verified": False,
        "proprietary_shader_code_identifiers_disclosed": False,
    }


def inspect_packet(packet, manifest, executable):
    packet, manifest, executable = map(lambda p: Path(p).absolute(),
                                       (packet,manifest,executable))
    if (not packet.is_dir() or not _physical(packet)
            or not manifest.is_file() or not _physical(manifest)
            or not executable.is_file() or not _physical(executable)):
        raise ValueError("Private authenticated Foam packet/remapper absent")
    approved = json.loads(manifest.read_text())
    if (approved.get("status") != "private_two_pass_inputs_staged"
            or approved.get("original_stage_programs") != 4
            or approved.get("original_shader_raw_object_sha256",
                            approved.get("original_object_sha256")) !=
            "67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1"
            or not approved.get("private_packet_staged")
            or approved.get("shaderlab_constructed") is not False):
        raise ValueError("B20 original Foam stage packet SHA prerequisite missing")
    rows = approved.get("stage_hashes")
    if not isinstance(rows,list) or len(rows)!=4:
        raise ValueError("Original Foam four SHA stage records absent")
    out = []
    with tempfile.TemporaryDirectory(prefix="t2-foam-explicit-private-") as directory:
        scratch = Path(directory)
        for n,(pi,stage) in enumerate(STAGES):
            item = rows[n]
            if (item.get("pass"),item.get("stage_code")) != (pi,stage):
                raise ValueError("Original stage order changed")
            where = packet / ("pass%d-stage%d"%(pi,stage))
            binary = where / "source.dxbc"
            translated = where / "original.spv"
            if (not _physical(binary) or not _physical(translated)
                    or not binary.is_file() or not translated.is_file()
                    or hashlib.sha256(binary.read_bytes()).hexdigest() != ORIGINAL_STAGE_SHA[(pi,stage)]
                    or item.get("original_dxbc_sha256") != ORIGINAL_STAGE_SHA[(pi,stage)]):
                raise ValueError("Original Foam DXBC compiled hash mismatch")
            count = ORIGINAL_TEXTURES_PER_STAGE[(pi,stage)]
            # Both authentic fragment passes bind CBV b0; vertex has t/s 0
            # and is source-empty. Its sampler mapping cannot be proved by
            # a nonzero t/s remap. Only fragment program maps are decisive.
            if stage == 1:
                out.append({"pass":pi,"stage_code":stage,
                            "original_texture_rows":0,
                            "genuine_sampler_register_mapping_covered":False})
                continue
            if count not in (1,5):
                raise ValueError("Unexpected genuine Foam fragment texture count")
            compiled = {}
            for profile in ("D","A","B"):
                dst = scratch / ("pass%d-%s.spv"%(pi,profile))
                try:
                    run = subprocess.run([str(executable),str(binary),str(dst),
                                          profile,str(count),"1"],
                                         stdin=subprocess.DEVNULL,
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL,
                                         timeout=30,check=False)
                except (OSError,subprocess.SubprocessError) as exc:
                    raise ValueError("Private original compiler executable failure") from None
                if run.returncode:
                    raise ValueError("Public explicit vkd3d compiler return code "+str(run.returncode))
                compiled[profile] = dst.read_bytes()
            data = verify_profile_identity(
                compiled["D"],compiled["A"],compiled["B"],
                translated.read_bytes(),count,1)
            out.append({"pass":pi,"stage_code":stage,
                        "original_texture_rows":count,**data})
    if len(out)!=4 or sum(x["original_texture_rows"] for x in out)!=6:
        raise ValueError("Original Foam source full-stage coverage incomplete")
    return {
        "status":"original_foam_explicit_native_to_spirv_binding_identity_verified",
        "source_authentic_original_stages":4,
        "original_fragments_explicit_verified":2,
        "original_t_s_pairs_mapped":6,
        "stages":out,
        "authored_unity_material_texture_sampler_upload_verified":False,
        "unity_shaderlab_or_adreno_pixels_verified":False,
        "proprietary_program_symbols_binaries_published":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--packet",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    p.add_argument("--compiler",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    try:
        dest=a.out.absolute()
        if (dest.exists() or not dest.parent.is_dir() or not _physical(dest)
                or dest.is_relative_to(a.packet.absolute())):
            raise ValueError("Unsafe original program report destination")
        result=inspect_packet(a.packet,a.manifest,a.compiler)
        dest.write_text(json.dumps(result,sort_keys=True)+"\n")
        print("T2_FOAM_EXPLICIT_SPV "+json.dumps({
            "status":result["status"],
            "native_t_s_pairs_source_compiler_mapped":6,
            "original_fragment_programs":2,
            "original_to_spirv_mapping_test_completed":True,
            "unity_or_device":False,
            "private_shader_published":False,
        }))
        return 0
    except BaseException as exc:
        # Error names only; never emit raw exception strings containing names.
        print("T2_FOAM_EXPLICIT_SPV "+json.dumps({
            "status":"blocked","failure_class":type(exc).__name__,
            "original_to_spirv_mapping_test_completed":False,
            "private_shader_published":False}))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
