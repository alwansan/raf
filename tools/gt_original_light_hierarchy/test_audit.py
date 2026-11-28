import math
import unittest
from types import SimpleNamespace
from tools.gt_original_light_hierarchy.audit import classify, flag, rotate, qnorm, qmul

def obj(name,cid,i,d):
    return SimpleNamespace(type=SimpleNamespace(name=name,value=cid),path_id=i,read_typetree=lambda **kw:d)
def p(i=0,f=0):
    return {"m_FileID":f,"m_PathID":i}
def comps(*ids):
    return [{"component":p(i)} for i in ids]
def xyz(x=0,y=0,z=0):
    return dict(x=x,y=y,z=z)
def transform(go,parent,children=(),q=None):
    return {"m_GameObject":p(go),"m_Father":p(parent),"m_Children":[p(i) for i in children],
            "m_LocalPosition":xyz(),"m_LocalRotation":q or dict(x=0,y=0,z=0,w=1),"m_LocalScale":xyz(1,1,1)}
def fixture(active=True,ancestor=True,enabled=1):
    light={"m_GameObject":p(1),"m_Enabled":enabled}
    leaf={"m_IsActive":active,"m_Component":comps(2,3)}
    root={"m_IsActive":ancestor,"m_Component":comps(5)}
    lt=transform(1,5)
    rt=transform(4,0,[2],dict(x=0,y=math.sqrt(.5),z=0,w=math.sqrt(.5)))
    d=[light,leaf,lt,root,rt]
    rows=[obj(*v) for v in [("Light",108,3,light),("GameObject",1,1,leaf),("Transform",4,2,lt),("GameObject",1,4,root),("Transform",4,5,rt)]]
    return rows,d
class TestHierarchy(unittest.TestCase):
    def test_exact_flag_schemas(self):
        for v,e in [(True,(True,"bool")),(False,(False,"bool")),(1,(True,"int01")),(0,(False,"int01")),(None,(None,"missing")),(1.0,(None,"other")),("1",(None,"other")),(2,(None,"other"))]:
            self.assertEqual(flag(v),e)
    def test_boolean_activity_and_forward(self):
        rows,d=fixture()
        r=classify(rows);c=r["counts"]
        self.assertEqual(c["prior_int_only_would_be_unknown"],1)
        self.assertEqual(c["serialized_light_and_hierarchy_active"],1)
        self.assertEqual(c["composed_forward_differs_from_positive_z"],1)
        self.assertEqual(r["root_depth_histogram"],{"1":1})
        f=rotate(qnorm((0,math.sqrt(.5),0,math.sqrt(.5))),(0,0,1))
        self.assertAlmostEqual(f[0],1)
        self.assertAlmostEqual(f[2],0)
    def test_inactive_ancestor(self):
        c=classify(fixture(ancestor=False)[0])["counts"]
        self.assertEqual(c["owner_self_active_yes"],1)
        self.assertEqual(c["self_active_but_ancestor_inactive"],1)
        self.assertEqual(c["serialized_light_and_hierarchy_inactive"],1)
    def test_disabled_component(self):
        c=classify(fixture(enabled=0)[0])["counts"]
        self.assertEqual(c["hierarchy_active_yes"],1)
        self.assertEqual(c["serialized_light_and_hierarchy_inactive"],1)
    def test_unknown_ancestor(self):
        c=classify(fixture(ancestor="true")[0])["counts"]
        self.assertEqual(c["hierarchy_activation_unknown"],1)
        self.assertNotIn("serialized_light_and_hierarchy_active",c)
    def test_nonreciprocal_light(self):
        rows,d=fixture();d[1]["m_Component"]=comps(2)
        self.assertEqual(classify(rows)["counts"]["unresolved_light_owner_component_mismatch"],1)
    def test_nonreciprocal_parent(self):
        rows,d=fixture();d[4]["m_Children"]=[]
        self.assertEqual(classify(rows)["counts"]["unresolved_parent_child_not_reciprocal"],1)
    def test_cycle(self):
        rows,d=fixture();d[4]["m_Father"]=p(2);d[2]["m_Children"]=[p(5)]
        self.assertEqual(classify(rows)["counts"]["unresolved_hierarchy_cycle"],1)
    def test_external_parent(self):
        rows,d=fixture();d[2]["m_Father"]=p(5,1)
        self.assertEqual(classify(rows)["counts"]["unresolved_external_pointer"],1)
    def test_wrong_transform_owner(self):
        rows,d=fixture();d[2]["m_GameObject"]=p(4)
        self.assertEqual(classify(rows)["counts"]["unresolved_transform_owner_component_mismatch"],1)
    def test_nonfinite_rotation(self):
        rows,d=fixture();d[2]["m_LocalRotation"]["x"]=float("nan")
        c=classify(rows)["counts"]
        self.assertEqual(c["complete_hierarchy"],1)
        self.assertEqual(c["trs_unresolved_transform_nonfinite"],1)
    def test_negative_scale_separate(self):
        rows,d=fixture();d[4]["m_LocalScale"]["x"]=-1
        c=classify(rows)["counts"]
        self.assertEqual(c["negative_scale_on_chain"],1)
        self.assertEqual(c["finite_local_trs_and_composed_forward"],1)
    def test_missing_components_not_complete(self):
        rows,d=fixture();d[1]["m_Component"]=comps(2,3,999)
        self.assertEqual(classify(rows)["counts"]["unresolved_component_missing"],1)
    def test_duplicate_children(self):
        rows,d=fixture();d[4]["m_Children"]=[p(2),p(2)]
        self.assertEqual(classify(rows)["counts"]["unresolved_duplicate_child"],1)
if __name__=="__main__":
    unittest.main()
