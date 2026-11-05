"""Only in private CI: bind original FFT DXBC-derived Unity HLSL image roles.

Original DXBC declares sampled t0/t1 and storage u0, as authenticated by
B18's source register and B01's C# SetTexture metadata. The translated HLSL
variable identifiers are not original resource names. Keep names in ephemeral
sidecar only; public diagnostics contain role counts, never identifiers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.t1_stage_original_fft_compute_candidates import (
    validate_import_candidate_manifest,
)

MAX_HLSL_CHARS = 512 * 1024
NAME = re.compile(r"^[A-Za-z_][A-Za-z_0-9]{0,119}$")
# SPIRV-Cross HLSL50 explicit typed Texture2D declarations.
# Anchor and validate register classes, not source code or invented names.
IMAGE = re.compile(
    r"(?m)^\s*(RWTexture2D|Texture2D)\s*"
    r"(?:<[^>\r\n]{1,100}>\s*)?"
    r"([A-Za-z_][A-Za-z_0-9]{0,119})\s*"
    r":\s*register\s*\(\s*([tu])\s*(\d{1,3})\s*"
    r"(?:,\s*space\s*(\d{1,2})\s*)?\)\s*;"
)
RESOURCE_DECL = re.compile(r"(?m)^\s*(?:RW)?Texture2D\b")
ROLES = {("t",0):"source",("t",1):"butterfly",("u",0):"output"}
SLOTS = (0,1)


def translated_image_symbols(text):
    if type(text) is not str or not 10 < len(text) <= MAX_HLSL_CHARS:
        raise ValueError("Private HLSL absent or too large")
    # Remove comments before declaration recognition; bounded scanner does
    # not claim to parse macros or conditional branches. Fail on unmatched
    # declarations instead of trusting an approximate register.
    clean = re.sub(r"/\*[\s\S]*?\*/|//[^\r\n]*",
                   lambda m: " " * len(m.group()), text)
    rows = list(IMAGE.finditer(clean))
    if len(rows) != 3 or len(RESOURCE_DECL.findall(clean)) != 3:
        raise ValueError("Private HLSL contains missing/ambiguous image declarations")
    bindings = {}
    for row in rows:
        typ, name, bank, register, space = row.groups()
        role = (bank,int(register))
        if ((typ=="RWTexture2D") != (bank=="u")
                or role not in ROLES or role in bindings
                or space not in (None,"0") or not NAME.fullmatch(name)):
            # The following is ONLY a bounded public register/type profile,
            # not the original generated identifier, expression or source.
            # It identifies an actual translator layout mismatch so that we
            # do not guess an unverified t0/t1/u0 mapping or touch game files.
            profile=sorted({
                (("u" if kind=="RWTexture2D" else "t"),
                 reg,int(n), int(s or "0"))
                for kind,identifier,reg,n,s in (m.groups() for m in rows)
            })
            raise ValueError(
                "Translated FFT texture register type/drift profile="+
                repr(profile))
        bindings[role] = name
    if set(bindings)!=set(ROLES) or len(set(bindings.values())) != 3:
        raise ValueError("Translated FFT image bindings incomplete or aliased")
    return {label:bindings[key] for key,label in ROLES.items()}


def stage_private_gpu_resources(project: Path):
    root=Path(project)
    base=root/"Assets/T1OriginalDerived"
    manifest_file=base/"PrivateCandidates.json"
    if root.is_symlink() or base.is_symlink() or manifest_file.is_symlink():
        raise ValueError("Unsafe private project/resource manifest")
    if not manifest_file.is_file():
        raise ValueError("Original-derived SHA manifest missing")
    manifest=json.loads(manifest_file.read_text())
    validate_import_candidate_manifest(manifest,root)
    results=[]
    for slot in SLOTS:
        item=manifest["rows"][slot]
        path=root/item["compute_asset"]
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=item["candidate_sha256"]:
            raise ValueError("Private Unity shader SHA mismatch before binding")
        try:
            symbols=translated_image_symbols(content.decode("utf-8"))
        except UnicodeDecodeError:
            raise ValueError("Original-derived HLSL not valid text") from None
        results.append({
            "compiled_slot":slot,
            "candidate_sha256":item["candidate_sha256"],
            "expected_group_x":item["expected_group_x"],
            "source_property":symbols["source"],
            "butterfly_property":symbols["butterfly"],
            "output_property":symbols["output"],
        })
    # Private only: never upload, print or commit the resource names.
    sidecar=base/"PrivateGpuResources.json"
    if sidecar.exists() or sidecar.is_symlink():
        raise ValueError("Refuse existing private FFT resource sidecar")
    sidecar.write_text(json.dumps({
        "schema_version":1, "original_fft_object_sha256":manifest["original_fft_object_sha256"],
        "selected_compiled_slots":list(SLOTS), "resources":results,
        "original_authored_resource_names_proven":False,
        "original_runtime_kernel_mapping_proven":False,
        "unity_gpu_dispatch_executed":False,
        "android_device_proven":False},sort_keys=True),encoding="utf-8")
    return {
        "source_authentic_original_compiled_candidates":len(manifest["rows"]),
        "private_translated_image_property_roles":len(results)*3,
        "selected_pair_slots":list(SLOTS),
        "original_authored_resource_names_proven":False,
        "original_runtime_kernel_mapping_proven":False,
        "unity_gpu_dispatch_executed":False,
        "android_device_proven":False,
        "private_property_names_published":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,required=True)
    args=p.parse_args()
    print("RAFT_T1_FFT_PRIVATE_GPU_RESOURCE_BRIDGE "+json.dumps(
        stage_private_gpu_resources(args.project),sort_keys=True))


if __name__=="__main__":
    main()
