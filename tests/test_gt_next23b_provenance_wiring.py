"""Exercise production function bodies with synthetic metadata and test doubles."""
import ast
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import traceback
import types
import unittest
from unittest.mock import Mock, patch

from scripts.gt_next23b_route_provenance import (
    COUNTS, bind_candidate_route_manifest, verify_candidate_route_manifest,
    verify_bundle_metadata,
)
from test_gt_next23b_route_provenance import fixture, encoded

ROOT = Path(__file__).resolve().parents[1]


def function(file, name, **namespace):
    path = ROOT / "scripts" / file
    tree = ast.parse(path.read_text(encoding="utf-8"))
    matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    if len(matches) != 1:
        raise AssertionError("Expected one actual function: " + name)
    exec(compile(ast.Module(body=matches, type_ignores=[]), str(path), "exec"), namespace)
    return namespace[name]


class Next23bProvenanceWiring(unittest.TestCase):
    def setUp(self):
        self.source, self.routes = fixture()
        self.source_bytes = encoded(self.source)
        self.shader = b"authored candidate -- no real compiled shader"

    def producer(self, modes):
        packet = [{"routes": [{"vs": "V", "fs": "F", "enabled": route["keywords"]}
                              for route in p["variants"]]} for p in self.routes["passes"]]
        verify = Mock()
        compose = function(
            "gt_next23b_private_stage_translation.py", "compose_private", json=json, traceback=traceback,
            STATUS="SOURCE_TEST_SUCCESS", keyword_routes=lambda *a: (packet, {"source_exact_keyword_routes_by_pass": list(COUNTS)}),
            shaderlab_layout=lambda *a, **kw: ("authored layout", {}), compile_routed_stages=lambda *a: 2312,
            stage_parameter_records=lambda *a: {"original_variant_stages_with_parameter_records": 2312,
                "original_vertex_fragment_varying_records_matched": 0, "named_constant_buffer_reflected_offsets_verified": 0},
            compose=lambda *a, **kw: self.shader.decode(), verified_source_next23b_pass_modes=lambda _: modes,
            engine_route_keys=lambda row, *a: [route["enabled"] for route in row["routes"]],
            bind_candidate_route_manifest=bind_candidate_route_manifest, verify_entrypoints=verify)
        return compose, verify

    def test_producer_seals_exact_source_and_candidate_and_does_not_claim_runtime(self):
        compose, check = self.producer([p["passType"] for p in self.routes["passes"]])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "original-private-variant-manifest.json").write_bytes(self.source_bytes)
            report = compose({}, [], [], [], [], {"V": "program-000", "F": "program-067"}, root, {}, engine_keywords=True)
            packet = json.loads((root / "Next23bEngineRoutes.json").read_text())
            verify_candidate_route_manifest(self.source_bytes, self.shader, packet)
            check.assert_called_once()
        self.assertEqual(report["status"], "SOURCE_TEST_SUCCESS")
        self.assertTrue(report["engine_keyword_candidate_names_match_source_packet"])
        self.assertFalse(report["original_runtime_engine_keywords_preserved"])

    def test_producer_rejects_disagreeing_pass_type_before_entrypoint_gate(self):
        modes = [p["passType"] for p in self.routes["passes"]]
        modes[0] = "Deferred"
        compose, check = self.producer(modes)
        dummy = types.ModuleType("scripts.t3_particle108_source_propstate")
        dummy.PrivateContractError = type("PrivateContractError", (Exception,), {})
        dummy.CATEGORIES = ()
        with tempfile.TemporaryDirectory() as d, patch.dict(sys.modules, {dummy.__name__: dummy}):
            root = Path(d)
            (root / "original-private-variant-manifest.json").write_bytes(self.source_bytes)
            report = compose({}, [], [], [], [], {"V": "program-000", "F": "program-067"}, root, {}, engine_keywords=True)
            self.assertFalse((root / "Next23bEngineRoutes.json").exists())
            check.assert_not_called()
        self.assertEqual(report["status"], "INCONCLUSIVE_NEXT23B_PRIVATE_COMPOSITION")
        self.assertEqual(report["composition_safe_checkpoint"], "independent_source_keyword_route_provenance")

    def inspect_with(self, *, mutate=None, missing_source=False, stale=False):
        parsed = copy.deepcopy(self.source["original_shader_ParsedForm_full_private"])
        parsed["m_Name"] = "Authored/Fixture"
        if mutate:
            mutate(parsed)
        obj = types.SimpleNamespace(type=types.SimpleNamespace(name="Shader"),
                                    read_typetree=lambda: {"m_ParsedForm": parsed, "platforms": [18]})
        unity = types.ModuleType("UnityPy")
        unity.load = Mock(return_value=types.SimpleNamespace(objects=[obj]))
        route_check = Mock(return_value={"vertex_routes_by_pass": list(COUNTS)})
        inspect = function("gt_verify_921_shader_bundle.py", "inspect", json=json, sha256=sha256,
                           exported_shader_identity=lambda _: "Authored/Fixture", decoded_platforms=lambda _: [(18, [])],
                           records=lambda _: [], validate_next23b_engine_manifest=lambda _: None,
                           verify_candidate_route_manifest=verify_candidate_route_manifest,
                           verify_bundle_metadata=verify_bundle_metadata, verify_routes=route_check)
        with tempfile.TemporaryDirectory() as d, patch.dict(sys.modules, {"UnityPy": unity}):
            root = Path(d)
            source = root / "shader"
            source.write_bytes(self.shader)
            original = root / "source-metadata.json"
            original.write_bytes(self.source_bytes + (b"\n" if stale else b""))
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"unityVersion": "2021.3.45f2", "passCount": 4, "errors": 0,
                "registeredRoutes": 1156, "privateBundleCompiled": True, "androidVulkanOnly": True,
                "candidateSha256": sha256(self.shader).hexdigest()}))
            manifest = root / "engine.json"
            manifest.write_text(json.dumps(bind_candidate_route_manifest(self.source_bytes, self.shader, self.routes)[0]))
            try:
                result = inspect(root / "not-a-real-bundle", source, receipt, manifest, "mock-decoder",
                                 next23b=True, source_variant_manifest=None if missing_source else original)
            except ValueError as exc:
                route_check.assert_not_called()
                if missing_source:
                    unity.load.assert_not_called()
                return str(exc)
            route_check.assert_called_once()
            return result

    def test_bundle_verifier_requires_source_commitment_and_metadata(self):
        result = self.inspect_with()
        self.assertEqual(result["bundle_serialized_pass_tags_matched"], 4)
        self.assertEqual(result["bundle_used_keyword_flag_bytes_matched"], 27)
        self.assertFalse(result["original_keyword_scope_verified"])
        self.assertFalse(result["original_runtime_keyword_selection_verified"])
        self.assertIn("independent_source_variant_manifest", self.inspect_with(missing_source=True))
        self.assertIn("commitment_mismatch", self.inspect_with(stale=True))
        self.assertIn("bundle_keyword_flag_byte_mismatch", self.inspect_with(mutate=lambda p: p["m_KeywordFlags"].__setitem__(0, 99)))
        self.assertIn("bundle_pass_lightmode_mismatch", self.inspect_with(mutate=lambda p: p["m_SubShaders"][0]["m_Passes"][0]["m_State"]["m_Tags"]["tags"][0].__setitem__(1, "Deferred")))


if __name__ == "__main__":
    unittest.main()
