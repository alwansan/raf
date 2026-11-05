"""T3 source-free authentic source->full native W1 original Shader48 GUID join tests.

Fixtures are artificial public integers, synthetic GUIDs and fake ShaderLab
profiles, never original game source or exported private trace.
"""
import json
import unittest

from scripts import t3_native_original_921_shader_target_audit as t3
from scripts import t3_original_renderer_shader_impact as source

SECRET="DO_NOT_EXPORT_PRIVATE_SHADER_NAME_OR_GUID"
ROOT_OWNER="sharedassets0.assets"


def fixture(*,top_dummy=True,top_passes=1,top_builtin=False):
    source_use={(ROOT_OWNER,i):35 for i in range(1,22)}
    source_use[ROOT_OWNER,1]=921
    source_use[ROOT_OWNER,21]=47
    assert len(source_use)==21 and sum(source_use.values())==1633
    report={"status":source.STATUS,
            "six_original_scenes_sha_verified":True,
            "original_distinct_typed_Shader48_targets":21,
            "counts":{"original_slots_to_verified_Shader48":1633},
            "original_nonnull_renderer_material_slots":1635}
    trace={"schema_version":1,
           "export_instance":"a"*32,
           "objects":[]}
    profile={}
    for i in range(1,22):
        guid=f"{i:032x}"
        file_id=4800000
        typ=3
        if i==1 and top_builtin:
            guid="0000000000000000e000000000000000"
            file_id=46
            typ=0
        trace["objects"].append({
           "class_id":48,
           "source":{"owner":ROOT_OWNER,"path_id":i},
           "export":{"file_id":file_id,"guid":guid,"type":typ},
           "exportable":True})
        if not(i==1 and top_builtin):
            count=top_passes if i==1 else 1
            d=top_dummy if i==1 else True
            profile[guid]={
              "dummy":d,
              "no_subprograms":False,
              "unknown_exporter":False,
              "unbalanced":False,
              "pass_count":count,
              "programmed":count,
              "partial_subshader_coverage":False}
    return source_use,report,(ROOT_OWNER,1),trace,profile


