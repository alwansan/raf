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

from scripts.b49_shaderlab_pass_contract import pass_coverage, remove_comments
from scripts.b47_compute_kernel_contract import kernel_entrypoint_profile

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


def _regular_unlinked_asset(path: Path, assets: Path) -> bool:
    """Require a physical in-Assets file; do not follow linked metadata.

    A linked shader meta previously satisfied is_file() and could make an
    external sidecar appear to belong to an original water shader. Check
    every path component without resolving away symbolic link evidence.
    Missing ordinary sidecars still mean unsatisfied coverage, not an error.
    """
    try:
        path.relative_to(assets)
    except ValueError as error:
        raise ValueError("Water source path escapes Unity Assets") from error
    cursor = path
    while cursor != assets:
        if cursor.is_symlink():
            raise ValueError("Unsafe linked water source or metadata path")
        cursor = cursor.parent
    return path.is_file()


def _verified_water_meta(path: Path, assets: Path, seen_guids: set[str]) -> bool:
    """Structurally validate an original water .meta identity without publishing it.

    Physical existence is not enough: malformed, missing, ambiguous or duplicate
    Unity GUIDs cannot establish reliable Shader/Compute asset binding. This
    verifies syntax and uniqueness only, NOT original export provenance.
    """
    if not _regular_unlinked_asset(path, assets):
        return False
    if path.stat().st_size > 65536:
        raise ValueError("Oversized water shader/compute GUID metadata")
    lines = path.read_bytes().splitlines()
    guid_lines = [line for line in lines if line.startswith(b"guid:")]
    if len(guid_lines) != 1:
        raise ValueError("Missing or ambiguous water shader/compute GUID metadata")
    match = re.fullmatch(rb"guid:[ \t]*([0-9a-fA-F]{32})[ \t]*", guid_lines[0])
    if match is None:
        raise ValueError("Malformed water shader/compute GUID metadata")
    identity = match.group(1).decode("ascii").lower()
    if identity in seen_guids:
        raise ValueError("Duplicate water shader/compute GUID metadata")
    seen_guids.add(identity)
    return True


def inspect(project: Path) -> dict:
    assets = project / "Assets"
    if project.is_symlink() or assets.is_symlink() or not assets.is_dir():
        raise ValueError("Unity exported Assets folder missing or redirected")
    found = {}
    seen_water_guids = set()
    for path in assets.rglob("*.shader"):
        if not _regular_unlinked_asset(path, assets):
            raise ValueError("Unsafe source shader path")
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
        without_comments = remove_comments(raw)
        match = DECL.search(without_comments)
        if not match or match[1] not in REQUIRED_PASS_COUNT:
            continue
        name = match[1]
        if name in found:
            raise ValueError("Duplicate original shader name: " + name)
        # No shader text is printed or copied to this JSON result.
        coverage = pass_coverage(without_comments)
        found[name] = {
            **coverage,
            "has_program": coverage["passes_with_complete_program"] > 0,
            "original_meta_present": _verified_water_meta(Path(str(path) + ".meta"), assets, seen_water_guids),
            "export_placeholder": "No subprograms found" in raw,
        }
    shader_rows = {}
    for name, minimum in REQUIRED_PASS_COUNT.items():
        observed = found.get(name)
        # Shader.passCount is per active SubShader (Unity 2021.3); the
        # diagnostic sum of passes across alternate SubShaders is insufficient.
        # Selection is platform-dependent and unverified at source-check time:
        # fail closed unless every authored candidate meets the device index.
        valid = bool(observed and observed["subshader_pass_counts"]
                     and all(count >= minimum
                             for count in observed["subshader_pass_counts"])
                     and observed["all_subshaders_programmed"]
                     and observed["original_meta_present"]
                     and not observed["export_placeholder"])
        shader_rows[name] = {
            "required_passes_from_device_log": minimum,
            "observed": observed,
            "contract_satisfied": valid,
        }

    computes = []
    for path in assets.rglob("*.compute"):
        if not _regular_unlinked_asset(path, assets):
            raise ValueError("Unsafe source compute shader path")
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
        profile = kernel_entrypoint_profile(raw)
        meta = Path(str(path) + ".meta")
        computes.append({
            **profile,
            "is_water_or_fft_named": bool(re.search(r'(water|fft|spectrum|foam)', path.name, re.IGNORECASE)),
            "original_meta_present": (_verified_water_meta(meta, assets, seen_water_guids)
                                      if re.search(r"(water|fft|spectrum|foam)", path.name, re.IGNORECASE)
                                      else _regular_unlinked_asset(meta, assets)),
        })
    water_compute = [
        row for row in computes
        if row["is_water_or_fft_named"] and row["all_kernel_entrypoints_structural"]
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
        "compute_files_with_structural_entrypoints": sum(x["all_kernel_entrypoints_structural"] for x in computes),
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
