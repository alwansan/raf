"""W2 fail-closed tests for the empty-config (base-variant) materials probe.

Synthetic only: shader identity via m_ParsedForm.m_Name (top-level m_Name
serialized empty in this build), same-file/external/unresolvable bucket
resolution, Standard base-variant counting, texture-emptiness split,
byte-length histograms and leak guards.
"""

from __future__ import annotations

import json
import types
import unittest

from scripts.probe_w2_empty_config_materials import (
    SCHEMA_VERSION,
    _shader_identity,
    build_indexes,
    classify_materials,
    external_paths,
    resolve_shader,
)


def _obj(path_id, type_name, tree):
    o = types.SimpleNamespace()
    o.path_id = path_id
    o.type = types.SimpleNamespace(name=type_name)
    o.read_typetree = lambda check_read=True: tree
    o.get_raw_data = lambda: b"r" * 123
    return o


def env(objects, externals=()):
    e = types.SimpleNamespace(objects=objects)
    e.file = types.SimpleNamespace(
        externals=[types.SimpleNamespace(path=p) for p in externals])
    return e


class ShaderIdentityTests(unittest.TestCase):
    def test_parsed_form_name_preferred(self):
        self.assertEqual(_shader_identity({"m_ParsedForm": {"m_Name": "Standard"},
                                           "m_Name": ""}), "Standard")
        self.assertEqual(_shader_identity({"m_Name": "Old Name"}), "Old Name")
        self.assertEqual(_shader_identity({}), "")
        self.assertEqual(_shader_identity(None), "")

    def test_index_and_resolution(self):
        e = env([_obj(7, "Shader", {"m_ParsedForm": {"m_Name": "Standard"}}),
                 _obj(8, "Shader", {"m_Name": ""})])
        idx = build_indexes("a.assets", e)
        self.assertEqual(idx, {7: "Standard", 8: "<unnamed-shader>"})
        nested = {"a.assets": idx, "b.assets": idx}
        self.assertEqual(external_paths(env([], externals=())), [])
        self.assertEqual(resolve_shader("a.assets", {"m_FileID": 0, "m_PathID": 7},
                                        nested, []), "Standard")
        self.assertEqual(resolve_shader("a.assets", {"m_FileID": 1, "m_PathID": 7},
                                        nested, ["dir/b.assets"]), "Standard")
        self.assertEqual(resolve_shader("a.assets", {"m_FileID": 1, "m_PathID": 7},
                                        {}, ["b.assets"]), "<unresolvable-external>")
        self.assertEqual(resolve_shader("a.assets", {"m_FileID": 9, "m_PathID": 1},
                                        {}, []), "<out-of-range>")
        self.assertEqual(resolve_shader("a.assets", None, {}, []), "<no-shader-pptr>")
        self.assertEqual(resolve_shader("a.assets", {"m_FileID": 0, "m_PathID": 99},
                                        {"a.assets": idx}, []), "<unresolvable-same-file>")

    def test_external_paths_normalized(self):
        e = env([], externals=("Library/unity default resources", "b.assets"))
        self.assertEqual(external_paths(e), ["unity default resources", "b.assets"])


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.standard_marker = {"m_FormatHash": 1}

    def test_standard_base_variant_counts_and_split(self):
        def std_material(tex_slots):
            saved = {"m_TexEnvs": [("_MainTex", {"m_Texture": {"m_FileID": 0, "m_PathID": pid},
                                                 "m_Scale": 1, "m_Offset": 1})
                                   for pid in tex_slots],
                     "m_Floats": [], "m_Colors": [], "m_Ints": []}
            tree = {"m_Shader": {"m_FileID": 0, "m_PathID": 900},
                    "m_ValidKeywords": [],
                    "m_InvalidKeywords": ["stale"],
                    "m_CustomRenderQueue": -1,
                    "m_LightmapFlags": 4,
                    "m_EnableInstancingVariants": False,
                    "m_DoubleSidedGI": True,
                    "m_SavedProperties": saved}
            return tree
        objs = [
            _obj(10, "Material", std_material([0, 0, 0, 0])),   # base, all slots null
            _obj(11, "Material", std_material([55], )),        # populated? no: keywords empty -> base, some bound
            _obj(12, "Material", dict(std_material([0]), m_ValidKeywords=["a"])),  # configured default
            _obj(13, "Material", {"m_Shader": {"m_FileID": 0, "m_PathID": 901},
                                  "m_ValidKeywords": []}),      # other shader, empty
            _obj(900, "Shader", {"m_ParsedForm": {"m_Name": "Standard"}}),
            _obj(901, "Shader", {"m_ParsedForm": {"m_Name": "Other"}}),
        ]
        e = env(objs)
        indexes = {"a.assets": build_indexes("a.assets", e)}
        scan = classify_materials("a.assets", e, indexes)
        self.assertEqual(SCHEMA_VERSION, 1)
        self.assertEqual(scan["materials"], 4)
        self.assertEqual(scan["standardReferences"], 3)
        self.assertEqual(scan["standardBaseVariant"], 2)
        self.assertEqual(scan["keywordEmptyByShaderName"], {"Standard": 2, "Other": 1})
        self.assertEqual(scan["baseVariantTextureEmptinessSplit"],
                         {"all-slots-null": 1, "some-bound": 1})
        self.assertEqual({str(k): v for k, v in scan["baseVariantRenderQueueHistogram"].items()}, {"-1": 2})
        self.assertEqual({str(k): v for k, v in scan["baseVariantLightmapFlagsHistogram"].items()}, {"4": 2})
        self.assertEqual({str(k): v for k, v in scan["baseVariantInstancingHistogram"].items()}, {"0": 2})
        self.assertEqual({str(k): v for k, v in scan["baseVariantDoubleSidedGIHistogram"].items()}, {"1": 2})
        self.assertEqual({str(k): v for k, v in scan["baseVariantInvalidKeywordSizes"].items()}, {"1": 2})
        self.assertEqual(scan["baseVariantOwners"], {"a.assets": 2})
        self.assertEqual({str(k): v for k, v in scan["baseVariantRecordByteLengthHistogram"].items()}, {"123": 2})
        self.assertEqual({str(k): v for k, v in scan["configuredRecordByteLengthHistogram"].items()}, {"123": 2})
        self.assertEqual(scan["unresolvableShaderRefs"], 0)

    def test_no_leak_keys(self):
        objs = [_obj(10, "Material", {"m_Shader": {"m_FileID": 0, "m_PathID": 900},
                                      "m_ValidKeywords": [], "m_InvalidKeywords": [],
                                      "m_SavedProperties": {}}),
                _obj(900, "Shader", {"m_ParsedForm": {"m_Name": "Standard"}})]
        e = env(objs)
        indexes = {"a.assets": build_indexes("a.assets", e)}
        scan = classify_materials("a.assets", e, indexes)
        blob = json.dumps(scan)
        for forbidden in ("m_Texture", "m_Color", "m_Scale", "m_Offset",
                          "m_ParsedForm", "m_Floats", "m_TexEnvs"):
            self.assertNotIn(forbidden, blob)


if __name__ == "__main__":
    unittest.main()