class NativeTopShaderJoinTests(unittest.TestCase):
    def checked(self,**options):
        args=fixture(**options)
        return t3.strict_native_top_join(*args[:3],*args[3:])

    def test_real_921_scope_fake_dummy_mapping(self):
        result=self.checked()
        self.assertEqual(result["status"],t3.STATUS)
        self.assertEqual(result["native_high_use_source_shader_export_status"],
                         "DUMMY_AFTER_NATIVE_RESTORERS")
        self.assertEqual(result["native_high_use_shaderlab_pass_count"],1)
        self.assertEqual(result["source_original_high_use_Shader48_passes"],4)
        self.assertFalse(result["native_high_use_shaderlab_pass_count_matches_original"])
        self.assertEqual(result["native_original_scene_shader_slots_to_dummy"],1633)
        self.assertEqual(result["native_original_scene_shader_slots_to_unity_builtin"],0)
        self.assertFalse(result["unity_compile_or_Android_pixels_proven"])

    def test_source_921_top_custom_nondummy_full_4passes_not_proved_authentic(self):
        result=self.checked(top_dummy=False,top_passes=4)
        self.assertEqual(result["native_high_use_source_shader_export_status"],
                         "NON_DUMMY_NATIVE_PROGRAM_AUTHENTICITY_UNPROVEN")
        self.assertTrue(result["native_high_use_shaderlab_pass_count_matches_original"])
        self.assertEqual(result["native_original_scene_shader_slots_to_non_dummy"],921)
        self.assertEqual(result["native_original_scene_shader_slots_to_dummy"],712)
        self.assertFalse(result["original_DXBC_to_native_shader_program_equivalence_proven"])

    def test_top_engine_transport_not_falsely_called_custom(self):
        result=self.checked(top_builtin=True)
        self.assertEqual(result["native_high_use_source_shader_export_status"],
                         "UNITY_BUILTIN_EXPORTED_PROGRAM_AUTHENTICITY_UNPROVEN")
        self.assertIsNone(result["native_high_use_shaderlab_pass_count"])
        self.assertIsNone(result["native_high_use_shaderlab_has_dummy_exporter_marker"])
        self.assertEqual(result["native_original_scene_shader_slots_to_unity_builtin"],921)

    def test_top_builtin_null_or_zero_guid_cannot_be_called_valid_engine_shader(self):
        valid="0000000000000000e000000000000000"
        for fid,guid in ((0,valid),(0,"0"*32),(46,"0"*32),(-1,valid)):
            args=list(fixture(top_builtin=True))
            args[3]["objects"][0]["export"]={
                "file_id":fid,"guid":guid,"type":0}
            with self.subTest(fileid=fid,zero_guid=guid=="0"*32):
                with self.assertRaises(ValueError):
                    t3.strict_native_top_join(*args)

    def test_missing_actual_exported_top_shader_meta_is_rejected(self):
        args=list(fixture())
        args[4].pop(f"{1:032x}")
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args)

    def test_extra_source_shader48_trace_duplicate_rejected(self):
        args=list(fixture())
        args[3]["objects"].append(dict(args[3]["objects"][0]))
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args)

    def test_traced_source_identity_cannot_be_forged(self):
        args=list(fixture())
        args[3]["objects"][0]["source"]["path_id"]=999
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args)

    def test_unpaired_original_high_use_source_rejected(self):
        args=list(fixture())
        args[2]=(ROOT_OWNER,2)
        with self.assertRaisesRegex(ValueError,"unmatched_original_top921"):
            t3.strict_native_top_join(*args)

    def test_duplicate_synthetic_shader_GUID_from_two_originals_rejected(self):
        args=list(fixture())
        args[3]["objects"][1]["export"]["guid"]=f"{1:032x}"
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args)

    def test_ambiguous_private_trace_instance_rejected(self):
        for instance in ("",SECRET,"a"*31,"a"*33,None):
            args=list(fixture())
            args[3]["export_instance"]=instance
            with self.subTest(instance=repr(instance)),self.assertRaises(ValueError):
                t3.strict_native_top_join(*args)

    def test_boolean_or_string_native_pass_count_rejected(self):
        for bad in (True,"4",-1,513):
            args=list(fixture())
            args[4][f"{1:032x}"]["pass_count"]=bad
            with self.subTest(value=repr(bad)),self.assertRaises(ValueError):
                t3.strict_native_top_join(*args)

    def test_private_unknown_profile_key_wrong_types_rejected(self):
        for key,bad in (("dummy",1),("unbalanced","false"),("programmed",True),
                        ("partial_subshader_coverage",None)):
            args=list(fixture())
            args[4][f"{1:032x}"][key]=bad
            with self.subTest(field=key),self.assertRaises(ValueError):
                t3.strict_native_top_join(*args)

    def test_source_origin_shader_slot_number_not_guessable_from_export_doc(self):
        args=list(fixture())
        args[0][ROOT_OWNER,1]=920
        args[0][ROOT_OWNER,21]=48
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args)

    def test_not_proven_current_native_export_solely_by_old_bounded_vendor_run(self):
        result=self.checked(top_dummy=False,top_passes=3)
        self.assertFalse(result["native_high_use_shaderlab_pass_count_matches_original"])
        self.assertFalse(result["original_DXBC_to_native_shader_program_equivalence_proven"])
        self.assertFalse(result["unity_compile_or_Android_pixels_proven"])

    def test_marker_free_shader_without_programs_must_not_count_as_restored(self):
        for no_subprograms, programmed in ((True, 4), (False, 0), (True, 0)):
            args=list(fixture(top_dummy=False, top_passes=4))
            top_profile=args[4][f"{1:032x}"]
            top_profile["no_subprograms"]=no_subprograms
            top_profile["programmed"]=programmed
            with self.subTest(no_subprograms=no_subprograms, programmed=programmed):
                with self.assertRaisesRegex(ValueError, "non_dummy_native_shader_without_subprograms"):
                    t3.strict_native_top_join(*args)

    def test_dummy_marker_remains_classified_dummy_even_if_no_subprograms(self):
        args=list(fixture(top_dummy=True, top_passes=4))
        top_profile=args[4][f"{1:032x}"]
        top_profile["no_subprograms"]=True
        top_profile["programmed"]=0
        result=t3.strict_native_top_join(*args)
        self.assertEqual(result["native_high_use_source_shader_export_status"],
                         "DUMMY_AFTER_NATIVE_RESTORERS")

    def test_marker_free_unknown_or_unbalanced_profile_is_inconclusive(self):
        for field in ("unknown_exporter", "unbalanced"):
            args=list(fixture(top_dummy=False, top_passes=4))
            args[4][f"{1:032x}"][field]=True
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "non_dummy_native_shader_ambiguous_export_profile"):
                    t3.strict_native_top_join(*args)

    def test_dummy_marker_remains_dummy_with_unknown_exporter(self):
        args=list(fixture(top_dummy=True, top_passes=4))
        args[4][f"{1:032x}"]["unknown_exporter"]=True
        args[4][f"{1:032x}"]["unbalanced"]=True
        result=t3.strict_native_top_join(*args)
        self.assertEqual(result["native_high_use_source_shader_export_status"],
                         "DUMMY_AFTER_NATIVE_RESTORERS")

    def test_marker_free_partial_subshader_coverage_is_inconclusive(self):
        args=list(fixture(top_dummy=False, top_passes=4))
        args[4][f"{1:032x}"]["partial_subshader_coverage"]=True
        with self.assertRaisesRegex(ValueError, "non_dummy_native_shader_incomplete_program_coverage"):
            t3.strict_native_top_join(*args)

    def test_marker_free_missing_program_in_pass_is_inconclusive(self):
        args=list(fixture(top_dummy=False, top_passes=4))
        args[4][f"{1:032x}"]["programmed"]=3
        with self.assertRaisesRegex(ValueError, "non_dummy_native_shader_incomplete_program_coverage"):
            t3.strict_native_top_join(*args)

    def test_dummy_marker_stays_dummy_despite_partial_sibling_or_missing_pass_program(self):
        args=list(fixture(top_dummy=True, top_passes=4))
        args[4][f"{1:032x}"]["partial_subshader_coverage"]=True
        args[4][f"{1:032x}"]["programmed"]=3
        result=t3.strict_native_top_join(*args)
        self.assertEqual(result["native_high_use_source_shader_export_status"],
                         "DUMMY_AFTER_NATIVE_RESTORERS")
        self.assertTrue(result["native_high_use_shaderlab_partial_subshader_coverage"])

    def test_safe_aggregate_does_not_leak_private_identity_or_guid(self):
        result=self.checked()
        encoded=json.dumps(result,sort_keys=True)
        for value in (ROOT_OWNER,SECRET,f"{1:032x}","private_trace", "export_instance", "path_id"):
            self.assertNotIn(value,encoded)
        self.assertFalse(result["private_original_names_GUIDs_ids_hashes_disclosed"])

    def test_wrong_version_or_missing_source_population_rejected(self):
        args=list(fixture())
        args[1]["counts"]["original_slots_to_verified_Shader48"]=1632
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args)
        args=list(fixture())
        args[3]["schema_version"]=2
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args)

    def test_private_original_bad_pass_count_rejected(self):
        args=list(fixture())
        with self.assertRaises(ValueError):
            t3.strict_native_top_join(*args,original_passes=5)


if __name__=="__main__":
    unittest.main()
