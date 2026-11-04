"""B25 Foam original render-state staging negative/positive synthetic controls."""
import copy
import hashlib
import tempfile
from pathlib import Path
import unittest
from scripts.b24_original_foam_stage_translation import TARGET
from scripts.b25_foam_pass_state import inspect, save_private

def v(value, name="<noninit>"):
    return {"name": name, "val": value}

def state():
    blend = dict(srcBlend=v(1), destBlend=v(0), srcBlendAlpha=v(1),
                 destBlendAlpha=v(0), blendOp=v(0), blendOpAlpha=v(0), colMask=v(15))
    stencil = {"comp":v(8), "pass":v(0), "fail":v(0), "zFail":v(0)}
    return dict(m_Name="", m_LOD=0, m_Tags={"tags":[]}, rtSeparateBlend=False,
                rtBlend0=blend, alphaToMask=v(0), zClip=v(1), zTest=v(0),
                zWrite=v(1), culling=v(2), offsetFactor=v(0), offsetUnits=v(0),
                fogMode=-1, fogColor={"name":"<noninit>", **{axis:v(0) for axis in "xyzw"}},
                fogDensity=v(0), fogStart=v(0), fogEnd=v(0),
                stencilRef=v(0), stencilReadMask=v(255), stencilWriteMask=v(255),
                stencilOp=stencil, stencilOpFront=copy.deepcopy(stencil),
                stencilOpBack=copy.deepcopy(stencil), lighting=False)

def fixture():
    a = state()
    b = copy.deepcopy(a)
    b["zWrite"] = v(0)
    return {"m_Name":TARGET, "m_SubShaders":[{"m_Passes":[
        {"m_Type":0, "m_State":a}, {"m_Type":0, "m_State":b}]}]}

class Tests(unittest.TestCase):
    def test_two_private_state_texts_and_hashes(self):
        report, texts = inspect(fixture())
        self.assertEqual(report["original_passes"],2)
        self.assertEqual(len(texts),2)
        self.assertNotEqual(report["states"][0]["sha256"],report["states"][1]["sha256"])
        for row,text in zip(report["states"],texts):
            self.assertEqual(row["sha256"],hashlib.sha256(text.encode()).hexdigest())
        self.assertFalse(report["shaderlab_installed"])
        self.assertFalse(report["state_source_published"])

    def test_private_staging_exact_and_no_clobber(self):
        _, texts = inspect(fixture())
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).absolute()
            save_private(root,texts)
            self.assertEqual((root/"foam-pass-00-state.txt").read_text(),texts[0])
            with self.assertRaisesRegex(ValueError,"already exists"):
                save_private(root,texts)

    def test_private_root_symlink_rejected(self):
        _, texts=inspect(fixture())
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/"dest"
            dest.mkdir()
            link=Path(d)/"linked"
            link.symlink_to(dest,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,"Unsafe"):
                save_private(link,texts)

    def test_bad_identity(self):
        x=fixture()
        x["m_Name"]="Fake/Other"
        with self.assertRaisesRegex(ValueError,"identity"):
            inspect(x)

    def test_bad_subshader_topology(self):
        x=fixture()
        x["m_SubShaders"] *= 2
        with self.assertRaisesRegex(ValueError,"subshader"):
            inspect(x)

    def test_bad_pass_count(self):
        for count in (0,1,3):
            with self.subTest(count=count):
                x=fixture()
                x["m_SubShaders"][0]["m_Passes"]=(x["m_SubShaders"][0]["m_Passes"]*3)[:count]
                with self.assertRaisesRegex(ValueError,"two-pass"):
                    inspect(x)

    def test_bad_pass_kind(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1
        with self.assertRaisesRegex(ValueError,"pass kind"):
            inspect(x)

    def test_missing_state(self):
        x=fixture()
        del x["m_SubShaders"][0]["m_Passes"][0]["m_State"]
        with self.assertRaisesRegex(ValueError,"render state"):
            inspect(x)

    def test_unsupported_color_mask(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["m_State"]["rtBlend0"]["colMask"]=v(7)
        with self.assertRaises(ValueError):
            inspect(x)

    def test_nan_state_rejected(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["m_State"]["offsetFactor"]=v(float("nan"))
        with self.assertRaises(ValueError):
            inspect(x)

    def test_unsafe_dynamic_property_rejected(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["m_State"]["zWrite"]=v(1,"bad ] \n Name")
        with self.assertRaises(ValueError):
            inspect(x)

if __name__=="__main__":
    unittest.main()
