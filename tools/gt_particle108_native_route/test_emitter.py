import unittest
from tools.gt_particle108_native_route.emitter import emitter_link,select_material,Reject
def ptr(n):return {"m_FileID":0,"m_PathID":n}
class EmitterTests(unittest.TestCase):
    def setUp(self):
        self.r=("level0",10);self.p=("level0",11)
        self.classes={self.r:"ParticleSystemRenderer",self.p:"ParticleSystem"}
        self.go={"m_Component":[{"component":ptr(10)},{"component":ptr(11)}]}
    def join(self):return emitter_link("level0",[],self.go,self.r,self.classes)
    def test_exact(self):self.assertEqual(self.join(),self.p)
    def test_wrong_renderer(self):
        self.go["m_Component"][0]={"component":ptr(99)}
        with self.assertRaises(Reject):self.join()
    def test_duplicate(self):
        self.go["m_Component"].append({"component":ptr(11)})
        with self.assertRaises(Reject):self.join()
    def test_wrong_class(self):
        self.classes[self.p]="MeshRenderer"
        with self.assertRaises(Reject):self.join()
    def test_ambiguous(self):
        self.classes[("level0",12)]="ParticleSystem"
        self.go["m_Component"].append({"component":ptr(12)})
        with self.assertRaises(Reject):self.join()
    def test_native_owner_scoped(self):
        self.assertEqual(select_material({("a",1):{"x":((0,5),None)},("b",1):{"x":((0,5),None)}},("a",5)),{("a",1)})
    def test_multiple_materials(self):
        with self.assertRaises(Reject):
            select_material({("a",1):{"x":((0,5),None)},("a",2):{"x":((0,5),None)}},("a",5))
if __name__=="__main__":unittest.main()
