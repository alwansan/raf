"""GFX103 syntax-only fail-closed regression without proprietary DXBC source."""
import struct
import unittest
from gfxlab.tools.gfx103_source_interpolation_gate import (
    dxbc_fragment_input_classes,enforce_native_gles_qualifier,source_pair_gate,NV)

def shdr(*declarations):
    # Minimal synthetic D3D10-style token stream: opcode + mode + 2 dwords.
    words=[0x50,2+2*len(declarations)]
    for op,mode in declarations:
        words.extend([op|(mode<<11)|(2<<24),0])
    return struct.pack("<%dI"%len(words),*words)

VERT="#version 310 es\nlayout(location=0) noperspective out vec3 c;\nvoid main(){}\n"
FRAG="#version 310 es\nlayout(location=0) noperspective in vec3 c;\nvoid main(){}\n"

class GFX103SourceInterpolationGate(unittest.TestCase):
    def test_dxbc_interpolation_classes_separate_ordinary_and_siv(self):
        d=dxbc_fragment_input_classes(shdr((98,2),(98,4),(100,4),(100,1),(99,0)))
        self.assertEqual(d["ordinary_modes"],{"linear":1,"linear_noperspective":1})
        self.assertEqual(d["system_interpreted_modes"],
                         {"linear_noperspective":1,"constant":1})
        self.assertEqual(d["system_generated_count"],1)
        self.assertEqual(d["ordinary_noperspective_declarations"],1)
        self.assertEqual(d["system_interpreted_noperspective_declarations"],1)
    def test_inject_required_vendor_extension_once(self):
        frag,proof=enforce_native_gles_qualifier(FRAG,"fragment",
            {"ordinary_noperspective_declarations":1,
             "system_interpreted_noperspective_declarations":0})
        self.assertIn("#extension "+NV+" : require\n",frag)
        self.assertEqual(frag.count("#extension "+NV),1)
        self.assertTrue(proof["nv_extension_required"])
        self.assertFalse(proof["original_shader_restored"])
    def test_es300_native_rejected_from_owner_gpu_evidence(self):
        with self.assertRaisesRegex(ValueError,"GFX103_NATIVE_ES300"):
            enforce_native_gles_qualifier(FRAG.replace("310","300"),"fragment",
              {"ordinary_noperspective_declarations":1,
               "system_interpreted_noperspective_declarations":0})
    def test_native_attribute_lost_rejected(self):
        with self.assertRaisesRegex(ValueError,"GFX103_NATIVE_ORDINARY_INTERPOLATION_LOST"):
            enforce_native_gles_qualifier("#version 310 es\nin vec3 c;\n",
              "fragment",{"ordinary_noperspective_declarations":1,
                          "system_interpreted_noperspective_declarations":0})
    def test_system_interpreted_is_distinct_and_not_conflated(self):
        frag,proof=enforce_native_gles_qualifier("#version 310 es\nin vec3 c;\n",
              "fragment",{"ordinary_noperspective_declarations":0,
                          "system_interpreted_noperspective_declarations":1})
        self.assertNotIn(NV,frag)
        self.assertEqual(proof["siv_noperspective_count"],1)
        self.assertFalse(proof["siv_builtin_mapping_verified"])
    def test_full_pair_noperspective_preserved(self):
        (v,f),meta=source_pair_gate(shdr((98,4)),VERT,FRAG)
        self.assertIn("#extension "+NV+" : require",v)
        self.assertIn("#extension "+NV+" : require",f)
        self.assertFalse(meta["stage_linked_on_device"])
        self.assertFalse(meta["phase_closed"])
    def test_vertex_side_missing_rejected(self):
        with self.assertRaisesRegex(ValueError,"GFX103_VERTEX_NATIVE_VARYING_MISSING"):
            source_pair_gate(shdr((98,4)),"#version 310 es\nout vec3 c;\n",FRAG)
    def test_weak_or_duplicate_extension_rejected(self):
        for directive in ("enable","disable","warn"):
            with self.assertRaisesRegex(ValueError,"GFX103_EXTENSION_NOT_REQUIRED"):
                enforce_native_gles_qualifier(
                    "#version 310 es\n#extension "+NV+" : "+directive+"\n"+VERT.split("\n",1)[1],
                    "vertex")
        with self.assertRaisesRegex(ValueError,"GFX103_DUPLICATE_EXTENSION"):
            enforce_native_gles_qualifier(
                "#version 310 es\n"+("#extension "+NV+" : require\n")*2+VERT.split("\n",1)[1],
                "vertex")
    def test_truncated_shdr_fails(self):
        with self.assertRaisesRegex(ValueError,"GFX103_"):
            dxbc_fragment_input_classes(shdr((98,4))[:-4])
    def test_no_original_material_or_pixel_false_proofs(self):
        _,proof=enforce_native_gles_qualifier(VERT,"vertex")
        for flag in ("material_cb_binding_verified","original_pixel_parity_verified",
                     "original_shader_restored","phase_closed"):
            self.assertIs(proof[flag],False)
    def test_version320_native_allowed(self):
        text,meta=enforce_native_gles_qualifier(VERT.replace("310","320"),"vertex")
        self.assertIn("#version 320 es",text)
        self.assertEqual(meta["glsl_es_version"],320)

if __name__=="__main__":unittest.main()
