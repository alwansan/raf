"""T3 original-vs-same-export color trace selection and privacy controls."""
import unittest
from scripts import t3_same_export_material_colors as m

class SelectedColorTrace(unittest.TestCase):
    def traces(self):
        return (
            dict(schema_version=1,export_instance='a'*32,objects=[
                dict(class_id=21,source=dict(owner='sharedassets6.assets',path_id=i+1),
                     export=dict(file_id=i+2100000,guid='b'*32,type=2),exportable=True)
                for i in range(41)
            ]+[
                dict(class_id=21,source=dict(owner='globalgamemanagers.assets',path_id=7),
                     export=dict(file_id=212222,guid='e'*32,type=2),exportable=True)
            ]),
            dict(schema_version=1,export_instance='a'*32,objects=[
                dict(class_id=28,source=dict(owner='sharedassets6.assets',path_id=45),
                     export=dict(file_id=2800000,guid='c'*32,type=2))]))
    def report(self):
        result={name:0 for name in m.SAFE_COUNTS}
        result.update(source_materials_verified=41,yaml_materials_compared=41,
                      color_slots_compared=90,mismatched_materials=0)
        result.update(original_material_color_values_preserved=True,
                      shader_program_or_device_fidelity_verified=False)
        return result
    def test_scope_materials_and_outside_owner_not_mixed(self):
        w1,b02=self.traces()
        r=m.select_same_export_materials(w1,b02)
        self.assertEqual(len(r['objects']),41)
        self.assertEqual(r['export_instance'],'a'*32)
    def test_cross_export_instance_refused(self):
        w1,b02=self.traces()
        b02['export_instance']='d'*32
        with self.assertRaises(ValueError):
            m.select_same_export_materials(w1,b02)
    def test_missing_selected_material_refused(self):
        w1,b02=self.traces()
        w1['objects'].pop(0)
        with self.assertRaises(ValueError):
            m.select_same_export_materials(w1,b02)
    def test_original_colors_match_stays_scoped(self):
        r=m.aggregate(self.report())
        self.assertEqual(r['status'],'SCOPED_COLOR_RGBA_MATCH')
        self.assertFalse(r['device_color_pixels_proven'])
        self.assertFalse(r['shader_variants_or_lighting_proven'])
        self.assertFalse(r['external_texture_targets_proven'])
    def test_color_drift_not_claimed_success(self):
        r=self.report()
        r['changed_color_values']=1
        r['mismatched_materials']=1
        r['original_material_color_values_preserved']=False
        self.assertEqual(m.aggregate(r)['status'],'SCOPED_COLOR_RGBA_MISMATCH')
    def test_full_material_set_is_mandatory(self):
        r=self.report()
        r['source_materials_verified']=40
        with self.assertRaises(ValueError):
            m.aggregate(r)
    def test_future_private_property_never_serialized(self):
        r=self.report()
        r['private_names']=['NEVER_PUBLISH']
        self.assertNotIn('private_names',m.aggregate(r))
if __name__=="__main__":
    unittest.main()
