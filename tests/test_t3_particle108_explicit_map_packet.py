"""Synthetic-only source DCL → explicit VKD3D v1.2 graphics private map packets."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_particle108_explicit_map_packet as m

SOURCE=(
    ("sampler",90,(1,)),
    ("srv",88,(3,)),
    ("cbuffer",89,(2,8)),
)

class T3GraphicsExplicitPacketTests(unittest.TestCase):
    def test_stage_declarations_to_two_distinct_private_packets(self):
        packets,safe=m.private_packets(SOURCE,1)
        self.assertEqual(set(packets),{"A","B"})
        self.assertTrue(packets["A"].startswith("T3MAP1 V A 3\n"))
        self.assertTrue(packets["B"].startswith("T3MAP1 V B 3\n"))
        self.assertEqual(safe["source_stage_resource_count"],3)
        self.assertEqual((safe["source_stage_cbuffer_count"],
                          safe["source_stage_srv_count"],
                          safe["source_stage_sampler_count"]),(1,1,1))
        self.assertFalse(safe["private_source_registers_and_descriptor_coordinates_published"])
        for private in ('"T3MAP1"','"cb2"','"t3"','"s1"'):
            self.assertNotIn(private,json.dumps(safe))
        self.assertTrue(safe["binding_request_is_NOT_SPIRV_binding_proof"])

    def test_stage_visibility_is_not_exchanged(self):
        vertex,_=m.private_packets(SOURCE,1)
        fragment,_=m.private_packets(SOURCE,0)
        self.assertIn(" V A ",vertex["A"].splitlines()[0])
        self.assertIn(" P A ",fragment["A"].splitlines()[0])

    def test_order_of_original_dcl_declarations_cannot_change_mapping(self):
        a,_=m.private_packets(SOURCE,1)
        b,_=m.private_packets(tuple(reversed(SOURCE)),1)
        self.assertEqual(a,b)

    def test_two_profiles_do_not_reuse_destination_descriptor_coordinates(self):
        a,_=m.private_packets(SOURCE,0)
        targets=[]
        for name,body in a.items():
            rows=[tuple(line.split()[-2:]) for line in body.splitlines()[1:]]
            self.assertEqual(len(rows),len(set(rows)))
            targets.extend(rows)
        self.assertEqual(len(targets),len(set(targets)))

    def test_bool_or_negative_source_register_is_rejected(self):
        for invalid in (True,-1,4096,1.5,"3"):
            with self.subTest(value=invalid),self.assertRaisesRegex(
                ValueError,"T3_INVALID_PRIVATE_EXPLICIT_DCL_RECORD"):
                m.private_packets((("srv",88,(invalid,)),),1)

    def test_2d_second_index_is_not_mistaken_as_register_identity(self):
        source=(("cbuffer",89,(2,9)),)
        a,_=m.private_packets(source,1)
        b,_=m.private_packets((("cbuffer",89,(2,11)),),1)
        self.assertEqual(a,b)

    def test_source_register_duplicate_fails_closed_even_if_different_opcode(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_REGISTER_COLLISION"):
            m.private_packets((("srv",88,(3,)),("srv",161,(3,))),0)

    def test_unknown_source_declaration_and_opcode_family_rejected(self):
        for record in (("srv",90,(1,)),("srv",123,(1,)),("unknown",88,(1,)),
                       ("srv",88,(1,2,3)),("srv",88,())):
            with self.subTest(record=record),self.assertRaises(ValueError):
                m.private_packets((record,),1)

    def test_missing_stage_or_overbudget_source_scope_rejected(self):
        with self.assertRaises(ValueError):
            m.private_packets(SOURCE,True)
        with self.assertRaises(ValueError):
            m.private_packets((),1)
        with self.assertRaises(ValueError):
            m.private_packets((("cbuffer",89,(1,)),)*65,1)

    def test_private_packet_write_is_exclusive_and_directory_bounded(self):
        packet,_=m.private_packets(SOURCE,1)
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            files=m.private_write_packets(packet,folder)
            self.assertEqual(set(files),set(m.PROFILE_TARGET))
            self.assertEqual(files["A"].read_text(),packet["A"])
            with self.assertRaisesRegex(ValueError,"T3_PRIVATE_PACKET_PREEXISTING"):
                m.private_write_packets(packet,folder)

    def test_bad_packet_destination_rejected(self):
        packet,_=m.private_packets(SOURCE,1)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"T3_PRIVATE_PACKET_DESTINATION"):
                m.private_write_packets(packet,Path(d)/"uncreated")
            with self.assertRaisesRegex(ValueError,"T3_PRIVATE_PACKET_DESTINATION"):
                m.private_write_packets({"A":packet["A"]},Path(d))

if __name__=="__main__":
    unittest.main()
