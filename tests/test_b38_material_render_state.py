"""B38 render-state exact-value regression, synthetic identities only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import copy
import unittest

from scripts.b38_material_render_state import normalize_state, compare, exported_states

SRC = ("sharedassets0.assets", 15)
DST = (2100000, "a" * 32)


def example():
    t = {"schema_version":1, "export_instance":"f"*32, "objects":[{
        "class_id":21,
        "source":{"owner":SRC[0],"path_id":SRC[1]},
        "export":{"file_id":DST[0],"guid":DST[1],"type":2},
        "exportable":True
    }]}
    s = {SRC:normalize_state({"m_CustomRenderQueue":-1, "m_LightmapFlags":4,
                              "m_EnableInstancingVariants":False, "m_DoubleSidedGI":True})}
    d = {DST:normalize_state({"m_CustomRenderQueue":-1, "m_LightmapFlags":4,
                             "m_EnableInstancingVariants":0, "m_DoubleSidedGI":1})}
    return t,s,d


def write_export(root, body):
    folder = Path(root)/"Assets"
    folder.mkdir()
    p = folder/"scene.asset"
    p.write_text("%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n"+body, encoding="utf-8")
    (folder/"scene.asset.meta").write_text("fileFormatVersion: 2\nguid: "+"a"*32+"\n")
    return p


BODY = ("  m_CustomRenderQueue: -1\n  m_LightmapFlags: 4\n"
        "  m_EnableInstancingVariants: 0\n  m_DoubleSidedGI: 1\n")


class B38MaterialRenderStateTests(unittest.TestCase):
    def test_flags_bool_and_int_equivalent(self):
        t,s,e=example()
        r=compare(t,s,e)
        self.assertTrue(r["source_render_state_preserved"])
        self.assertEqual(r["actual_exported_materials_compared"],1)
        self.assertNotIn("sharedassets0",str(r))
        self.assertFalse(r["shader_pixels_unity_or_device_verified"])

    def test_queue_drift_is_detected(self):
        t,s,e=example()
        e[DST]["m_CustomRenderQueue"]=3000
        r=compare(t,s,e)
        self.assertEqual((r["queue_value_mismatches"],r["mismatched_materials"]),(1,1))
        self.assertFalse(r["source_render_state_preserved"])

    def test_lightmap_instancing_and_gi_drift_is_detected(self):
        t,s,e=example()
        e[DST].update(m_LightmapFlags=0,m_EnableInstancingVariants=1,m_DoubleSidedGI=0)
        r=compare(t,s,e)
        self.assertEqual((r["lightmap_flags_mismatches"],r["instancing_flags_mismatches"],
                          r["double_sided_gi_mismatches"]),(1,1,1))
        self.assertEqual(r["mismatched_materials"],1)

    def test_missing_and_invalid_flags_rejected(self):
        t,s,e=example()
        obj=copy.deepcopy(s[SRC])
        obj.pop("m_CustomRenderQueue")
        with self.assertRaisesRegex(ValueError,"Missing"):normalize_state(obj)
        obj=s[SRC].copy()
        obj["m_LightmapFlags"]=True
        with self.assertRaisesRegex(ValueError,"integer"):normalize_state(obj)
        obj=s[SRC].copy()
        obj["m_DoubleSidedGI"]=2
        with self.assertRaisesRegex(ValueError,"Boolean"):normalize_state(obj)

    def test_untrusted_trace_identity_rejected(self):
        t,s,e=example()
        t["export_instance"]="fake"
        with self.assertRaisesRegex(ValueError,"same-instance"):compare(t,s,e)
        t,s,e=example()
        t["objects"].append(copy.deepcopy(t["objects"][0]))
        with self.assertRaisesRegex(ValueError,"duplicated original"):compare(t,s,e)

    def test_exported_embedded_material_document(self):
        with TemporaryDirectory() as tmp:
            write_export(tmp,BODY)
            self.assertEqual(exported_states(Path(tmp)),{DST:normalize_state({
                "m_CustomRenderQueue":-1,"m_LightmapFlags":4,
                "m_EnableInstancingVariants":0,"m_DoubleSidedGI":1})})

    def test_duplicate_render_queue_yaml_key_rejected(self):
        with TemporaryDirectory() as tmp:
            write_export(tmp,BODY+"  m_CustomRenderQueue: 2000\n")
            with self.assertRaisesRegex(ValueError,"Malformed exported Material YAML"):
                exported_states(Path(tmp))

    def test_exported_missing_render_field_rejected(self):
        with TemporaryDirectory() as tmp:
            write_export(tmp,BODY.replace("  m_CustomRenderQueue: -1\n",""))
            with self.assertRaisesRegex(ValueError,"Missing"):exported_states(Path(tmp))

    def test_unsafe_symlink_rejected(self):
        with TemporaryDirectory() as tmp:
            folder=Path(tmp)/"Assets"
            folder.symlink_to(Path(tmp),target_is_directory=True)
            with self.assertRaisesRegex(ValueError,"Unsafe"):exported_states(Path(tmp))


if __name__=="__main__":
    unittest.main()
