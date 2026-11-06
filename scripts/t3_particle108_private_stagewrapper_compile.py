#!/usr/bin/env python3
"""Private Shader48 ShaderLab combined HLSLPROGRAM branch compilation check.

This checks glslang's two macro-selected branches of each scratch ShaderLab
candidate, beyond separately compiled SPIRV-Cross HLSL files. It is NOT Unity
ShaderLab import, original keyword selection, material binding, or GPU fidelity.
No proprietary source, compiler diagnostics, private paths or SPIR-V are logged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

STATUS = "T3_PRIVATE_SHADER48_BOTH_SHADERLAB_BRANCHES_GLSLANG_VULKAN11_VALID"
MAX_SHADERLAB = 4 * 1024 * 1024
MAX_SPV = 8 * 1024 * 1024
EXPECTED = frozenset("keyword-%d-private.shader" % i for i in range(4))
START = re.compile(r"(?m)^[ \t]*HLSLPROGRAM[ \t]*$")
END = re.compile(r"(?m)^[ \t]*ENDHLSL[ \t]*$")
PRAGMAS = frozenset(("#pragma target 5.0", "#pragma vertex main", "#pragma fragment main"))


def extract(source: str) -> str:
    """Extract exactly one ShaderLab program without assuming Unity compilation."""
    if type(source) is not str or not 0 < len(source.encode("utf-8")) <= MAX_SHADERLAB:
        raise ValueError("invalid_private_shaderlab_size")
    start = list(START.finditer(source))
    end = list(END.finditer(source))
    if len(start) != 1 or len(end) != 1 or end[0].start() <= start[0].end():
        raise ValueError("invalid_private_shaderlab_boundaries")
    body = source[start[0].end():end[0].start()]
    if (body.count("#if defined(SHADER_STAGE_VERTEX)") != 1
        or body.count("#elif defined(SHADER_STAGE_FRAGMENT)") != 1
        or body.count("#error Unsupported_stage") != 1):
        raise ValueError("invalid_private_stage_switch")
    lines = body.splitlines(keepends=True)
    pragmas = [line.strip() for line in lines if line.strip().startswith("#pragma")]
    if len(pragmas) != 3 or set(pragmas) != PRAGMAS:
        raise ValueError("invalid_private_shaderlab_pragmas")
    executable = "".join(line for line in lines if not line.strip().startswith("#pragma"))
    if not re.search(r"\bmain\s*\(", executable):
        raise ValueError("invalid_private_shaderlab_entrypoint")
    return executable


def compile_branch(executable: str, stage: int, private_dir: Path) -> bool:
    """Compile selected ShaderLab branch with glslang; never print private errors."""
    if (type(stage) is not int or stage not in (0, 1)
        or type(executable) is not str or not 0 < len(executable.encode("utf-8")) <= MAX_SHADERLAB
        or not isinstance(private_dir, Path) or private_dir.is_symlink()
        or not private_dir.is_dir()):
        raise ValueError("invalid_private_stage_compiler_input")
    suffix, macro = (("frag", "SHADER_STAGE_FRAGMENT")
                     if stage == 0 else ("vert", "SHADER_STAGE_VERTEX"))
    with tempfile.TemporaryDirectory(prefix="t3-shaderlab-branch-", dir=private_dir) as folder:
        root = Path(folder)
        src = root / ("source." + suffix + ".hlsl")
        spv = root / "validated.spv"
        src.write_text(executable, encoding="utf-8")
        cmd = ["glslangValidator", "-V", "-D", "--target-env", "vulkan1.1",
               "-S", suffix, "-e", "main", "-D" + macro + "=1",
               "-o", str(spv), str(src)]
        try:
            result = subprocess.run(cmd, capture_output=True, check=False, timeout=90)
            if result.returncode or not spv.is_file() or spv.is_symlink():
                return False
            if not 20 <= spv.stat().st_size <= MAX_SPV:
                return False
            validated = subprocess.run(
                ["spirv-val", "--target-env", "vulkan1.1", str(spv)],
                capture_output=True, check=False, timeout=45)
            return validated.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False


def verify(private_dir: Path, *, compiler=compile_branch) -> dict:
    """Both stage branches must independently compile for all four candidates."""
    if (not isinstance(private_dir, Path) or not private_dir.is_dir()
        or private_dir.is_symlink()):
        raise ValueError("invalid_private_variant_directory")
    found = {p.name for p in private_dir.glob("keyword-*-private.shader")}
    if found != EXPECTED:
        raise ValueError("invalid_private_variant_set")
    successes = 0
    for i in range(4):
        candidate = private_dir / ("keyword-%d-private.shader" % i)
        if (candidate.is_symlink() or not candidate.is_file()
            or not 0 < candidate.stat().st_size <= MAX_SHADERLAB):
            raise ValueError("invalid_private_shaderlab_file")
        executable = extract(candidate.read_text(encoding="utf-8"))
        for stage in (1, 0):
            successes += compiler(executable, stage, private_dir) is True
    return {
        "schema_version": 1,
        "status": STATUS if successes == 8 else "INCONCLUSIVE",
        "original_private_candidate_files_examined": 4,
        "HLSLPROGRAM_macro_selected_stage_compiles_attempted": 8,
        "HLSLPROGRAM_macro_selected_stage_spirv_validations_passed": successes,
        "Unity_Editor_ShaderLab_import_proven": False,
        "original_keyword_routing_or_material_binding_proven": False,
        "original_pixels_on_Android_verified": False,
        "private_shader_text_or_compile_errors_published": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--private-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or not args.out.parent.is_dir()
        or args.out.resolve().is_relative_to(args.private_dir.resolve())):
        raise ValueError("unsafe_private_summary_output")
    try:
        report = verify(args.private_dir)
    except Exception:
        # Never expose path, source bytes, compiler stderr, or an exception
        # containing private owner names from runner-local staging.
        report = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "failure_code": "PRIVATE_STAGE_WRAPPER_UNCLASSIFIED",
                  "Unity_Editor_ShaderLab_import_proven": False,
                  "private_shader_text_or_compile_errors_published": False}
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("T3_PRIVATE_SHADERLAB_STAGE_WRAPPER_SAFE=" + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
