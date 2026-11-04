from pathlib import Path
import struct
import tempfile
import unittest
from scripts.repair_exported_mesh_vertices import repair, load_mesh
from scripts.compare_exported_mesh_geometry import positions


def mesh(project, name, guid, raw=None, index_format=0):
    path = project / 'Assets/Mesh' / (name + '.asset')
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = '' if raw is None else raw.hex()
    size = 0 if raw is None else len(raw)
    text = f'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!43 &4300000
Mesh:
  m_Name: {name}
  m_IndexFormat: {index_format}
  m_IndexBuffer: "000001000200"
  m_SubMeshes:
  - firstByte: 0
    indexCount: 3
  m_VertexData:
    m_VertexCount: 3
    m_Channels:
    - stream: 0
      offset: 0
      format: 0
      dimension: 3
    m_DataSize: {size}
    _typelessdata: {encoded}
  m_Unrelated: keep-this-value
'''
    path.write_text(text)
    path.with_suffix('.asset.meta').write_text('fileFormatVersion: 2\nguid: ' + guid + '\nuserData: retained\n')
    return path


class VertexRestorationTests(unittest.TestCase):
    def test_repair_retains_target_meta_scene_references_and_other_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target, provider = root / 'target', root / 'provider'
            original = mesh(target, 'A', 'a' * 32)
            raw = struct.pack('<9f', 0, 0, 0, 1, 0, 0, 0, 1, 0)
            mesh(provider, 'A', 'b' * 32, raw)
            meta_before = original.with_suffix('.asset.meta').read_bytes()
            scene = target / 'Assets/test.unity'
            scene.write_text('m_Mesh: {fileID: 4300000, guid: ' + 'a' * 32 + '}\n')
            scene_before = scene.read_bytes()
            report = repair(target, provider, {'A'}, root / 'snapshot')
            self.assertEqual(report['restored_meshes'], 1)
            self.assertEqual(original.with_suffix('.asset.meta').read_bytes(), meta_before)
            self.assertEqual(scene.read_bytes(), scene_before)
            self.assertEqual(load_mesh(original.read_text())['m_Unrelated'], 'keep-this-value')
            self.assertEqual(len(positions(load_mesh(original.read_text()))), 3)
            self.assertIn('_typelessdata: \n', (root / 'snapshot/Assets/Mesh/A.asset').read_text())

    def test_one_bad_identity_refuses_all_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target, provider = root / 'target', root / 'provider'
            raw = struct.pack('<9f', *([0.] * 9))
            a, b = mesh(target, 'A', 'a' * 32), mesh(target, 'B', 'b' * 32)
            mesh(provider, 'A', 'c' * 32, raw)
            mesh(provider, 'B', 'd' * 32, raw, index_format=1)
            originals = [p.read_bytes() for p in (a, b)]
            with self.assertRaisesRegex(ValueError, 'identity changed'):
                repair(target, provider, {'A', 'B'}, root / 'snapshot')
            self.assertEqual([p.read_bytes() for p in (a, b)], originals)
            self.assertFalse((root / 'snapshot').exists())

    def test_nonfinite_provider_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = mesh(root / 'target', 'A', 'a' * 32)
            before = original.read_bytes()
            mesh(root / 'provider', 'A', 'b' * 32,
                 struct.pack('<9f', float('nan'), *([0.] * 8)))
            with self.assertRaisesRegex(ValueError, 'non-finite'):
                repair(root / 'target', root / 'provider', {'A'}, root / 'snapshot')
            self.assertEqual(original.read_bytes(), before)

    def test_refuse_symlinked_target_mesh_and_meta_before_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target, provider = root / 'target', root / 'provider'
            original = mesh(target, 'A', 'a' * 32)
            external = root / 'external.asset'
            external.write_bytes(original.read_bytes())
            original.unlink()
            original.symlink_to(external)
            with self.assertRaisesRegex(ValueError, 'Unsafe Mesh YAML asset link'):
                repair(target, provider, {'A'}, root / 'snapshot')
            self.assertEqual(external.read_bytes(), original.read_bytes())
            self.assertFalse((root / 'snapshot').exists())
            original.unlink()
            original.write_bytes(external.read_bytes())
            meta = original.with_suffix('.asset.meta')
            external_meta = root / 'external.meta'
            external_meta.write_bytes(meta.read_bytes())
            meta.unlink()
            meta.symlink_to(external_meta)
            with self.assertRaisesRegex(ValueError, 'unsafe Mesh .meta link'):
                repair(target, provider, {'A'}, root / 'snapshot')
            self.assertEqual(external_meta.read_bytes(), meta.read_bytes())
            self.assertFalse((root / 'snapshot').exists())

    def test_refuse_symlinked_provider_and_unowned_hardlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target, provider = root / 'target', root / 'provider'
            mesh(target, 'A', 'a' * 32)
            original = mesh(provider, 'A', 'b' * 32, struct.pack('<9f', *([0.] * 9)))
            original_meta = original.with_suffix('.asset.meta')
            outside = root / 'original-other-copy'
            outside.write_bytes(original.read_bytes())
            original.unlink()
            original.symlink_to(outside)
            with self.assertRaisesRegex(ValueError, 'Unsafe Mesh YAML asset link'):
                repair(target, provider, {'A'}, root / 'snapshot')
            original.unlink()
            original.hardlink_to(outside)
            with self.assertRaisesRegex(ValueError, 'Unsafe Mesh YAML asset link'):
                repair(target, provider, {'A'}, root / 'snapshot')
            original.unlink()
            original.write_bytes(outside.read_bytes())
            external_meta = root / 'meta-other-copy'
            external_meta.write_bytes(original_meta.read_bytes())
            original_meta.unlink()
            original_meta.hardlink_to(external_meta)
            with self.assertRaisesRegex(ValueError, 'unsafe Mesh .meta link'):
                repair(target, provider, {'A'}, root / 'snapshot')
            self.assertFalse((root / 'snapshot').exists())

    def test_refuse_symlinked_mesh_directory_and_dangling_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target, provider = root / 'target', root / 'provider'
            original = mesh(target, 'A', 'a' * 32)
            mesh(provider, 'A', 'b' * 32, struct.pack('<9f', *([0.] * 9)))
            directory = original.parent
            external = root / 'foreign-mesh-directory'
            directory.rename(external)
            directory.symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'Unsafe Mesh directory symlink'):
                repair(target, provider, {'A'}, root / 'snapshot')
            directory.unlink()
            external.rename(directory)
            snapshot = root / 'snapshot'
            snapshot.symlink_to(root / 'missing-snapshot', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'Snapshot destination'):
                repair(target, provider, {'A'}, snapshot)
