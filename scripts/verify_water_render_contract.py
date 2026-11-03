"""Fail-closed audit for original water shader passes observed missing on Android.

No shader source is generated, rewritten, downloaded or published. The exact
pass-index minima are grounded in the owner's November 2 device error log.
This gate is intended to run AFTER authored shader restorations but BEFORE
an expensive Unity native build when the owner eventually authorizes one.
"""
import argparse
import json
from pathlib import Path
import re

# Unity logs show requests for these maximum pass indices. Valid index N
# requires a restored ShaderLab source with at least N+1 authored passes.
REQUIRED_PASS_COUNT = {
    "UltimateWater/Spectrum/Water Spectrum": 6,  # logged index 5
    "UltimateWater/Utilities/Blur (Subsurface Scattering)": 2,  # 1
    "UltimateWater/Foam/Global": 2,  # 1
    "UltimateWater/Depth/Depth Copy": 4,  # 3
    "Sandbox/VolumetricLight": 5,  # 4; separate authenticated restore exists
}
DECL = re.compile(r'\bShader\s+"([^"\r\n]+)"')
PASS = re.compile(r'\bPass\s*\{')
PROGRAM = re.compile(r'\b(?:CGPROGRAM|HLSLPROGRAM)\b')
KERNEL = re.compile(r'^\s*#\s*pragma\s+kernel\s+\w+', re.MULTILINE)


def inspect(project: Path) -> dict:
    assets = project / "Assets"
    if not assets.is_dir():
        raise ValueError("Unity exported Assets folder absent")
    found = {}
    for path in assets.rglob("*.shader"):
        if path.is_symlink() or not path.is_file():
            raise ValueError("Unsafe source shader path")
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
        match = DECL.search(raw)
        if not match or match[1] not in REQUIRED_PASS_COUNT:
            continue
        name = match[1]
        if name in found:
            raise ValueError("Duplicate original shader name: " + name)
        # No shader text is printed or copied to this JSON result.
        without_comments = re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*', '', raw)
        found[name] = {
            "pass_count": len(PASS.findall(without_comments)),
            "has_program": bool(PROGRAM.search(without_comments)),
            "original_meta_present": Path(str(path) + ".meta").is_file(),
            "export_placeholder": "No subprograms found" in raw,
        }
    shader_rows = {}
    for name, minimum in REQUIRED_PASS_COUNT.items():
        observed = found.get(name)
        valid = bool(observed and observed["pass_count"] >= minimum
                     and observed["has_program"]
                     and observed["original_meta_present"]
                     and not observed["export_placeholder"])
        shader_rows[name] = {
            "required_passes_from_device_log": minimum,
            "observed": observed,
            "contract_satisfied": valid,
        }

    computes = []
    for path in assets.rglob("*.compute"):
        if path.is_symlink() or not path.is_file():
            raise ValueError("Unsafe source compute shader path")
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
        without_comments = re.sub(r'/\*[\s\S]*?\*/|//[^\r\n]*', '', raw)
        kernels = KERNEL.findall(without_comments)
        computes.append({
            "kernel_count": len(kernels),
            "is_water_or_fft_named": bool(re.search(r'(water|fft|spectrum|foam)', path.name, re.IGNORECASE)),
            "original_meta_present": Path(str(path) + ".meta").is_file(),
        })
    water_compute = [
        row for row in computes
        if row["is_water_or_fft_named"] and row["kernel_count"] > 0
        and row["original_meta_present"]
    ]
    # This is a structural source check, not proof of authentic ownership,
    # original GUID matching, GPU compilation, or correct FFT output.
    return {
        "shader_contracts": shader_rows,
        "all_logged_shader_pass_requirements_satisfied": all(
            row["contract_satisfied"] for row in shader_rows.values()),
        "compute_source_files": len(computes),
        "compute_files_with_kernels": sum(x["kernel_count"] > 0 for x in computes),
        "water_named_compute_sources_with_kernels": len(water_compute),
        "water_compute_source_candidate_present": bool(water_compute),
        "authentic_water_kernel_identity_verified": False,
        "device_execution_verified": False,
        "modified_source": False,
    }


def native_ready(report):
    # Even convincing-looking source with the right pass count is not proof
    # it matches Raft's original serialized shader GUID, FFT index order or
    # gameplay material contracts. Until an authenticated recovery can attest
    # those identities, a synthetic shader must never clear the native gate.
    return (
        report["all_logged_shader_pass_requirements_satisfied"]
        and report["water_compute_source_candidate_present"]
        and report["authentic_water_kernel_identity_verified"]
    )



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    result = inspect(args.project)
    print("RAFT_ORIGINAL_WATER_RENDER_GATE " + json.dumps(result, sort_keys=True))
    if args.strict and not native_ready(result):
        raise SystemExit("Original water rendering contract incomplete or unauthenticated: verify original shader passes, GPU kernels and identities before native Unity build")


if __name__ == "__main__":
    main()
