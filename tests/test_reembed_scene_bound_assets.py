from pathlib import Path
import tempfile
import unittest
from scripts.reembed_scene_bound_assets import plan, apply, documents

S = '1' * 32
A = '2' * 32
B = '3' * 32
T = '4' * 32


class SceneBoundAssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        self.assets = self.root / 'Assets'
        self.assets.mkdir(parents=True)

    def asset(self, name, guid, kind, local, body):
        p = self.assets / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!' + str(kind) + ' &' + str(local) + '\n' + body + '\n')
        Path(str(p) + '.meta').write_text('fileFormatVersion: 2\nguid: ' + guid + '\noriginalMeta: preserved\n')
        return p

    def basic(self):
        scene = self.asset('Scenes/a.unity', S, 1, 10,
            'GameObject:\n  data: {fileID: 11400000, guid: ' + A + ', type: 2}')
        source = self.asset('MonoBehaviour/item.asset', A, 114, 11400000,
            'MonoBehaviour:\n  m_GameObject: {fileID: 0}\n  target: {fileID: 10, guid: ' + S + ', type: 2}\n  customField: 1234')
        return scene, source

    def test_reembedding_preserves_every_field_object_and_meta(self):
        scene, source = self.basic()
        original, meta = source.read_bytes(), Path(str(source) + '.meta').read_bytes()
        scene_meta = Path(str(scene) + '.meta').read_bytes()
        result = plan(self.root)
        self.assertEqual(result['report']['scene_bound_assets'], 1)
        self.assertEqual(result['report']['serialized_objects_before'], 2)
        backup = Path(self.tmp.name) / 'backup'
        apply(result, backup)
        self.assertEqual(len(documents(scene.read_text())), 2)
        self.assertIn('customField: 1234', scene.read_text())
        self.assertIn('target: {fileID: 10}', scene.read_text())
        self.assertFalse(source.exists())
        self.assertEqual((backup / 'Assets/MonoBehaviour/item.asset').read_bytes(), original)
        self.assertEqual((backup / 'Assets/MonoBehaviour/item.asset.meta').read_bytes(), meta)
        self.assertEqual(Path(str(scene) + '.meta').read_bytes(), scene_meta)

    def test_indirect_owners_are_relocated_with_reference_closure(self):
        self.basic()
        self.asset('Data/wrapper.asset', B, 114, 11400000,
            'MonoBehaviour:\n  inner: {fileID: 11400000, guid: ' + A + ', type: 2}')
        result = plan(self.root)
        self.assertEqual(result['report']['scene_bound_assets'], 2)
        self.assertEqual(result['report']['serialized_objects_after'], 3)
        apply(result, Path(self.tmp.name) / 'backup')

    def test_resource_lookup_risk_rejected_without_any_writes(self):
        scene, _ = self.basic()
        self.asset('Resources/wrapper.asset', B, 114, 11400000,
            'MonoBehaviour:\n  inner: {fileID: 11400000, guid: ' + A + ', type: 2}')
        before = scene.read_bytes()
        with self.assertRaisesRegex(ValueError, 'resource/editor'):
            plan(self.root)
        self.assertEqual(scene.read_bytes(), before)

    def test_cross_scene_ownership_rejected(self):
        self.basic()
        self.asset('Scenes/b.unity', T, 1, 20,
            'GameObject:\n  shared: {fileID: 11400000, guid: ' + A + ', type: 2}')
        with self.assertRaisesRegex(ValueError, 'Another scene'):
            plan(self.root)

    def test_prefab_consumer_not_silently_removed(self):
        self.basic()
        self.asset('Prefabs/item.prefab', B, 1, 4,
            'GameObject:\n  shared: {fileID: 11400000, guid: ' + A + ', type: 2}')
        with self.assertRaisesRegex(ValueError, 'single ScriptableObject'):
            plan(self.root)

    def test_scene_local_id_collision_uses_alias_for_same_object(self):
        scene, _ = self.basic()
        scene.write_text(scene.read_text() + '--- !u!114 &11400000\nMonoBehaviour:\n  untouched: 9\n')
        result = plan(self.root)
        self.assertEqual(result['report']['serialized_objects_before'], 3)
        apply(result, Path(self.tmp.name) / 'backup')
        self.assertEqual(len(documents(scene.read_text())), 3)
        self.assertIn('untouched: 9', scene.read_text())

    def test_invalid_reference_object_id_rejected(self):
        scene, _ = self.basic()
        scene.write_text(scene.read_text().replace('fileID: 11400000', 'fileID: 999'))
        with self.assertRaisesRegex(ValueError, 'absent object'):
            plan(self.root)

    def test_binary_consumer_refused(self):
        self.basic()
        (self.assets / 'binary.bin').write_bytes(b'binary\x00' + A.encode())
        with self.assertRaisesRegex(ValueError, 'Non-YAML'):
            plan(self.root)

    def test_no_scene_objects_is_a_nonmutating_noop(self):
        p = self.asset('Data/item.asset', A, 114, 11400000, 'MonoBehaviour:\n  noScene: {fileID: 0}')
        before = p.read_bytes()
        self.assertEqual(plan(self.root)['report']['scene_bound_assets'], 0)
        self.assertEqual(p.read_bytes(), before)

    def test_backup_inside_project_rejected(self):
        scene, _ = self.basic()
        before = scene.read_bytes()
        with self.assertRaisesRegex(ValueError, 'outside'):
            apply(plan(self.root), self.root / 'backup')
        self.assertEqual(scene.read_bytes(), before)

    def test_scene_asset_pointer_is_not_a_scene_object(self):
        self.asset('Scenes/a.unity', S, 1, 10, 'GameObject:\n  name: retained')
        self.asset('Data/ref.asset', A, 114, 11400000,
            'MonoBehaviour:\n  sceneAsset: {fileID: 102900000, guid: ' + S + ', type: 3}')
        self.assertEqual(plan(self.root)['report']['scene_bound_assets'], 0)

    def test_local_self_reference_survives_identity_collision(self):
        scene, source = self.basic()
        scene.write_text(scene.read_text() + '--- !u!114 &11400000\nMonoBehaviour:\n  retained: 7\n')
        source.write_text(source.read_text() + '  self: {fileID: 11400000}\n')
        result = plan(self.root)
        apply(result, Path(self.tmp.name) / 'backup')
        self.assertEqual(result['report']['serialized_objects_before'], 3)

    def test_string_guid_consumer_is_not_silently_left_dangling(self):
        scene, _ = self.basic()
        scene.write_text(scene.read_text() + '  addressableGuid: ' + A + '\n')
        with self.assertRaisesRegex(ValueError, 'Non-PPtr'):
            plan(self.root)
