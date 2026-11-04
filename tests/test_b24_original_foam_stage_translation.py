"""B24 original Foam program-stage link controls, all synthetic fixtures."""
import tempfile
from pathlib import Path
import unittest
from scripts.b24_original_foam_stage_translation import TARGET, inspect, validate_stage


def program(stage):
    layout = ((160,2,0),(176,0,1),(368,0,1)) if stage == 1 else ((160,2,0),)
    buffers, refs = [], []
    for slot, (size, vectors, matrices) in enumerate(layout):
        buffers.append(dict(m_Size=size, m_IsPartialCB=True, m_NameIndex=slot,
                            m_VectorParams=[0]*vectors, m_MatrixParams=[0]*matrices))
        refs.append(dict(m_NameIndex=slot, m_Index=slot, m_ArraySize=1))
    return dict(m_PlayerSubPrograms=[[dict(m_BlobIndex=1, m_KeywordIndices=[])]],
                m_ParameterBlobIndices=[[0]],
                m_CommonParameters=dict(m_ConstantBuffers=buffers, m_ConstantBufferBindings=refs))


def original():
    second = dict(m_Type=0, progVertex=program(1), progFragment=program(0))
    for key in ("progVertex", "progFragment"):
        second[key]["m_CommonParameters"]["m_ConstantBuffers"][0]["m_VectorParams"] = [0]
    return dict(m_Name=TARGET, m_SubShaders=[dict(m_Passes=[
        dict(m_Type=0, progVertex=program(1), progFragment=program(0)),
        second
    ])])


class OriginalFoamStageTests(unittest.TestCase):
    def test_four_original_program_pairs_private_and_unique(self):
        def link(meta, entries, stage):
            return b"DXBC" + bytes([stage])*40, dict(blob_index=1)
        def translator(code, stage, private):
            self.assertTrue(private.is_dir())
            return dict(vulkan11_valid=True, hlsl_recovered=True, roundtrip_vulkan11_valid=True)
        with tempfile.TemporaryDirectory() as folder:
            data = inspect(original(), [(0,b"dummy-parameter")], Path(folder),
                           link=link, translator=translator,
                           parse=lambda raw: {"synthetic": True})
        self.assertEqual(len(data), 4)
        self.assertEqual({(x["pass"],x["stage_code"]) for x in data},
                         {(0,0),(0,1),(1,0),(1,1)})
        self.assertTrue(all(not x["source_published"] for x in data))

    def test_reject_missing_or_extra_pass(self):
        for count in (0,1,3):
            game = original()
            passes = game["m_SubShaders"][0]["m_Passes"]
            game["m_SubShaders"][0]["m_Passes"] = (passes*3)[:count]
            with tempfile.TemporaryDirectory() as folder:
                with self.assertRaisesRegex(ValueError, "two-pass count"):
                    inspect(game, [(0,b"dummy")], Path(folder))

    def test_reject_forged_shader_identity(self):
        game = original()
        game["m_Name"] = "Fake/Foam"
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "identity"):
                inspect(game, [(0,b"dummy")], Path(folder))

    def test_reject_modified_cb_shape_and_partial_flag(self):
        for field, new in (("m_Size",159),("m_IsPartialCB",False),
                           ("m_VectorParams",[]),("m_NameIndex",9)):
            with self.subTest(field=field):
                data = program(1)
                data["m_CommonParameters"]["m_ConstantBuffers"][0][field] = new
                with self.assertRaisesRegex(ValueError, "partial-CB"):
                    validate_stage(data, 1)

    def test_reject_invalid_cb_slot_or_array_size(self):
        for field, new in (("m_Index",9),("m_ArraySize",2)):
            data = program(0)
            data["m_CommonParameters"]["m_ConstantBufferBindings"][0][field] = new
            with self.assertRaisesRegex(ValueError, "partial-CB"):
                validate_stage(data, 0)

    def test_reject_fake_variant_and_keyword(self):
        data = program(0)
        data["m_PlayerSubPrograms"][0].append(dict(m_BlobIndex=2,m_KeywordIndices=[]))
        with self.assertRaisesRegex(ValueError, "variant"):
            validate_stage(data, 0)
        data = program(0)
        data["m_PlayerSubPrograms"][0][0]["m_KeywordIndices"] = [4]
        with self.assertRaisesRegex(ValueError, "keyword"):
            validate_stage(data, 0)

    def test_two_original_passes_have_distinct_exact_vector_member_counts(self):
        for stage_code in (0, 1):
            baseline = program(stage_code)
            self.assertIsNotNone(validate_stage(baseline, stage_code,
                                                {"original_pass": 0}))
            second = program(stage_code)
            second["m_CommonParameters"]["m_ConstantBuffers"][0]["m_VectorParams"] = [0]
            diag = {"original_pass": 1}
            self.assertIsNotNone(validate_stage(second, stage_code, diag))
            self.assertEqual(diag["original_second_pass_vector_members"], 1)
            for count in (0, 2, 3, 10):
                second["m_CommonParameters"]["m_ConstantBuffers"][0]["m_VectorParams"] = [0] * count
                with self.assertRaisesRegex(ValueError, "partial-CB"):
                    validate_stage(second, stage_code, {"original_pass": 1})
            with self.assertRaisesRegex(ValueError, "partial-CB"):
                validate_stage(second, stage_code, {"original_pass": 0})

    def test_reject_missing_parameter_table(self):
        data = program(1)
        data["m_ParameterBlobIndices"] = []
        with self.assertRaisesRegex(ValueError, "parameter table"):
            validate_stage(data, 1)

    def test_reject_non_original_pass_kind_or_missing_stage(self):
        game = original()
        game["m_SubShaders"][0]["m_Passes"][0]["m_Type"] = 4
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "pass kind"):
                inspect(game, [(0,b"dummy")], Path(folder))
        game = original()
        del game["m_SubShaders"][0]["m_Passes"][0]["progVertex"]
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "stage absent"):
                inspect(game, [(0,b"dummy")], Path(folder))


if __name__ == "__main__":
    unittest.main()
