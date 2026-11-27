"""Exercise the published NEXT23b editor and receipt verifier on authored assets only."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from test_gt_next23b_route_provenance import fixture, encoded
from scripts.gt_runtime_keyword_contract import strict_engine_router
from scripts.gt_next23b_route_provenance import bind_candidate_route_manifest, verify_candidate_route_manifest
from scripts.gt_next23b_unity_receipt import (
    read_snapshot, strict_json, verify_unity_receipt, MAX_SOURCE_BYTES,
    MAX_MANIFEST_BYTES, MAX_RECEIPT_BYTES, MAX_BUNDLE_BYTES,
)

NAME = "GT/AuthoredNext23bReceipt"
EDITOR = ROOT / "android-port/Experiments/GT/Editor/Next23bShaderValidation.cs"


def make_inputs():
    source, routes = fixture()
    # Authored global keywords, not an inference about the game's scope.
    flags = source["original_shader_ParsedForm_full_private"]["m_KeywordFlags"]
    flags[:] = [0] * len(flags)
    blocks = [f'Shader "{NAME}" {{', 'SubShader {']
    for p, row in enumerate(routes["passes"]):
        # Nonempty first route: route zero is not the empty-keyword default.
        variants = row["variants"]
        variants[:] = variants[1:] + variants[:1]
        keys = [v["keywords"] for v in variants]
        programs = {r: f"#define GT_PROBE_ROUTE {r + 1}.0" for r in range(len(keys))}
        pragmas, code = strict_engine_router(keys, programs)
        blocks.extend(['Pass {', f'Name "AUTHORED_PASS_{p}"',
                       'Tags { "LightMode" = "' + row["passType"] + '" }',
                       'Cull Off ZWrite Off', 'HLSLPROGRAM', '#pragma target 4.5',
                       '#pragma vertex gt_vert', '#pragma fragment gt_frag', *pragmas, code,
                       'float4 gt_vert(float4 p:POSITION):SV_POSITION {',
                       '    p.x += GT_PROBE_ROUTE / 4096.0; return p;', '}',
                       'float4 gt_frag():SV_Target {',
                       f'    return float4(GT_PROBE_ROUTE / 1024.0, {p}.0 / 4.0, 0.25, 1.0);',
                       '}', 'ENDHLSL', '}'])
    blocks += ['}', 'Fallback Off', '}']
    shader = ('\n'.join(blocks) + '\n').encode()
    source_bytes = encoded(source)
    manifest, report = bind_candidate_route_manifest(source_bytes, shader, routes)
    route_bytes = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    return shader, source_bytes, route_bytes, report


def stage(project, out):
    if project.exists() or project.is_symlink() or out.exists() or out.is_symlink():
        raise ValueError("fresh_synthetic_project_and_report_required")
    shader, source, routes, proof = make_inputs()
    files = {
        "Assets/GTNext23b.shader": shader,
        "Assets/Editor/Next23bShaderValidation.cs": EDITOR.read_bytes(),
        "Packages/manifest.json": b'{"dependencies":{}}\n',
        "ProjectSettings/ProjectVersion.txt": b"m_EditorVersion: 2021.3.45f2\n",
        "Next23bEngineRoutes.json": routes,
        "SyntheticSourceManifest.json": source,
    }
    for name, value in files.items():
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value)
    report = dict(status="AUTHORED_PROJECT_PREPARED", synthetic_only=True,
                  Unity_run_executed=False, original_assets_read=False,
                  XAPK_requested=False, route_counts=proof["source_routes_by_pass"],
                  input_sha256={name: sha256(value).hexdigest() for name, value in files.items()})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report


def verify(project, out, run_id):
    import UnityPy
    from scripts.gt_next23b_route_provenance import verify_bundle_metadata
    if out.exists() or out.is_symlink():
        raise ValueError("fresh_verification_report_required")
    expected_shader, expected_source, expected_routes, _ = make_inputs()
    shader = read_snapshot(project / "Assets/GTNext23b.shader", MAX_SOURCE_BYTES)
    source = read_snapshot(project / "SyntheticSourceManifest.json", MAX_SOURCE_BYTES)
    routes = read_snapshot(project / "Next23bEngineRoutes.json", MAX_MANIFEST_BYTES)
    if (shader, source, routes) != (expected_shader, expected_source, expected_routes):
        raise ValueError("authored_fixture_bytes_changed")
    receipt = strict_json(read_snapshot(project / "ProbeResults/gt-next23b-unity-safe.json", MAX_RECEIPT_BYTES))
    bundle = read_snapshot(project / "ProbeResults/Private/gt-next23b", MAX_BUNDLE_BYTES)
    proof = verify_unity_receipt(receipt, shader, routes, source, bundle)
    packet = strict_json(routes)
    verify_candidate_route_manifest(source, shader, packet)
    # Real bundle decoding, no mocks. Test same-size bundle substitution before decoder.
    for field, items in (
        ("bundleSha256", (shader, routes, source, bytes([bundle[0] ^ 1]) + bundle[1:])),
        ("engineRouteManifestSha256", (shader, routes + b"\n", source, bundle)),
    ):
        try:
            verify_unity_receipt(receipt, *items)
        except ValueError as exc:
            if field + "_mismatch" not in str(exc):
                raise
        else:
            raise ValueError("synthetic_negative_control_accepted")
    env = UnityPy.load(bundle)
    shaders = [obj.read_typetree() for obj in env.objects if obj.type.name == "Shader"]
    matches = [obj for obj in shaders if obj["m_ParsedForm"]["m_Name"] == NAME]
    if len(matches) != 1 or list(matches[0]["platforms"]) != [18]:
        raise ValueError("authored_android_vulkan_bundle_shader_missing_or_ambiguous")
    # Save the separately proven receipt + decode result even if the stricter
    # serialized metadata/route checks subsequently discover incompatibilities.
    report = dict(status="SYNTHETIC_EDITOR_RECEIPT_AND_BUNDLE_DECODE_VERIFIED",
                  synthetic_only=True, ci_run_id=run_id, UnityPy_version=getattr(UnityPy, "__version__", "unknown"),
                  actual_bundle_decoded=True, android_vulkan_serialized_platform=18,
                  same_size_bundle_and_manifest_negative_controls=2,
                  bundle_sha256=sha256(bundle).hexdigest(), original_assets_read=False,
                  original_runtime_keyword_selection_verified=False, game_pixels_verified=False,
                  XAPK_requested=False, **proof)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    meta = verify_bundle_metadata(source, matches[0]["m_ParsedForm"], packet)
    report.update(meta, status="SYNTHETIC_EDITOR_RECEIPT_BUNDLE_AND_METADATA_VERIFIED")
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("stage", "verify"))
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--run-id")
    a = p.parse_args()
    if a.command == "stage":
        result = stage(a.project, a.out)
    else:
        if not a.run_id:
            p.error("verify requires CI run identity")
        result = verify(a.project, a.out, a.run_id)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
