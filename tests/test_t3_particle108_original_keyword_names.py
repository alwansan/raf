"""Synthetic only: original Shader48 keyword table mapping, no actual names."""
import json
import unittest
from scripts import t3_particle108_original_keyword_names as m


def stage(indexes):
    return {"m_SubPrograms":[{"m_KeywordIndices":list(v),
             "m_GlobalKeywordIndices":[],"m_LocalKeywordIndices":[]}
             for v in indexes],
            "m_PlayerSubPrograms":[]}


def parsed(names=None,flags=None,*,with_names=True,with_flags=True,
           rows=None):
    values=[[],[0],[1],[0,1]] if rows is None else rows
    out={"m_SubShaders":[{"m_Passes":[{
        "m_Type":0,"progVertex":stage(values),
        "progFragment":stage(list(reversed(values)))}]}]}
    if with_names:out["m_KeywordNames"]=["SYNTH_LEFT","SYNTH_RIGHT"] if names is None else names
    if with_flags:out["m_KeywordFlags"]=[0,0] if flags is None else flags
    return out


class TableProvenance(unittest.TestCase):
    def test_synthetic_two_switches_table_mapping(self):
        r=m.classify(parsed())
        self.assertTrue(r["original_switch_index_to_name_table_mapping_proven"])
        self.assertEqual(r["table_category"],"TWO_SWITCH_INDEX_NAMES_FOUND_WITH_FLAGS_UNINTERPRETED")
        self.assertEqual(r["keyword_table_size"],2)
        self.assertFalse(r["original_index_name_to_unity_directive_or_global_scope_proven"])

    def test_both_fields_absent_proves_no_mapping_not_failure(self):
        r=m.classify(parsed(with_names=False,with_flags=False))
        self.assertEqual(r["table_category"],"BOTH_FIELDS_ABSENT_ORIGINAL_SERIALIZATION")
        self.assertFalse(r["original_switch_index_to_name_table_mapping_proven"])

    def test_only_one_field_present_not_guessed(self):
        for a,b in ((True,False),(False,True)):
            with self.subTest(a=a,b=b):
                r=m.classify(parsed(with_names=a,with_flags=b))
                self.assertEqual(r["table_category"],"PARTIAL_KEYWORD_NAME_FLAG_FIELDS")
                self.assertFalse(r["original_switch_index_to_name_table_mapping_proven"])

    def test_wrong_name_and_flag_types_rejected(self):
        for key,kwargs in (("names",{"names":"string"}),("flags",{"flags":"byte"})):
            with self.subTest(key=key):
                self.assertEqual(m.classify(parsed(**kwargs))["table_category"],
                                 "INVALID_KEYWORD_NAME_FLAG_FIELD_TYPES")

    def test_out_of_bounds_switch_is_not_mapped(self):
        r=m.classify(parsed(names=["ONLY_ONE"], flags=[0]))
        self.assertEqual(r["table_category"],"ORIGINAL_SWITCH_INDEX_OUTSIDE_TABLE")
        self.assertFalse(r["original_switch_index_to_name_table_mapping_proven"])

    def test_duplicate_keyword_names_are_ambiguous(self):
        r=m.classify(parsed(names=["SYNTH","SYNTH"],flags=[0,0]))
        self.assertEqual(r["table_category"],"DUPLICATED_OR_AMBIGUOUS_KEYWORD_NAME")

    def test_name_is_strict_legal_identifier(self):
        for unsafe in ("#pragma shader", "contains space","N\nNEXT", "", "8BAD",True):
            with self.subTest(name=unsafe):
                r=m.classify(parsed(names=[unsafe,"SYNTH"],flags=[0,0]))
                self.assertEqual(r["table_category"],"UNSAFE_OR_NONIDENTIFIER_SOURCE_KEYWORD_NAME")

    def test_bad_flag_type_or_length_untrusted(self):
        for flags in ([0], [0,True], [0,-1], [0,256]):
            with self.subTest(flags=flags):
                r=m.classify(parsed(flags=flags))
                self.assertEqual(r["table_category"],"UNTRUSTED_NAME_FLAG_ROW_PARITY")

    def test_extra_table_entries_not_unknown_keywords(self):
        r=m.classify(parsed(names=["A","B","C"],flags=[0,0,1]))
        self.assertTrue(r["original_switch_index_to_name_table_mapping_proven"])
        self.assertEqual(r["keyword_table_size"],3)
        self.assertFalse(r["original_index_name_to_unity_directive_or_global_scope_proven"])

    def test_unexpected_global_namespace_rejected(self):
        p=parsed()
        p["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_SubPrograms"][1]["m_GlobalKeywordIndices"]=[7]
        with self.assertRaisesRegex(ValueError,"namespace|mismatch"):
            m.classify(p)

    def test_not_4_true_source_pairs_fail_closed(self):
        p=parsed(rows=[[],[0],[1]])
        with self.assertRaises(ValueError): m.classify(p)

    def test_fields_absent_never_make_unity_or_android_claim(self):
        r=m.classify(parsed(with_names=False,with_flags=False))
        for key in ("original_index_name_to_unity_directive_or_global_scope_proven",
                    "original_material_keyword_variant_runtime_binding_proven",
                    "Unity_Editor_compile_or_Android_GPU_pixels_proven"):
            self.assertFalse(r[key])

    def test_safe_report_never_prints_synthetic_private_keyword_identifiers(self):
        r=m.classify(parsed(names=["PRIV_ALPHA","PRIV_BETA"],flags=[0,1]))
        blob=json.dumps(r,sort_keys=True)
        for fragment in ("PRIV_ALPHA","PRIV_BETA","m_KeywordNames\":",
                         "m_KeywordFlags\":"):
            self.assertNotIn(fragment,blob)
        self.assertFalse(r["source_keyword_names_indices_flags_shader_text_or_paths_published"])


if __name__=="__main__":
    unittest.main()
