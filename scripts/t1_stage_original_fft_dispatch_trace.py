"""Stage Android-only diagnostics at SHA-authentic original Dx11FFT binding and Dispatch sites.

Never rewrite original Dispatch/SetTexture arithmetic, invent FindKernel, or
publish original CSharp9. Recreate the native lifetime overlay from the backed
up original before touching the generated Unity project.
"""
import argparse
import hashlib
from pathlib import Path
import re

from scripts.adapt_android_render_lifetimes import adapt
from scripts.probe_original_fft_kernel_callsites import (
    analyze_source, constant_offset_from_base, parse_original_args,
    mask_noncode, SIMPLE_ID, sha,
)
from scripts.probe_original_fft_inherited_seed import prove, BASE_SHA256
from scripts.probe_original_water_compute import ORIGINAL_SOURCE_SHA256

ORIGINAL_SHA = ORIGINAL_SOURCE_SHA256["Dx11FFT"]
MARKER = "RaftAndroid.Diagnostics.T1FftDirectDispatchTrace"
# Exact full-line direct member invocation; no invocation nested inside
# expressions, conditional branches or shared statements may be rewritten.
DIRECT = re.compile(
    r"(?m)^(?P<indent>[ \t]*)(?P<receiver>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"
    r"\.Dispatch\((?P<args>[^;\r\n]+)\);[ \t]*$"
)


BIND = re.compile(DIRECT.pattern.replace(r'\.Dispatch', r'\.SetTexture'))


def _one(root, stem):
    paths = list(root.rglob(stem + ".cs"))
    if len(paths) != 1 or paths[0].is_symlink() or not paths[0].is_file():
        raise ValueError("Required original CSharp identity absent or ambiguous")
    return paths[0]


