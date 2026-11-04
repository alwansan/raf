import copy
from pathlib import Path
import struct
import unittest

from scripts.w5_blur_raster_host import generate
from scripts.w5_blur_recovery import normalize_uniforms


def binary():
    words = [0x07230203, 0x10000, 0, 50, 0,
             (4 << 16) | 32, 10, 2, 5,  # Uniform pointer to reflected struct
             (4 << 16) | 59, 10, 20, 2,
             (4 << 16) | 71, 20, 33, 0,
             (4 << 16) | 71, 20, 34, 0]
    return struct.pack('<%dI' % len(words), *words)


def fixture():
    plan = {'buffers': [dict(slot=0, allocation_bytes=80, name='$Globals', members=[
        dict(name='FixtureValue', kind='vector', serialized_dimension=1, serialized_index=32)])]}
    original = {'ubos': [dict(name='cb4_struct', type='_5', block_size=64)],
                'types': {'_5': {'members': [dict(name='cb0_0_m0', type='vec4', offset=0)]}}}
    rebuilt = {'ubos': [dict(name='__raft_w5_Globals', type='_5', block_size=80)],
               'types': {'_5': {'members': [dict(name='FixtureValue', type='float', offset=32)]}}}
    return plan, original, rebuilt


class RecoveryTests(unittest.TestCase):
    def test_slot_identity_maps_both_programs_to_same_descriptor(self):
        plan, original, rebuilt = fixture()
        old = normalize_uniforms(binary(), original, plan, 0, False)
        new = normalize_uniforms(binary(), rebuilt, plan, 0, True)
        self.assertEqual(old, new)
        self.assertEqual(struct.unpack('<%dI' % (len(old) // 4), old)[16], 6)

    def test_reject_trimmed_or_shifted_named_layout(self):
        plan, _, rebuilt = fixture()
        for mode in ('size', 'offset', 'type', 'name'):
            candidate = copy.deepcopy(rebuilt)
            if mode == 'size':
                candidate['ubos'][0]['block_size'] = 64
            else:
                candidate['types']['_5']['members'][0][mode] = {'offset': 36, 'type': 'vec2', 'name': 'Wrong'}[mode]
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                normalize_uniforms(binary(), candidate, plan, 0, True)

    def test_reject_unresolved_or_duplicate_original_slots(self):
        plan, original, _ = fixture()
        for mode in ('wrong_slot', 'missing', 'duplicate'):
            candidate = copy.deepcopy(original)
            if mode == 'wrong_slot':
                candidate['types']['_5']['members'][0]['name'] = 'cb1_0_m0'
            elif mode == 'missing':
                candidate['ubos'] = []
            else:
                candidate['ubos'].append(copy.deepcopy(candidate['ubos'][0]))
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                normalize_uniforms(binary(), candidate, plan, 0, False)

    def test_host_template_pin_and_no_changes_to_w1_source(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/w1_depth_raster_vulkan.cpp'
        source = path.read_text()
        candidate = generate(source)
        self.assertIn('VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,6', candidate)
        self.assertIn('mutation==7', candidate)
        self.assertEqual(source, path.read_text())
        with self.assertRaises(ValueError):
            generate(source + '\n')


if __name__ == '__main__':
    unittest.main()
