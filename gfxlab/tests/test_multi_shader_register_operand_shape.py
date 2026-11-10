import unittest,struct
from gfxlab.tools.multi_shader_register_operand_shape import declaration_operand,scan_declarations

def stream(*items):
    words=[0x50,2+len(items),*items]
    return struct.pack("<%dI"%len(words),*words)
def operand(kind,dimension):
    return (kind<<12)|(dimension<<20)

class TestDXBCSourceOperandShape(unittest.TestCase):
    def test_immediate_slot_resource_cb_sampler(self):
        r=declaration_operand(88,[(4<<24)|88,operand(7,1),3,0])
        c=declaration_operand(89,[(4<<24)|89,operand(8,2),0,19])
        s=declaration_operand(90,[(3<<24)|90,operand(6,1),2])
        self.assertEqual(r,("resource",(3,)))
        self.assertEqual(c,("constant_buffer",(0,19)))
        self.assertEqual(s,("sampler",(2,)))
    def test_strict_wrong_operand_type_rejects(self):
        with self.assertRaises(ValueError):
            declaration_operand(89,[89,operand(7,2),0,8])
    def test_relative_index_rejects(self):
        with self.assertRaises(ValueError):
            declaration_operand(88,[88,operand(7,1)|(2<<22),0])
    def test_length_and_duplicate_slot(self):
        w=[(4<<24)|89,operand(8,2),0,19,
           (4<<24)|89,operand(8,2),0,19,
           (4<<24)|88,operand(7,1),4,0,
           (3<<24)|90,operand(6,1),2]
        x=scan_declarations(stream(*w))
        self.assertEqual(x["constant_buffer_declarations"],2)
        self.assertEqual(x["constant_buffer_distinct_register_slots"],1)
        self.assertEqual(x["constant_buffer_duplicate_slot_declarations"],1)
        self.assertEqual(x["constant_buffers_with_nonzero_declaration_size"],1)
        self.assertFalse(x["source_register_numbers_exported"])