def _read(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return text.replace("\r\n", "\n"), raw


def rewrite(original, adapted, base):
    if not all(isinstance(x, str) for x in (original, adapted, base)):
        raise ValueError("Invalid original FFT source inputs")
    if sha(original) != ORIGINAL_SHA or sha(base) != BASE_SHA256:
        raise ValueError("Original Dx11FFT/GpuFFT source SHA changed")
    if adapted != adapt("Dx11FFT", original).replace("\r\n", "\n"):
        raise ValueError("Generated game source differs from pinned original lifetime overlay")
    verified = prove(original, base, ORIGINAL_SHA, BASE_SHA256)
    fieldhash = verified["protected_inherited_seed_identifier_sha256"]
    fields = re.findall(r"\bprotected\s+int\s+([A-Za-z_]\w*)\s*;", base)
    seed = [value for value in fields if sha(value) == fieldhash]
    if len(seed) != 1:
        raise ValueError("Inherited protected original FFT exponent field ambiguous")
    report = analyze_source(original, ORIGINAL_SHA)
    by_api = report["calls_by_api"]
    if (by_api.get("Dispatch") != 2 or by_api.get("SetTexture") != 6
            or by_api.get("FindKernel", 0) != 0):
        raise ValueError("Original managed direct compute call count drift")
    if [r["kernel_index_affine_offset_from_first_dispatch"] for r in
            report["compute_api_callsites"] if r["call_kind"] == "Dispatch"] != [0, 1]:
        raise ValueError("Original source numeric Dispatch offsets differ")

    if MARKER in adapted:
        raise ValueError("Refusing to instrument already patched source")
    matches = list(DIRECT.finditer(adapted))
    if len(matches) != 2:
        raise ValueError("Expected two standalone original Dispatch statements")
    masked = mask_noncode(adapted)
    arguments = []
    receivers = []
    for i, match in enumerate(matches):
        # A regex over raw C# alone is insufficient: comments/strings must not
        # be allowed to masquerade as executable source.
        if not DIRECT.fullmatch(masked[match.start():match.end()]):
            raise ValueError("Dispatch statement appears in non-executable source")
        opener = adapted.find("(", match.start("receiver"), match.end("args"))
        args, closing = parse_original_args(adapted, opener, masked=masked)
        if len(args) != 4 or adapted[closing + 1:match.end()].strip() != ";":
            raise ValueError("Unexpected original Dispatch arity/statement boundary")
        if args[1].strip() != "1" or args[3].strip() != "1":
            raise ValueError("Original Dispatch X/Z counts changed")
        if not SIMPLE_ID.fullmatch(args[2].strip()) or not args[2].strip().endswith(".height"):
            raise ValueError("Original y-group argument not an observed pure texture height")
        receivers.append(match.group("receiver"))
        arguments.append(args)
    if len(set(receivers)) != 1:
        raise ValueError("Original FFT passes use different ComputeShader receivers")
    base_arg = arguments[0][0].strip()
    if not SIMPLE_ID.fullmatch(base_arg):
        raise ValueError("Expected side-effect-free original numeric index variable")
    if [constant_offset_from_base(args[0], base_arg) for args in arguments] != [0, 1]:
        raise ValueError("Actual original Dispatch argument relation drift")

    binds = list(BIND.finditer(adapted))
    if len(binds) != 6:
        raise ValueError("Expected six standalone original SetTexture statements")
    binding_edits = []
    for site, match in enumerate(binds):
        if (not BIND.fullmatch(masked[match.start():match.end()])
                or match.group("receiver") != receivers[0]):
            raise ValueError("Original SetTexture receiver or source boundary changed")
        opener = adapted.find("(", match.start("receiver"), match.end("args"))
        args, closing = parse_original_args(adapted, opener, masked=masked)
        pass_index = site // 3
        if (len(args) != 3 or adapted[closing + 1:match.end()].strip() != ";"
                or constant_offset_from_base(args[0], base_arg) != pass_index
                or match.end() >= matches[pass_index].start()
                or (pass_index and match.start() <= matches[0].end())):
            raise ValueError("Original SetTexture pass ordering or numeric index changed")
        indent = match.group("indent")
        token = "__raftT1FftBind" + str(site)
        binding_edits.append((match.start(), match.end(), (
            indent + "#if UNITY_ANDROID && !UNITY_EDITOR\n"
            + indent + "int " + token + " = " + MARKER + ".BeforeBinding("
            + str(site) + ", " + match.group("receiver") + ");\n"
            + indent + "try\n" + indent + "{\n" + indent + "#endif\n"
            + adapted[match.start():match.end()] + "\n"
            + indent + "#if UNITY_ANDROID && !UNITY_EDITOR\n"
            + indent + "    " + MARKER + ".BindingResult(" + token + ", false);\n"
            + indent + "}\n"
            + indent + "catch (System.Exception)\n"
            + indent + "{\n"
            + indent + "    " + MARKER + ".BindingResult(" + token + ", true);\n"
            + indent + "    throw;\n"
            + indent + "}\n" + indent + "#endif"
        )))
    output = adapted
    edits = binding_edits
    for i, match in reversed(list(enumerate(matches))):
        args = arguments[i]
        indent = match.group("indent")
        token = "__raftT1FftBeforeDispatch" + str(i)
        params = ", ".join([match.group("receiver")] + [x.strip() for x in args] +
                           ["this." + seed[0], str(i)])
        original_line = adapted[match.start():match.end()]
        replacement = (
            indent + "#if UNITY_ANDROID && !UNITY_EDITOR\n"
            + indent + "int " + token + " = " + MARKER + ".BeforeDispatch("
            + params + ");\n"
            + indent + "try\n"
            + indent + "{\n"
            + indent + "#endif\n"
            + original_line + "\n"
            + indent + "#if UNITY_ANDROID && !UNITY_EDITOR\n"
            + indent + "    " + MARKER + ".AfterDispatch(" + token + ");\n"
            + indent + "}\n"
            + indent + "catch (System.Exception __raftT1FftDispatchException" + str(i) + ")\n"
            + indent + "{\n"
            + indent + "    " + MARKER + ".DispatchThrew(" + token
            + ", __raftT1FftDispatchException" + str(i) + ");\n"
            + indent + "    throw;\n"
            + indent + "}\n"
            + indent + "#endif"
        )
        edits.append((match.start(), match.end(), replacement))
    for start, end, replacement in sorted(edits, reverse=True):
        output = output[:start] + replacement + output[end:]
    if (output.count(MARKER + ".BeforeDispatch(") != 2
            or output.count(MARKER + ".AfterDispatch(") != 2
            or output.count(MARKER + ".DispatchThrew(") != 2
            or output.count("catch (System.Exception __raftT1FftDispatchException") != 2
            or len(DIRECT.findall(output)) != 2
            or len(BIND.findall(output)) != 6
            or output.count(MARKER + ".BeforeBinding(") != 6):
        raise ValueError("Incomplete original dispatch trace hook placement")
    return output


def apply(project, original_backup, managed_original, backup):
    project, original_backup = Path(project), Path(original_backup)
    managed_original, backup = Path(managed_original), Path(backup)
    if (not project.is_dir() or not original_backup.is_dir()
            or not managed_original.is_dir() or backup.exists()
            or backup.resolve().is_relative_to(project.resolve())):
        raise ValueError("Unsafe source or backup path for diagnostics")
    path = _one(project, "Dx11FFT")
    old_source = _one(original_backup, "Dx11FFT")
    gpu = _one(managed_original, "GpuFFT")
    original, _ = _read(old_source)
    adapted, raw = _read(path)
    base, _ = _read(gpu)
    patched = rewrite(original, adapted, base)
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    line_ending = "\r\n" if b"\r\n" in raw else "\n"
    changed = bom + patched.replace("\n", line_ending).encode("utf-8")
    if changed == raw:
        raise ValueError("Trace hook did not change source")
    meta = Path(str(path) + ".meta")
    meta_before = meta.read_bytes() if meta.exists() else None
    backup.mkdir(parents=True, exist_ok=False)
    (backup / "Dx11FFT.cs").write_bytes(raw)
    try:
        path.write_bytes(changed)
        if meta_before is not None and meta.read_bytes() != meta_before:
            raise ValueError("Original Dx11FFT .meta GUID changed")
    except BaseException:
        path.write_bytes(raw)
        raise
    return {"original_derived_sha_verified": True,
            "original_inherited_sha_verified": True,
            "native_lifetime_overlay_exact": True,
            "android_only_before_hooks": 2,
            "android_only_binding_hooks": 6,
            "android_only_returned_hooks": 2,
            "original_dispatch_statements_preserved": True,
            "original_findkernel_claimed": False,
            "unity_editor_or_device_executed": False,
            "original_source_or_shader_published": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--original-backup", type=Path, required=True)
    p.add_argument("--managed-original", type=Path, required=True)
    p.add_argument("--backup", type=Path, required=True)
    a = p.parse_args()
    result = apply(a.project, a.original_backup, a.managed_original, a.backup)
    import json
    print("RAFT_T1_ORIGINAL_FFT_DISPATCH_HOOKS " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
