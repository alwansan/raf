"""Synthetic original Settings field classifier tests, no game code."""
import unittest
from scripts.probe_a2_settings_typed_fields import field_signature,class_scope,ZIP2_PIN,DLL_BLOB

class A2FieldMetadata(unittest.TestCase):
    def test_known_fields_and_arrays_without_properties(self):
        sample="""public class Settings : MonoBehaviour {
            public GameObject menu;
            [SerializeField] private Button action;
            private GameObject ignored;
            public static Canvas Instance;
            [NonSerialized] public Slider cache;
            public float scale;
            [SerializeField] private GameObject[] tabs;
            public void Show() { var local = new GameObject(); }
            public bool Open { get; set; }
        }"""
        x=field_signature(sample)
        self.assertEqual(x["candidate_serializable_field_count"],4)
        self.assertEqual(x["candidate_type_categories"]["known_unity_native_object_reference"],2)
        self.assertEqual(x["candidate_type_categories"]["builtin_value_or_struct"],1)
        self.assertEqual(x["candidate_type_categories"]["array_or_collection_unknown_element"],1)
        self.assertFalse(x["typed_original_pointer_offsets_recovered"])
        self.assertNotIn("tabs",str(x))

    def test_comments_and_strings_cannot_create_fields(self):
        src="""class Settings {
            // public GameObject fake;
            public RectTransform root;
            private string text = "public Canvas spoof;";
            public void Show() { string x = "public Canvas wrong"; }
        }"""
        self.assertEqual(field_signature(src)["candidate_serializable_field_count"],1)

    def test_nested_methods_properties_not_source_fields(self):
        src="""class Settings {
          public GameObject[] panels;
          class Nested { public Button hidden; }
          public GameObject Property { get; set; }
          void X() { bool b = false; }
        }"""
        x=field_signature(src)
        self.assertEqual(x["candidate_serializable_field_count"],1)
        self.assertEqual(x["candidate_type_categories"]["array_or_collection_unknown_element"],1)

    def test_readonly_static_and_private_do_not_count(self):
        src="""class Settings {
           public static Button current;
           public readonly Slider permanent;
           private GameObject hidden;
           public Transform owner;
        }"""
        x=field_signature(src)
        self.assertEqual(x["candidate_serializable_field_count"],1)
        self.assertTrue(x["excluded_and_unparsed_counts"]["static_const_readonly"]>=2)

    def test_wrong_class_and_braces_rejected(self):
        with self.assertRaisesRegex(ValueError,"missing or ambiguous"):
            class_scope("class Other { public Button a; }")
        with self.assertRaisesRegex(ValueError,"brace mismatch"):
            class_scope("class Settings { public Button a;")
        with self.assertRaisesRegex(ValueError,"No Settings"):
            field_signature("class Settings { public void X() {} }")

    def test_pinned_source_and_bounds(self):
        self.assertEqual(len(ZIP2_PIN),40)
        self.assertEqual(len(DLL_BLOB),40)
        with self.assertRaisesRegex(ValueError,"oversized"):
            class_scope("class Settings {"+"x"*300001+"}")
if __name__=="__main__":
    unittest.main()
