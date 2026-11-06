"""T2 synthetic controls for exact original private SPIR-V DescriptorSet-only patch."""
import struct
import tempfile
from pathlib import Path
import unittest

from scripts.t2_foam_private_descriptor_set_remap import (
    scan_binary_decorations, reflected_ids, relocate_fragment_sets,
    compare_before_after_reflection, source_preserving_stage_set,
    relocate_conflicting_only, verify_selective_reflection,
)
from scripts.t2_foam_embedded_descriptor_layout import (
    compare_cross_stage_descriptors,
)


def op(decor, target, val):
    return [(4 << 16) | 71, target, decor, val]


def binary():
    words = [0x07230203,0x00010300,0,32,0]
    words += op(33,6,1) + op(34,6,0)
    words += op(33,7,0) + op(34,7,0)
    words += [(1 << 16) | 0]
    return struct.pack("<%dI" % len(words),*words)


def old():
    return {
        "entryPoints":[{"name":"main","mode":"frag"}],
        "separate_samplers":[{"id":6,"set":0,"binding":1}],
        "ubos":[{"id":7,"set":0,"binding":0,"block_size":128}],
    }


def after():
    obj=old()
    for rows in (obj["separate_samplers"],obj["ubos"]):
        rows[0]["set"]=1
    return obj


def vertex():
    return {"entryPoints":[{"name":"main","mode":"vert"}],
            "ubos":[{"id":8,"set":0,"binding":0,"block_size":96},
                    {"id":9,"set":0,"binding":1,"block_size":64}]}


