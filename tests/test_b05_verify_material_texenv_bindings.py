"""B05 synthetic negative controls; success does not prove on-device colors."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.b05_verify_material_texenv_bindings import compare, normalize_texenvs, exported_texenvs

SRC=('sharedassets0.assets',100)
MAT=(2100000,'a'*32)
TEX=(2800000,'b'*32,3)

def fixture():
    trace={'schema_version':1,'export_instance':'f'*32,'objects':[
        {'class_id':21,'source':{'owner':SRC[0],'path_id':SRC[1]},
         'export':{'file_id':MAT[0],'guid':MAT[1],'type':2},'exportable':True},
        {'class_id':28,'source':{'owner':SRC[0],'path_id':101},
         'export':{'file_id':TEX[0],'guid':TEX[1],'type':TEX[2]},'exportable':True},
    ]}
    original={SRC:{'_MainTex':(0,101),'_Normal':(0,0),'_External':(1,209)}}
    exported={MAT:{'_MainTex':TEX,'_Normal':(0,'0'*32,0),'_External':(2800000,'e'*32,3)}}
    return trace,original,exported

class B05TexEnvTests(unittest.TestCase):
    def test_original_internal_exact_and_external_unproved(self):
        t,s,a=fixture()
        r=compare(t,s,a)
        self.assertEqual((r['exact_internal_targets_compared'],r['external_targets_not_proven']),(1,1))
        self.assertTrue(r['source_slots_faithful_with_resolved_scope'])
        self.assertFalse(r['all_texture_targets_proven'])
        self.assertFalse(r['unity_shader_or_android_pixels_proven'])
        self.assertNotIn('_MainTex',json.dumps(r))
        self.assertNotIn('sharedassets0',json.dumps(r))

    def test_bound_to_null_rejected(self):
        t,s,a=fixture();a[MAT]['_MainTex']=(0,'0'*32,0)
        r=compare(t,s,a)
        self.assertEqual(r['bound_to_null'],1)
        self.assertFalse(r['source_slots_faithful_with_resolved_scope'])

    def test_wrong_internal_target_detected(self):
        t,s,a=fixture();a[MAT]['_MainTex']=(2800000,'c'*32,3)
        self.assertEqual(compare(t,s,a)['wrong_internal_targets'],1)

    def test_missing_or_extra_slots_detected(self):
        t,s,a=fixture();del a[MAT]['_MainTex']
        self.assertEqual(compare(t,s,a)['missing_slots'],1)
        a[MAT]['_Extra']=(0,'0'*32,0)
        self.assertEqual(compare(t,s,a)['extra_slots'],1)

    def test_null_to_bound_detected(self):
        t,s,a=fixture();a[MAT]['_Normal']=TEX
        self.assertEqual(compare(t,s,a)['null_to_bound'],1)

    def test_missing_internal_trace_never_guessed(self):
        t,s,a=fixture();t['objects'].pop()
        r=compare(t,s,a)
        self.assertEqual(r['unresolved_internal_targets'],1)
        self.assertFalse(r['source_slots_faithful_with_resolved_scope'])

    def test_duplicate_trace_source_rejected(self):
        t,s,a=fixture();t['objects'].append(copy.deepcopy(t['objects'][1]))
        with self.assertRaisesRegex(ValueError,'Duplicated original'):
            compare(t,s,a)

    def test_same_instance_material_identity_required(self):
        t,s,a=fixture();t['export_instance']='bad'
        with self.assertRaisesRegex(ValueError,'same-instance'):
            compare(t,s,a)
        t,s,a=fixture();a[MAT[0],'d'*32]=a.pop(MAT)
        with self.assertRaisesRegex(ValueError,'identities'):
            compare(t,s,a)

    def test_original_shapes_null_and_duplicate(self):
        self.assertEqual(normalize_texenvs([('_MainTex',{'m_Texture':{'m_FileID':0,'m_PathID':101}})]),{'_MainTex':((0,101),None)})
        with self.assertRaisesRegex(ValueError,'duplicate'):
            normalize_texenvs([('_MainTex',{'m_Texture':{'m_FileID':0,'m_PathID':1}})]*2)
        with self.assertRaisesRegex(ValueError,'no target'):
            normalize_texenvs([('_External',{'m_Texture':{'m_FileID':2,'m_PathID':0}})])
        with self.assertRaisesRegex(ValueError,'Invalid original PPtr'):
            normalize_texenvs([('_MainTex',{'m_Texture':{'m_FileID':False,'m_PathID':1}})])

    def test_exported_yaml_embedded_material(self):
        with tempfile.TemporaryDirectory() as td:
            assets=Path(td)/'Assets';assets.mkdir()
            asset=assets/'embedded.asset'
            asset.write_text('%YAML 1.1\n--- !u!128 &12800000\nFont: {m_Name: dummy}\n--- !u!21 &2100000\nMaterial:\n  m_SavedProperties:\n    m_TexEnvs:\n    - _MainTex:\n        m_Texture: {fileID: 2800000, guid: '+ 'b'*32 +', type: 3}\n')
            (assets/'embedded.asset.meta').write_text('fileFormatVersion: 2\nguid: '+'a'*32+'\n')
            self.assertEqual(exported_texenvs(Path(td)),{MAT:{'_MainTex':(TEX,None)}})


    def test_actual_exported_texenv_mapping_shape_and_strict_original(self):
        # Authentic same-instance T3 run 41939065539 failed with
        # texenv_wrong_container. Export YAML can use a dictionary; the source
        # Unity typetree is still required to use an explicit list.
        value={'m_Texture':{'fileID':TEX[0],'guid':TEX[1],'type':TEX[2]},
               'm_Scale':{'x':1,'y':1},'m_Offset':{'x':0,'y':0}}
        self.assertEqual(normalize_texenvs({'_MainTex':value},exported=True),
                         {'_MainTex':(TEX,(1.,1.,0.,0.))})
        self.assertEqual(normalize_texenvs({},exported=True),{})
        with self.assertRaisesRegex(ValueError,'array'):
            normalize_texenvs({'_MainTex':value})
        with self.assertRaisesRegex(ValueError,'Malformed or duplicate'):
            normalize_texenvs({12:value},exported=True)
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            normalize_texenvs({'_MainTex':{'m_Texture':value['m_Texture'],
                           'm_Scale':{'x':1,'y':1}}},exported=True)

    def test_actual_exported_material_mapping_yaml(self):
        with tempfile.TemporaryDirectory() as td:
            assets=Path(td)/'Assets';assets.mkdir()
            mat=assets/'scope.mat'
            mat.write_text('%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n'
                           '  m_SavedProperties:\n'
                           '    m_TexEnvs:\n'
                           '      _MainTex:\n'
                           '        m_Texture: {fileID: 2800000, guid: '+ 'b'*32 +', type: 3}\n'
                           '        m_Scale: {x: 1, y: 1}\n'
                           '        m_Offset: {x: 0, y: 0}\n')
            (assets/'scope.mat.meta').write_text('fileFormatVersion: 2\nguid: '+'a'*32+'\n')
            self.assertEqual(exported_texenvs(Path(td)),
                             {MAT:{'_MainTex':(TEX,(1.,1.,0.,0.))}})

    def test_uv_transforms_same_and_modified(self):
        t,s,a=fixture()
        s[SRC]['_MainTex']=((0,101),(2.,1.,.5,0.))
        a[MAT]['_MainTex']=(TEX,(2.,1.,.5,0.))
        first=compare(t,s,a)
        self.assertEqual(first['uv_transform_slots_compared'],1)
        self.assertEqual(first['uv_transform_value_mismatches'],0)
        a[MAT]['_MainTex']=(TEX,(2.,1.,.65,0.))
        result=compare(t,s,a)
        self.assertEqual(result['uv_transform_value_mismatches'],1)
        self.assertFalse(result['source_slots_faithful_with_resolved_scope'])

    def test_uv_unknown_not_silently_verified(self):
        t,s,a=fixture()
        r=compare(t,s,a)
        self.assertEqual(r['uv_transform_missing_or_unproven'],3)
        self.assertFalse(r['all_uv_transforms_verified'])
        s[SRC]['_MainTex']=((0,101),(1.,1.,0.,0.))
        self.assertEqual(compare(t,s,a)['uv_transform_missing_or_unproven'],3)

    def test_uv_normalizer_rejects_partial_or_nonfinite(self):
        pointer={'m_FileID':0,'m_PathID':101}
        slot={'m_Texture':pointer,'m_Scale':{'x':2,'y':1},'m_Offset':{'x':0.25,'y':0}}
        actual=normalize_texenvs([('_MainTex',slot)])
        self.assertEqual(actual,{'_MainTex':((0,101),(2.,1.,.25,0.))})
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            normalize_texenvs([('_MainTex',{'m_Texture':pointer,'m_Scale':{'x':1,'y':1}})])
        invalid=dict(slot)
        invalid['m_Offset']={'x':float('nan'),'y':0}
        with self.assertRaisesRegex(ValueError,'Nonfinite'):
            normalize_texenvs([('_MainTex',invalid)])


    def test_scoped_owner_full_export_superset_never_claims_global_proof(self):
        t, s, a = fixture()
        other_mat = (2100111, 'c'*32)
        t['objects'].append(dict(class_id=21,
            source=dict(owner='sharedassets36.assets', path_id=721),
            export=dict(file_id=other_mat[0], guid=other_mat[1], type=2),
            exportable=True))
        a[other_mat] = {'_Other': (0, '0'*32, 0)}
        scoped = compare(t, s, a, selected_owners={SRC[0]})
        self.assertEqual((scoped['materials_compared'], scoped['outside_scope_export_materials'],
                          scoped['outside_scope_trace_materials']), (1, 1, 1))
        self.assertEqual(scoped['source_scope'], 'selected-owner')
        self.assertTrue(scoped['source_slots_faithful_with_resolved_scope'])
        self.assertFalse(scoped['all_texture_targets_proven'])
        self.assertFalse(scoped['full_game_source_coverage_verified'])
        with self.assertRaisesRegex(ValueError, 'Unverified traced original'):
            compare(t, s, a)

    def test_scoped_owner_missing_and_extra_selected_material_rejected(self):
        t, s, a = fixture()
        t['objects'] = [row for row in t['objects'] if row['class_id'] != 21]
        with self.assertRaisesRegex(ValueError, 'identities'):
            compare(t, s, a, selected_owners={SRC[0]})
        t, s, a = fixture()
        t['objects'].append(dict(class_id=21,
            source=dict(owner=SRC[0], path_id=999),
            export=dict(file_id=2100111, guid='c'*32, type=2),
            exportable=True))
        with self.assertRaisesRegex(ValueError, 'Unverified traced original'):
            compare(t, s, a, selected_owners={SRC[0]})

    def test_scoped_owner_collision_with_unchecked_source_rejected(self):
        t, s, a = fixture()
        t['objects'].append(dict(class_id=21,
            source=dict(owner='sharedassets36.assets', path_id=999),
            export=dict(file_id=MAT[0], guid=MAT[1], type=2),
            exportable=True))
        with self.assertRaisesRegex(ValueError, 'collides'):
            compare(t, s, a, selected_owners={SRC[0]})

    def test_scoped_owner_filter_and_pin_allowlist_rejected(self):
        t, s, a = fixture()
        with self.assertRaisesRegex(ValueError, 'Invalid selected-original'):
            compare(t, s, a, selected_owners={'untrusted.assets'})
        with self.assertRaisesRegex(ValueError, 'Invalid selected-original'):
            compare(t, s, a, selected_owners=set())
        from scripts.b05_verify_material_texenv_bindings import original_texenvs
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'Unpinned'):
                original_texenvs(Path(tmp), owner_names={'../outside'})

    def test_symlink_export_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            assets=Path(td)/'Assets';assets.mkdir()
            (assets/'link').symlink_to(Path(td),target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'Linked'):
                exported_texenvs(Path(td))


class DocumentScopedLocalTextureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name)
        self.assets=self.project/'Assets'
        self.assets.mkdir()
        self.t,self.s,self.a=fixture()
        self.s[SRC]={'_MainTex':((0,101),(1.,1.,0.,0.))}
        self.t['objects'][1]['export']={'file_id':2800000,'guid':MAT[1],'type':2}
        self.t['objects'][1]['exportable']=True

    def document(self,name='embedded.asset',guid=MAT[1],anchor=2100000,texture_class=28,
                 texture_root='Texture2D',stripped=False,texture=True):
        p=self.assets/name
        body=f'%YAML 1.1\n--- !u!21 &{anchor}\nMaterial:\n  m_SavedProperties:\n    m_TexEnvs:\n    - _MainTex:\n        m_Texture: {{fileID: 2800000}}\n        m_Scale: {{x: 1, y: 1}}\n        m_Offset: {{x: 0, y: 0}}\n'
        if texture:
            body+=f'--- !u!{texture_class} &2800000'+(' stripped' if stripped else '')+f'\n{texture_root}:\n  m_Width: 2\n  m_Height: 2\n'
        p.write_text(body)
        Path(str(p)+'.meta').write_text(f'guid: {guid}\n')
        return p

    def audit(self):
        docs={}
        actual=exported_texenvs(self.project,private_texture_documents=docs)
        r=compare(self.t,self.s,actual,private_texture_documents=docs)
        self.assertNotIn(MAT[1],json.dumps(r))
        self.assertNotIn('_MainTex',json.dumps(r))
        return r

    def test_real_yaml_document_scoped_local_texture(self):
        self.document()
        result=self.audit()
        self.assertEqual(result['document_scoped_local_texture_targets_proven'],1)
        self.assertEqual(result['exact_internal_targets_compared'],1)
        self.assertTrue(result['all_texture_targets_proven'])
        self.assertTrue(result['all_uv_transforms_verified'])

    def test_equal_anchor_in_different_document_is_wrong_target(self):
        self.document()
        self.t['objects'][1]['export']['guid']='b'*32
        result=self.audit()
        self.assertEqual(result['local_texture_document_identity_mismatch'],1)
        self.assertFalse(result['selected_texture_targets_proven'])

    def test_same_triple_type0_is_not_identity(self):
        self.document()
        self.t['objects'][1]['export']={'file_id':2800000,'guid':'0'*32,'type':0}
        result=self.audit()
        self.assertEqual(result['equal_unscoped_type0_triples'],1)
        self.assertEqual(result['exact_internal_targets_compared'],0)
        self.assertEqual(result['unresolved_internal_targets'],1)
        self.assertFalse(result['source_slots_faithful_with_resolved_scope'])

    def test_missing_texture_document(self):
        self.document(texture=False)
        r=self.audit()
        self.assertEqual(r['local_texture_document_unavailable'],1)
        self.assertFalse(r['selected_texture_targets_proven'])

    def test_stripped_reference_not_texture_document(self):
        self.document(stripped=True)
        self.assertEqual(self.audit()['local_texture_document_unavailable'],1)

    def test_wrong_texture_class_even_same_anchor_and_guid(self):
        self.document(texture_class=117,texture_root='Texture3D')
        result=self.audit()
        self.assertEqual(result['local_texture_document_class_mismatch'],1)
        self.assertFalse(result['selected_texture_targets_proven'])

    def test_wrong_root_not_texture_document(self):
        self.document(texture_root='Material')
        self.assertEqual(self.audit()['local_texture_document_unavailable'],1)

    def test_exportability_must_be_proven(self):
        self.document()
        del self.t['objects'][1]['exportable']
        self.assertEqual(self.audit()['local_texture_document_unavailable'],1)

    def test_duplicate_guid_across_documents_rejected(self):
        self.document()
        self.document(name='alias.asset',anchor=2100001)
        with self.assertRaisesRegex(ValueError,'Duplicate GUID across'):
            self.audit()

    def test_duplicate_anchor_rejected_even_nonmaterial(self):
        p=self.document()
        p.write_text(p.read_text()+'--- !u!28 &2800000\nTexture2D: {}\n')
        with self.assertRaisesRegex(ValueError,'Duplicate anchor'):
            self.audit()

    def test_local_cannot_pass_without_actual_document_inventory(self):
        self.document()
        actual=exported_texenvs(self.project)
        r=compare(self.t,self.s,actual)
        self.assertEqual(r['local_texture_document_unavailable'],1)
        self.assertFalse(r['selected_texture_targets_proven'])


if __name__=='__main__':
    unittest.main()
