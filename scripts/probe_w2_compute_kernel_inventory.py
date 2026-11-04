"""Aggregate the serialized compute-kernel inventory of the original game's
ComputeShader providers (FFT-FORMAT-009 / WATER-001 support).

Purpose: complete the item W4's compute-provider note left open —
"serialized kernel tables read as zero via read_typetree ...; kernel
identity must come from the compiled program records". Direct typetree
inspection shows the serialized ``variants[].kernels`` list *does* resolve
kernel identity (names, variant map, keyword lists), so the host-side
dispatch inventory is recoverable CPU-only without any compiled blob.

Per provider, aggregate-only outputs (kernel and provider names are engine
packaging metadata — the API surface the restorer must bind; consistent
with W3's keyword-name and W4's gate-identity precedents):
- provider name, kernel count, ordered kernel-name list;
- distinct kernel-name count, total variantMap entries;
- per-kernel global/local keyword counts (no keyword strings);
- serialized constant-buffer count.

Fail-closed: variants list shaped exactly one entry per provider, every
kernel entry has a non-empty string name, variantMap entries are present,
unknown fields hard-fail. All three LFS-verified owners (sha committed
object identity via ``git show HEAD``): sharedassets0 (DX11 FFT),
resources (7 water/SSS/OIT/compute providers), sharedassets29 (CSMain).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from scripts.probe_w2_fullgame_texture_colors import (
    sha256_file,
    validate_owner_names,
    verify_and_hash,
)

SCHEMA_VERSION = 1

OWNERS = ("sharedassets0.assets", "resources.assets", "sharedassets29.assets")

_FORBIDDEN = ("m_PathID", "m_Shader", "stringTagMap", "m_ValidKeywords")


def aggregate_provider(name: str, tree: dict) -> dict:
    variants = tree.get("variants")
    if not isinstance(variants, list) or len(variants) != 1:
        raise ValueError(f"{name}: expected exactly one serialized variant row")
    variant = variants[0]
    kernels = variant.get("kernels")
    if not isinstance(kernels, list) or not kernels:
        raise ValueError(f"{name}: empty kernels table")
    names: list[str] = []
    per_kernel: list[dict] = []
    for kernel in kernels:
        kernel_name = kernel.get("name")
        if not isinstance(kernel_name, str) or not kernel_name:
            raise ValueError(f"{name}: kernel entry without a usable name")
        for key in kernel:
            if key not in {"name", "globalKeywords", "localKeywords", "variantMap"}:
                raise ValueError(f"{name}: unexpected kernel field {key!r}")
        variant_map = kernel.get("variantMap")
        if not isinstance(variant_map, list) or len(variant_map) != 1:
            raise ValueError(f"{name}: kernel {kernel_name!r} variantMap depth deviates")
        names.append(kernel_name)
        per_kernel.append(
            {
                "name": kernel_name,
                "globalKeywords": len(kernel.get("globalKeywords", [])),
                "localKeywords": len(kernel.get("localKeywords", [])),
                "variantMapEntries": len(variant_map),
            }
        )
    constant_buffers_value = variant.get("constantBuffers")
    cb_count = len(constant_buffers_value) if isinstance(constant_buffers_value, list) else 0
    return {
        "providerName": tree.get("m_Name", ""),
        "kernelCount": len(kernels),
        "distinctKernelNames": len(set(names)),
        "kernelNames": names,
        "perKernel": per_kernel,
        "serializedConstantBuffers": cb_count,
    }


def aggregate_owner(owner: Path) -> dict:
    import UnityPy

    env = UnityPy.load(str(owner))
    providers = []
    for obj in env.objects:
        if obj.type.name != "ComputeShader":
            continue
        providers.append(aggregate_provider(f"{owner.name}@{obj.path_id}", obj.read_typetree()))
    total_kernels = sum(p["kernelCount"] for p in providers)
    return {"providerCount": len(providers), "totalKernels": total_kernels, "providers": providers}


def probe(source: Path, repo: Path, repo_rel_prefix: str) -> dict:
    owners = {}
    for name in OWNERS:
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing owner: {path}")
        verify_and_hash(path, repo, f"{repo_rel_prefix}/{name}")
        owners[name] = aggregate_owner(path)
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "owners": owners,
    }
    blob = json.dumps(result)
    for forbidden in _FORBIDDEN:
        if forbidden in blob:
            raise ValueError(f"forbidden output key leaked: {forbidden}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="original Raft_Data root")
    parser.add_argument("--repo", required=True, help="repo worktree for identity cross-check")
    parser.add_argument("--repo-rel-prefix", default="Raft/Raft_Data")
    parser.add_argument("--out", required=True, help="aggregate JSON path")
    args = parser.parse_args(argv)
    result = probe(Path(args.source), Path(args.repo), args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"aggregate_written": str(out), "no_proprietary_payload": True,
                      "kernels": sum(o["totalKernels"] for o in result["owners"].values())}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