class PrivateSPIRVDecorationOnlyControls(unittest.TestCase):
    def test_exact_id_register_decorations_and_only_two_set_literals_change(self):
        before=binary()
        words,binding,sets,positions=scan_binary_decorations(before)
        self.assertEqual(sets,{6:0,7:0})
        self.assertEqual(binding,{6:1,7:0})
        patched,safe=relocate_fragment_sets(before,old(),1)
        new,original_bindings,new_sets,_=scan_binary_decorations(patched)
        self.assertEqual(new_sets,{6:1,7:1})
        self.assertEqual(original_bindings,binding)
        self.assertEqual(sum(a!=b for a,b in zip(words,new)),2)
        self.assertEqual({i for i,(a,b) in enumerate(zip(words,new)) if a!=b},
                         set(positions.values()))
        self.assertTrue(safe["original_Binding_and_non_descriptor_words_unchanged"])
        self.assertTrue(compare_before_after_reflection(old(),after(),1))

    def test_collision_before_relocation_and_none_after(self):
        before=compare_cross_stage_descriptors(vertex(),old())
        self.assertEqual(before["shared_descriptor_class_conflict_count"],1)
        self.assertEqual(before["shared_CB_buffer_extent_difference_count"],1)
        after_result=compare_cross_stage_descriptors(vertex(),after())
        self.assertEqual(after_result["shared_numeric_set_binding_count"],0)
        self.assertTrue(after_result["same_type_pipeline_descriptor_set_layout_possible"])

    def test_choose_an_unused_set_instead_of_guessing_fixed_set(self):
        self.assertEqual(source_preserving_stage_set(vertex()),1)
        v=vertex()
        v["ubos"].append({"id":10,"set":1,"binding":2,"block_size":64})
        self.assertEqual(source_preserving_stage_set(v),2)

    def test_wrong_reflection_id_binding_or_original_set_rejected(self):
        cases=[]
        x=old();x["separate_samplers"][0]["binding"]=8;cases.append(x)
        x=old();x["separate_samplers"][0]["id"]=10;cases.append(x)
        x=old();x["separate_samplers"][0]["set"]=1;cases.append(x)
        for x in cases:
            with self.subTest(case=x),self.assertRaises(ValueError):
                relocate_fragment_sets(binary(),x,1)

    def test_missing_optional_reflection_ids_uses_binary_numeric_coordinates(self):
        src=old()
        src["separate_samplers"][0].pop("id")
        src["ubos"][0].pop("id")
        patched,safe=relocate_fragment_sets(binary(),src,1)
        self.assertTrue(safe["descriptor_set_decorations_only_changed"])
        self.assertTrue(compare_before_after_reflection(src,{
            "entryPoints":[{"name":"main","mode":"frag"}],
            "separate_samplers":[{"set":1,"binding":1}],
            "ubos":[{"set":1,"binding":0,"block_size":128}]
        },1))
        self.assertNotEqual(binary(),patched)

    def test_invalid_SPIRV_magic_header_opcode_and_decorations(self):
        for patched in (
            b"", b"\x00"*20,
            binary()[:-1],
            binary()[:20] + struct.pack("<I",(0 << 16)|71)+binary()[24:],
        ):
            with self.subTest(size=len(patched)),self.assertRaises(ValueError):
                scan_binary_decorations(patched)
        old_binary=binary()
        words=list(struct.unpack("<%dI"%(len(old_binary)//4),old_binary))
        words[3]=1
        with self.assertRaises(ValueError):
            scan_binary_decorations(struct.pack("<%dI"%len(words),*words))

    def test_truncated_opdecorate_word_count_fails_closed(self):
        # Valid word boundaries but an invalid OpDecorate arity must not
        # silently bypass descriptor validation (including unknown modes).
        original = list(struct.unpack("<%dI" % (len(binary()) // 4), binary()))
        for count in (1, 2):
            with self.subTest(word_count=count):
                words = original[:5] + [((count << 16) | 71)]
                if count == 2:
                    words.append(6)
                words += original[9:]
                blob = struct.pack("<%dI" % len(words), *words)
                with self.assertRaisesRegex(ValueError,
                        "^malformed_private_descriptor_decoration$"):
                    scan_binary_decorations(blob)

    def test_duplicate_binding_or_set_decorations_rejected(self):
        for duplicate in (op(34,6,0),op(33,6,1)):
            words=list(struct.unpack("<%dI"%(len(binary())//4),binary()))
            words+=duplicate
            with self.assertRaises(ValueError):
                scan_binary_decorations(struct.pack("<%dI"%len(words),*words))

    def test_orphan_binding_without_set_rejected(self):
        words=list(struct.unpack("<%dI"%(len(binary())//4),binary()))
        index=words.index(34)
        del words[index-2:index+2]
        with self.assertRaises(ValueError):
            scan_binary_decorations(struct.pack("<%dI"%len(words),*words))

    def test_reflection_byte_range_or_id_drift_rejected(self):
        corrupted=after();corrupted["ubos"][0]["block_size"]=256
        with self.assertRaises(ValueError):
            compare_before_after_reflection(old(),corrupted,1)
        corrupted=after();corrupted["ubos"][0]["id"]=999
        with self.assertRaises(ValueError):
            compare_before_after_reflection(old(),corrupted,1)

    def test_invalid_target_set_fails_closed(self):
        for value in (0,16,True,-1,"1"):
            with self.subTest(value=value),self.assertRaises(ValueError):
                relocate_fragment_sets(binary(),old(),value)

    def test_unrecognized_unsafe_descriptor_category_rejected(self):
        corrupted=old();corrupted["push_constants"]=[{"id":99}]
        _, bindings, sets, _ = scan_binary_decorations(binary())
        with self.assertRaises(ValueError):
            reflected_ids(corrupted, bindings, sets, mode="frag")

    def test_repeated_source_binary_relocation_has_failsafe(self):
        once,_=relocate_fragment_sets(binary(),old(),1)
        with self.assertRaises(ValueError):
            relocate_fragment_sets(once,after(),1)


    def test_selective_remap_only_changes_conflicting_sampler_keeps_cb0(self):
        patched,collisions=relocate_conflicting_only(binary(),vertex(),old(),1)
        a,bindings,original_sets,sites=scan_binary_decorations(binary())
        b,after_bindings,after_sets,_=scan_binary_decorations(patched)
        self.assertEqual(len(collisions),1)
        self.assertEqual(sum(x!=y for x,y in zip(a,b)),1)
        self.assertEqual(bindings,after_bindings)
        self.assertEqual(after_sets[6],1)  # changed conflicting Sampler
        self.assertEqual(after_sets[7],0)  # unchanged source CB0
        report={
            "entryPoints":[{"name":"main","mode":"frag"}],
            "separate_samplers":[{"id":6,"set":1,"binding":1}],
            "ubos":[{"id":7,"set":0,"binding":0,"block_size":128}]
        }
        self.assertTrue(verify_selective_reflection(old(),report,collisions,1))
        self.assertEqual(compare_cross_stage_descriptors(vertex(),report)[
            "shared_CB_buffer_extent_difference_count"],1)
        self.assertEqual(compare_cross_stage_descriptors(vertex(),report)[
            "shared_descriptor_class_conflict_count"],0)

    def test_selective_reflection_cb0_wrong_set_or_extent_rejected(self):
        patched,conflicts=relocate_conflicting_only(binary(),vertex(),old(),1)
        x=after();x["ubos"][0]["block_size"]=128
        with self.assertRaises(ValueError):
            verify_selective_reflection(old(),x,conflicts,1)
        x={
            "entryPoints":[{"name":"main","mode":"frag"}],
            "separate_samplers":[{"id":6,"set":1,"binding":1}],
            "ubos":[{"id":7,"set":0,"binding":0,"block_size":256}]
        }
        with self.assertRaises(ValueError):
            verify_selective_reflection(old(),x,conflicts,1)

    def test_selective_used_target_or_reflection_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            relocate_conflicting_only(binary(),vertex(),old(),0)
        changed=old();changed["separate_samplers"][0]["binding"]=3
        with self.assertRaises(ValueError):
            relocate_conflicting_only(binary(),vertex(),changed,1)

    def test_selective_without_actual_conflict_not_accepted(self):
        match={"entryPoints":[{"name":"main","mode":"vert"}],
               "separate_samplers":[{"set":0,"binding":1}],
               "ubos":[{"set":0,"binding":0,"block_size":96}]}
        with self.assertRaises(ValueError):
            relocate_conflicting_only(binary(),match,old(),1)

if __name__=="__main__":
    unittest.main()
