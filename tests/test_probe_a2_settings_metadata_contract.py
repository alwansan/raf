"""Synthetic-only exact managed token and source field comparisons."""
import unittest
from scripts.probe_a2_settings_metadata_contract import candidate_source_names,verify_fielddefs

def row(name,n,kind="unity_engine_type_unverified_base",**kw):
    return dict(name=name,token=0x04000000+n,kind=kind,
      element_kind=kw.get("element_kind"),is_public=kw.get("is_public",True),
      is_static=kw.get("is_static",False),is_const=kw.get("is_const",False),
      is_readonly=kw.get("is_readonly",False),is_not_serialized=kw.get("is_not_serialized",False),
      has_nonserialized_attribute=kw.get("has_nonserialized_attribute",False),
      has_serialize_field=kw.get("has_serialize_field",False),
      has_serialize_reference=kw.get("has_serialize_reference",False))

def sample(fields,ns="Game"):
    return dict(format_version=1,assembly_name="Assembly-CSharp",
      candidate_types=[dict(name="Settings",namespace_name=ns,token=0x02000011,
                             fields=fields)])

class OriginalMetadataTests(unittest.TestCase):
    def test_valid_typed_field_metadata_agrees_with_original_source(self):
        metadata=sample([row("flag",1,"primitive_4byte_or_smaller"),
          row("owner",2,"same_assembly_class",is_public=False,has_serialize_field=True),
          row("panels",3,"array",element_kind="unity_engine_type_unverified_base"),
          row("ignored",4,"string",is_not_serialized=True)])
        x=verify_fielddefs(metadata,"Assembly-CSharp","Game",["flag","owner","panels"])
        self.assertEqual(x["original_candidate_eligible_fielddefs"],3)
        self.assertEqual(x["collection_element_families"]["unity_engine_type_unverified_base"],1)
        self.assertTrue(x["source_declaration_order_equals_metadata_order"])
        self.assertFalse(x["original_unity_serialized_field_offsets_proven"])
        self.assertNotIn("owner",str(x))

    def test_wrong_order_distinguished_from_missing_fields(self):
        metadata=sample([row("alpha",1),row("beta",2)])
        x=verify_fielddefs(metadata,"Assembly-CSharp","Game",["beta","alpha"])
        self.assertTrue(x["source_field_name_set_equals_metadata"])
        self.assertFalse(x["source_declaration_order_equals_metadata_order"])

    def test_private_static_readonly_excluded(self):
        metadata=sample([row("only",1),row("hidden",2,is_public=False),
                         row("static",3,is_static=True),row("readonly",4,is_readonly=True)])
        x=verify_fielddefs(metadata,"Assembly-CSharp","Game",["only"])
        self.assertEqual(x["original_candidate_eligible_fielddefs"],1)

    def test_wrong_type_identity_or_duplicate_is_rejected(self):
        m=sample([row("ok",1)])
        with self.assertRaisesRegex(ValueError,"assembly identity"):
            verify_fielddefs(m,"NotOriginal","Game",["ok"])
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            verify_fielddefs(m,"Assembly-CSharp","WrongNamespace",["ok"])
        m["candidate_types"].append(m["candidate_types"][0])
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            verify_fielddefs(m,"Assembly-CSharp","Game",["ok"])

    def test_field_token_drift_fails_closed(self):
        for fields in ([row("x",3),row("y",2)],
                       [row("x",1),row("y",1)],
                       [row("x",1),row("y",0x02000001)]):
            with self.assertRaisesRegex(ValueError,"tokens not ordered"):
                verify_fielddefs(sample(fields),"Assembly-CSharp","Game",["x","y"])

    def test_duplicate_names_and_excess_field_rejected(self):
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            verify_fielddefs(sample([row("same",1),row("same",2)]),
                             "Assembly-CSharp","Game",["same"])
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            verify_fielddefs(sample([row("x",1)]),"Assembly-CSharp","Game",["x","x"])

    def test_source_member_negative_controls(self):
        source='''class Settings {
            public int Count;
            [SerializeField] private UnityEngine.GameObject panel;
            private UnityEngine.GameObject hidden;
            public static int Cache;
            [NonSerialized] public bool skip;
            public void Open() { int fake=42; }
            public bool Property { get; set; }
        }'''
        self.assertEqual(candidate_source_names(source),["Count","panel"])
        with self.assertRaisesRegex(ValueError,"missing or ambiguous"):
            candidate_source_names("class Other { public int Count; }")

if __name__=="__main__":
    unittest.main()
