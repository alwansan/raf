"""Exercise production Python function bodies with authored, in-memory inputs.

AST loading isolates the route contracts from unavailable Unity/asset readers.
The injected source transforms and module decoder are test doubles: these are
not translation, SPIR-V, Unity, runtime material or game-pixel receipts.
"""
import ast
import itertools
import json
from pathlib import Path
import re
import unittest
from unittest.mock import Mock

from scripts.gt_runtime_keyword_contract import (
    exact_independent_toggle_plan, strict_bundle_route_key, strict_engine_router,
)

ROOT = Path(__file__).resolve().parents[1]
COUNTS = (512, 4, 128, 512)
MODES = ("ForwardBase", "ForwardAdd", "Deferred", "ShadowCaster")


def production_function(filename, name, **namespace):
    path = ROOT / "scripts" / filename
    parsed = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    matches = [node for node in parsed.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        raise AssertionError("expected one actual production function: " + name)
    tree = ast.Module(body=matches, type_ignores=[])
    exec(compile(tree, str(path), "exec"), namespace)
    return namespace[name]


def keys_for_pass(p, n):
    names = [f"SOURCE_P{p}_K{i}" for i in range(n)]
    keys = [tuple(name for name, enabled in zip(names, bits) if enabled)
            for bits in itertools.product((False, True), repeat=n)]
    return keys[1:] + keys[:1]


class MemoryPath:
    def __init__(self, files, path=""):
        self.files = files
        self.path = path

    def __truediv__(self, part):
        return MemoryPath(self.files, self.path + "/" + part if self.path else part)

    def read_text(self, encoding="utf-8"):
        return self.files[self.path]

    def read_bytes(self):
        return self.files[self.path]


def authored_composer_inputs():
    files, pairs, routes, original_names = {}, [], [], []
    for p, n in enumerate((9, 2, 7, 9)):
        keys = keys_for_pass(p, n)
        original_names.extend(sorted(set().union(*map(set, keys))))
        routes.append({"subshader": 0, "pass": p, "routes": []})
        for r, key in enumerate(keys):
            entry = {"enabled": list(key), "vs": "program-000", "fs": "program-001"}
            metadata = {"m_KeywordIndices": sorted(original_names.index(name) for name in key)}
            pair = {"subshader": 0, "pass": p}
            for offset, stage in enumerate(("vs", "fs")):
                pair[stage] = {"program_ref": entry[stage], "original_variant_metadata": metadata}
                files[f"bound-stage-{len(pairs) * 2 + offset:03d}/resource-bound.hlsl"] = (
                    f"main() {{}}\nGT_MARKER_{stage}_P{p}_R{r}")
            pairs.append(pair)
            routes[-1]["routes"].append(entry)
    files["program-000/source.dxbc"] = b"authored-test-placeholder-not-bytecode"
    files["original-private-layout.txt"] = "\n// Original stage programs attach here\n" * 4
    files["original-private-keyword-routes.json"] = json.dumps(routes)
    files["original-private-variant-manifest.json"] = json.dumps({
        "paired": pairs, "original_shader_ParsedForm_full_private": {"m_KeywordNames": original_names}})
    files["original-private-parameter-records.json"] = json.dumps({"stage_records": [{}] * (2 * len(pairs))})
    return MemoryPath(files)


def compose_function(route_keys, router):
    def diagnostic_not_expected(*args):
        raise AssertionError("legacy selector path entered for NEXT23b strict candidate")
    return production_function(
        "gt_original_921_shaderlab.py", "compose", json=json, re=re,
        verified_source_next23b_pass_modes=lambda manifest: MODES,
        paired_uniform_layouts=lambda records: [{}, {}],
        rebind_constant_buffers=lambda source, layout, **kw: source,
        restore_vertex_inputs=lambda source, placeholder: (source, None),
        unity_varying_semantics=lambda source: source,
        pin_varying_locations=lambda source, stage: source,
        unity_resource_bindings=lambda source, stage: source,
        engine_route_keys=route_keys,
        combine_stages=lambda vs, fs: vs.splitlines()[1] + "\n" + fs.splitlines()[1],
        strict_engine_router=router, routed_stage=diagnostic_not_expected,
        pass_coverage=lambda shader: {
            "subshader_pass_counts": [shader.count("HLSLPROGRAM")],
            "passes_with_complete_program": shader.count("ENDHLSL")},
    )


def manifest_packet():
    return {"passes": [{"passType": mode, "variants": [{"keywords": list(key)} for key in keys_for_pass(p, n)]}
                       for p, (mode, n) in enumerate(zip(MODES, (9, 2, 7, 9)))]}


def verifier():
    return production_function(
        "gt_verify_921_shader_bundle.py", "verify_routes", EXPECTED_ROUTES=COUNTS,
        stage_variants=lambda rows: rows,
        strict_bundle_route_key=strict_bundle_route_key,
        vulkan_execution_models=lambda authored_placeholder, decoder: {0, 4},
    )


def bundle_fixture(rows):
    return {"m_KeywordNames": ["A", "OTHER_PASS"], "m_SubShaders": [{"m_Passes": [{
        stage: [(0, i, {"m_KeywordIndices": indices, "m_BlobIndex": blob})
                for i, (indices, blob) in enumerate(rows)]
        for stage in ("progVertex", "progFragment")}]}]}


class RuntimeKeywordProductionIntegration(unittest.TestCase):
    def test_next23b_composer_uses_strict_branch_for_all_four_passes(self):
        router = Mock(wraps=strict_engine_router)
        compose = compose_function(lambda row, index, modes: [tuple(route["enabled"]) for route in row["routes"]], router)
        shader = compose(authored_composer_inputs(), engine_keywords=True)
        self.assertEqual(router.call_count, 4)
        self.assertEqual([len(call.args[0]) for call in router.call_args_list], list(COUNTS))
        self.assertEqual(shader.count("#error Unmapped_original_keyword_set"), 4)
        self.assertNotIn("GT_ORIGINAL_921_", shader)
        for p, call in enumerate(router.call_args_list):
            keys, programs = call.args
            self.assertTrue(keys[0])
            self.assertEqual(keys[-1], ())
            for r in range(len(keys)):
                self.assertEqual(programs[r], f"GT_MARKER_vs_P{p}_R{r}\nGT_MARKER_fs_P{p}_R{r}")

    def test_next23b_composer_refuses_unproved_lattice(self):
        def sparse(row, index, modes):
            keys = [tuple(route["enabled"]) for route in row["routes"]]
            if index == 0:
                keys[0] = ("UNMAPPED_EXTRA",)
            return keys
        compose = compose_function(sparse, strict_engine_router)
        with self.assertRaisesRegex(ValueError, "sparse_keyword_lattice"):
            compose(authored_composer_inputs(), engine_keywords=True)

    def test_production_manifest_rejects_sparse_or_invalid_names(self):
        gate = production_function("gt_verify_921_shader_bundle.py", "validate_next23b_engine_manifest",
                                   exact_independent_toggle_plan=exact_independent_toggle_plan)
        gate(manifest_packet())
        for replacement in (["UNMAPPED_EXTRA"], ["invalid keyword"]):
            packet = manifest_packet()
            packet["passes"][0]["variants"][0]["keywords"] = replacement
            with self.assertRaises(ValueError):
                gate(packet)

    def test_strict_verifier_rejects_old_projection_false_accept(self):
        gate = verifier()
        expected = [{frozenset(), frozenset({"A"})}]
        entries = [(None, b"authored-program-zero"), (None, b"authored-program-one")]
        result = gate(bundle_fixture([([], 0), ([0], 1)]), entries, expected, "test-double", (2,), strict_engine=True)
        self.assertEqual(result["vertex_routes_by_pass"], [2])
        self.assertEqual(result["fragment_routes_by_pass"], [2])
        wrong = bundle_fixture([([], 0), ([0, 1], 1)])
        self.assertEqual(gate(wrong, entries, expected, "test-double", (2,))["vertex_routes_by_pass"], [2])
        with self.assertRaisesRegex(ValueError, "unmapped_exact_keyword_set"):
            gate(wrong, entries, expected, "test-double", (2,), strict_engine=True)

    def test_strict_verifier_rejects_ambiguous_program_and_missing_route(self):
        gate = verifier()
        expected = [{frozenset(), frozenset({"A"})}]
        entries = [(None, bytes([i])) for i in range(3)]
        with self.assertRaisesRegex(ValueError, "ambiguous_keyword_program"):
            gate(bundle_fixture([([], 0), ([0], 1), ([0], 2)]), entries, expected, "test-double", (2,), strict_engine=True)
        with self.assertRaisesRegex(ValueError, "engine_routes_missing"):
            gate(bundle_fixture([([], 0)]), entries, expected, "test-double", (2,), strict_engine=True)
        with self.assertRaisesRegex(ValueError, "exact_engine_manifest_required"):
            gate(bundle_fixture([([], 0)]), entries, None, "test-double", (2,), strict_engine=True)


if __name__ == "__main__":
    unittest.main()
