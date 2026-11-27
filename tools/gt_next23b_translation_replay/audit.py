"""Read-only, private replay of the existing DXBC translation toolchain.

Only use on an independently authorized, immutable source snapshot. Expected
stage/source SHA comes from the independent source-slot byte admission, not a
manifest produced by the translator. Tool executable pins must be supplied by
an independent trusted environment; binary hashes alone do not pin libraries.
No acquisition, Unity compile, installation, or semantic equivalence claim.
"""
from hashlib import sha256
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile

from scripts.probe_directx_shader_bridge import inspect_dxbc
from scripts.run_original_dxbc_translation_probe import version_tokens

TOOLS = ("vkd3d-compiler", "spirv-val", "spirv-cross", "glslangValidator")
FILES = ("source.dxbc", "original.spv", "private.hlsl", "roundtrip.spv")
LIMITS = dict(zip(FILES, (16*1024*1024, 64*1024*1024, 1024*1024, 64*1024*1024)))
HEX = re.compile(r"[0-9a-f]{64}\Z")


def need(ok, why):
    if not ok:
        raise ValueError("next23b_translation_replay_" + why)


def sha(data):
    return sha256(data).hexdigest()


def read_bounded(path, limit):
    need(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size <= limit,
         "unsafe_or_missing_snapshot_file")
    with path.open("rb") as f:
        data = f.read(limit + 1)
    need(0 < len(data) <= limit, "snapshot_size")
    return data


def snapshot(directory):
    """Read once; caller must ensure immutable/quiescent private directory."""
    need(directory.is_dir() and not directory.is_symlink(), "unsafe_directory")
    return {name: read_bounded(directory/name, LIMITS[name]) for name in FILES}


def pins_checked(pins):
    need(type(pins) is dict and set(pins) == set(TOOLS), "tool_population")
    resolved = {}
    for name in TOOLS:
        pair = pins[name]
        need(type(pair) is dict and set(pair) == {"path", "sha256"}
             and type(pair["path"]) is str and type(pair["sha256"]) is str
             and HEX.fullmatch(pair["sha256"]), "tool_pin_schema")
        path = Path(pair["path"])
        need(path.is_absolute() and path.is_file() and not path.is_symlink()
             and path.resolve() == path and os.access(path, os.X_OK), "tool_path")
        need(sha(read_bounded(path, 128*1024*1024)) == pair["sha256"], "tool_digest")
        resolved[name] = str(path)
    return resolved


def module_stage(data, stage):
    """Require one actual main entrypoint of the expected execution model."""
    need(type(data) is bytes and 20 <= len(data) <= 64*1024*1024
         and len(data)%4 == 0 and data[:4] == b"\x03\x02\x23\x07", "module_header")
    at, entries = 20, []
    while at < len(data):
        head, = struct.unpack_from("<I", data, at)
        width, op = head >> 16, head & 65535
        need(width > 0 and at+4*width <= len(data), "module_instruction")
        if op == 15:
            need(width >= 4, "entrypoint_record")
            model, = struct.unpack_from("<I", data, at+4)
            name = data[at+12:at+4*width].split(b"\0",1)[0]
            entries.append((model, name))
        at += 4*width
    need(entries == [(0 if stage == 1 else 4, b"main")], "module_stage_entry")


def invoke(tools, directory, name, *args):
    try:
        result = subprocess.run([tools[name], *args], cwd=directory,
                                capture_output=True, timeout=30, check=False,
                                env={**os.environ, "LC_ALL":"C"})
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("next23b_translation_replay_tool_failed_" + name) from None
    # Do not expose private tool output or paths.
    need(result.returncode == 0, "tool_failed_" + name)


