"""B30 source-free FFT variantMap routing controls, no original assets."""
import unittest
from scripts.b30_fft_variantmap_routing import summarize_routing, GROUPS

def fixture(kind="all_equal"):
    rows=[]
    for i in range(20):
        keys=[] if kind=="all_equal" else [f"group-{i//2}"]
        rows.append({"name":"synthetic-shared","globalKeywords":keys,"localKeywords":[],
          "variantMap":[(1,{"bin":list(b"DXBC"+bytes([i])*60),"group":(GROUPS[i],1,1)})]})
    return {"variants":[{"kernels":rows}]}

class Routing(unittest.TestCase):
    def test_shared_tags_cannot_establish_runtime_ids(self):
        r=summarize_routing(fixture())
        self.assertEqual(r["original_compiled_slots"],20)
        self.assertEqual(r["header_and_keyword_combined_unique_combinations"],1)
        self.assertEqual(r["header_and_keyword_collision_sizes"],[20])
        self.assertEqual(r["source_candidate_adjacent_pairs_with_same_discriminator"],10)
        self.assertEqual(r["source_candidate_cross_bank_positions_with_same_discriminator"],10)
        self.assertFalse(r["runtime_findkernel_id_to_compiled_slot_verified"])

    def test_pair_keywords_cannot_prove_runtime_mapping(self):
        r=summarize_routing(fixture("pair"))
        self.assertEqual(r["header_and_keyword_combined_unique_combinations"],10)
        self.assertEqual(r["header_and_keyword_collision_sizes"],[2]*10)
        self.assertEqual(r["source_candidate_adjacent_pairs_with_same_discriminator"],10)
        self.assertEqual(r["source_candidate_cross_bank_positions_with_same_discriminator"],0)
        self.assertFalse(r["keyword_identity_is_runtime_selector_verified"])

    def test_wrong_original_group_order_rejected(self):
        f=fixture("pair");rows=f["variants"][0]["kernels"];rows[0],rows[2]=rows[2],rows[0]
        with self.assertRaises(ValueError): summarize_routing(f)

    def test_duplicate_keyword_rejected(self):
        f=fixture();f["variants"][0]["kernels"][0]["localKeywords"]=["x","x"]
        with self.assertRaises(ValueError): summarize_routing(f)

    def test_invalid_variantmap_record_rejected(self):
        f=fixture();f["variants"][0]["kernels"][0]["variantMap"]=[(1,{}),(2,{})]
        with self.assertRaises(ValueError): summarize_routing(f)

    def test_ambiguous_workgroup_rejected(self):
        f=fixture();f["variants"][0]["kernels"][0]["variantMap"][0][1]["other"]=(64,1,1)
        with self.assertRaises(ValueError): summarize_routing(f)

    def test_private_program_identifiers_not_returned(self):
        r=str(summarize_routing(fixture("pair")))
        for word in ("synthetic-shared","group-1","DXBC"):
            self.assertNotIn(word,r)

    def test_forged_twenty_named_runtime_kernels_rejected(self):
        f=fixture();f["variants"][0]["kernels"][3]["name"]="other-name"
        with self.assertRaises(ValueError): summarize_routing(f)

    def test_opaque_structured_header_preserves_collision_classes(self):
        f=fixture()
        for row in f["variants"][0]["kernels"]:
            row["variantMap"][0]=(("<opaque>", [1,2], {"v":3}), row["variantMap"][0][1])
        result=summarize_routing(f)
        self.assertEqual(result["original_variant_map_header_unique_values"],1)
        self.assertFalse(result["opaque_map_header_meaning_inferred"])

    def test_custom_unstable_header_is_rejected(self):
        f=fixture()
        f["variants"][0]["kernels"][0]["variantMap"][0]=(object(),f["variants"][0]["kernels"][0]["variantMap"][0][1])
        with self.assertRaises(ValueError): summarize_routing(f)

    def test_invalid_binary_payload_rejected(self):
        f=fixture();f["variants"][0]["kernels"][2]["variantMap"][0][1]["bin"]=list(b"FAKE"+bytes([2])*60)
        with self.assertRaises(ValueError): summarize_routing(f)

    def test_unsafe_keyword_structure_rejected(self):
        f=fixture();f["variants"][0]["kernels"][1]["globalKeywords"]=[{"untrusted":True}]
        with self.assertRaises(ValueError): summarize_routing(f)

if __name__=="__main__": unittest.main()