def replay(stage, expected_dxbc_sha, retained, pins):
    """Replay exact legacy flags in a clean private temp folder, compare bytes.

    expected_dxbc_sha and stage must come from independent source admission.
    retained is a single immutable snapshot of the four producer outputs.
    A pass proves exact reproducibility under this toolchain only, not semantic
    DXBC/SPIR-V equivalence, runtime route selection or rights/authenticity.
    """
    need(type(stage) is int and stage in (0,1)
         and type(expected_dxbc_sha) is str and HEX.fullmatch(expected_dxbc_sha), "expected_identity")
    need(type(retained) is dict and set(retained)==set(FILES)
         and all(type(retained[n]) is bytes and 0<len(retained[n])<=LIMITS[n]
                 for n in FILES), "snapshot_schema")
    code = retained["source.dxbc"]
    need(sha(code)==expected_dxbc_sha, "source_digest")
    header = inspect_dxbc(code)
    versions = version_tokens(code)
    need(header["container"]=="DXBC" and header["executable_shader_chunk"]
         and len(versions)==1 and versions[0]["shader_stage_code"]==stage, "source_stage")
    tools = pins_checked(pins)
    with tempfile.TemporaryDirectory(prefix="gt-translation-replay-") as tmp:
        work = Path(tmp)
        (work/"source.dxbc").write_bytes(code)
        invoke(tools, work, "vkd3d-compiler", "-x","dxbc-tpf","-b","spirv-binary",
               "-o","original.spv","source.dxbc")
        first = read_bounded(work/"original.spv", LIMITS["original.spv"])
        module_stage(first, stage)
        invoke(tools, work, "spirv-val","--target-env","vulkan1.1","original.spv")
        need(first == retained["original.spv"], "original_spv_mismatch")
        invoke(tools, work, "spirv-cross","original.spv","--hlsl","--shader-model","50",
               "--output","private.hlsl")
        hlsl = read_bounded(work/"private.hlsl", LIMITS["private.hlsl"])
        need(hlsl == retained["private.hlsl"], "hlsl_mismatch")
        invoke(tools, work, "glslangValidator","-V","-D","-S","vert" if stage==1 else "frag",
               "-e","main","-o","roundtrip.spv","private.hlsl")
        roundtrip = read_bounded(work/"roundtrip.spv", LIMITS["roundtrip.spv"])
        module_stage(roundtrip, stage)
        invoke(tools, work, "spirv-val","--target-env","vulkan1.1","roundtrip.spv")
        need(roundtrip == retained["roundtrip.spv"], "roundtrip_spv_mismatch")
        need((work/"source.dxbc").read_bytes()==code, "source_modified")
    pins_checked(pins)
    return {"stage":stage, "source_dxbc_sha256":expected_dxbc_sha,
            "original_spv_sha256":sha(first), "hlsl_sha256":sha(hlsl),
            "roundtrip_spv_sha256":sha(roundtrip)}


def verify_all(byte_witness, retained, pins):
    """Full NEXT23b consumer; private output only.

    byte_witness must be the trusted in-process result of the previous
    independent source admission (not a user-provided assertion).
    """
    need(type(byte_witness) is dict and type(byte_witness.get("slots")) is list
         and len(byte_witness["slots"])==2312, "slot_population")
    expected = {}
    for row in byte_witness["slots"]:
        ref, stage, digest = row["program_ref"], row["stage"], row["dxbc_sha256"]
        need(type(ref) is str and re.fullmatch(r"program-[0-9]{3}", ref)
             and expected.setdefault(ref,(stage,digest))==(stage,digest), "slot_program_drift")
    need(set(expected)=={f"program-{i:03d}" for i in range(134)}
         and len(set(expected.values()))==134 and type(retained) is dict
         and set(retained)==set(expected), "program_population")
    proof = {ref:replay(*expected[ref], retained[ref], pins) for ref in sorted(expected)}
    return proof, {"status":"PASS_EXACT_TRANSLATION_REPLAY_ONLY",
                   "programs_replayed":len(proof), "source_slots":2312,
                   "semantic_equivalence_verified":False,
                   "original_authorization_verified_by_this_tool":False,
                   "compiled_unity_route_identity_verified":False,
                   "production_install_allowed":False}
