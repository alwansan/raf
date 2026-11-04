"""W2 fail-closed tests for the Settings-panel route probe (synthetic only).

Covers: transform-child edge resolution (children edges point to child
RectTransforms, resolved to GameObjects via m_GameObject), the two-direction
Settings→Canvas census, dangling Settings instances, clamp bounds and
leak guards (no names, path IDs, or settings values in output).
"""

from __future__ import annotations

import contextlib
import json
import sys
import types
import unittest

from scripts.probe_w2_settings_panel_route import (
    CANVAS_CLASS,
    SCALER_CLASS,
    TARGET_SETTINGS_CLASS,
    SCHEMA_VERSION,
    canvas_route_census,
    subtree_walk,
    walk_settings_route,
)
from scripts.probe_w2_settings_panel_route import OwnerView


def _obj(path_id, type_name, tree):
    o = types.SimpleNamespace()
    o.path_id = path_id
    o.type = types.SimpleNamespace(name=type_name)
    o.read_typetree = lambda check_read=True: tree
    return o


def _rect(path_id, go_pid, father=None, children=()):
    return {"m_GameObject": {"m_FileID": 0, "m_PathID": go_pid},
            "m_Father": father or {"m_FileID": 0, "m_PathID": 0},
            "m_Children": [{"m_FileID": 0, "m_PathID": c} for c in children]}


def _go(path_id, components):
    return {"m_Component": [{"component": {"m_FileID": 0, "m_PathID": pid}}
                            for pid in components]}


class Env:
    def __init__(self, objects):
        self.objects = objects


def build_world():
    """Topology: settings manager GO(2) --rect 3--> canvas GO(5) --rect 4-->
    mid GO(9) --rect 6--> mid2 GO(14) --rect 15--> box GO(12)."""
    objs = [
        _obj(1, "MonoBehaviour", {"m_GameObject": {"m_FileID": 0, "m_PathID": 2},
                                  "m_Script": {"m_FileID": 0, "m_PathID": 80}}),
        _obj(80, "MonoScript", {"m_ClassName": TARGET_SETTINGS_CLASS}),
        _obj(2, "GameObject", _go(2, [1, 3])),
        _obj(3, "Transform", _rect(3, 2,
                                   father={"m_FileID": 0, "m_PathID": 0},
                                   children=[4])),
        _obj(4, "RectTransform", _rect(4, 5,
                                       father={"m_FileID": 0, "m_PathID": 3},
                                       children=[6])),
        _obj(5, "GameObject", _go(5, [4, 7, 8])),
        _obj(7, "Canvas", {"m_GameObject": {"m_FileID": 0, "m_PathID": 5}}),
        _obj(8, "MonoBehaviour", {"m_GameObject": {"m_FileID": 0, "m_PathID": 5},
                                  "m_Script": {"m_FileID": 0, "m_PathID": 81}}),
        _obj(81, "MonoScript", {"m_ClassName": SCALER_CLASS}),
        _obj(6, "RectTransform", _rect(6, 9,
                                       father={"m_FileID": 0, "m_PathID": 4},
                                       children=[15])),
        _obj(9, "GameObject", _go(9, [6])),
        _obj(15, "RectTransform", _rect(15, 14,
                                        father={"m_FileID": 0, "m_PathID": 6},
                                        children=[11])),
        _obj(14, "GameObject", _go(14, [15])),
        _obj(11, "RectTransform", _rect(11, 12,
                                        father={"m_FileID": 0, "m_PathID": 15},
                                        children=[])),
        _obj(12, "GameObject", _go(12, [11, 13])),
        _obj(13, "MonoBehaviour", {"m_GameObject": {"m_FileID": 0, "m_PathID": 12},
                                   "m_Script": {"m_FileID": 0, "m_PathID": 82}}),
        _obj(82, "MonoScript", {"m_ClassName": "GraphicsSettingsBox"}),
    ]
    classes = {1: TARGET_SETTINGS_CLASS, 3: "Transform", 4: "RectTransform",
               6: "RectTransform", 7: CANVAS_CLASS, 8: SCALER_CLASS,
               11: "RectTransform", 13: "GraphicsSettingsBox",
               15: "RectTransform"}
    return Env(objs), classes


class RouteTests(unittest.TestCase):
    def setUp(self):
        env, classes = build_world()
        self.view = OwnerView(env, classes, {})

    def test_schema(self):
        self.assertEqual(SCHEMA_VERSION, 1)

    def test_subtree_resolves_transform_child_edges(self):
        # box GO is three hops below the canvas GO (canvas -> mid -> mid2 -> box)
        tree = subtree_walk(self.view, 5)
        classes_at_depth3 = [n for n in tree if n["depth"] == 3]
        self.assertEqual(len(classes_at_depth3), 1)
        self.assertIn("GraphicsSettingsBox", classes_at_depth3[0]["classes"])

    def test_canvas_route_census_finds_scaler_family_route(self):
        census = canvas_route_census(self.view)
        self.assertEqual(census["canvases"], 1)
        self.assertEqual(census["canvasScalerSiblingCount"], 1)
        self.assertEqual(census["canvasScalerRoutesWithSettingsFamily"], 1)
        entry = census["routes"][0]
        self.assertEqual(entry["canvasScalerSibling"], 1)
        self.assertEqual(entry["settingsFamilyInSubtree"]["GraphicsSettingsBox"], 1)
        self.assertEqual(entry["settingsFamilyDepths"]["GraphicsSettingsBox"], 3)

    def test_walk_settings_route_complete(self):
        route = walk_settings_route(self.view, 1)
        self.assertEqual(route["gameobjectLinked"], 1)
        self.assertEqual(route["danglingInstance"], 0)
        self.assertEqual(route["routeComplete"], 1)
        self.assertEqual(route["canvasAncestorsAbove"], 0)
        self.assertEqual(route["canvasNodesInSubtree"], 1)
        self.assertEqual(route["canvasScalerOnCanvasNodeCount"], 1)
        blob = json.dumps(route)
        for forbidden in ("m_Name", "m_PathID", "scaleFactor", "referenceResolution"):
            self.assertNotIn(forbidden, blob)

    def test_dangling_settings_instance(self):
        dangling = _obj(55, "MonoBehaviour",
                        {"m_GameObject": {"m_FileID": 0, "m_PathID": 0},
                         "m_Script": {"m_FileID": 0, "m_PathID": 80}})
        merged = {**self.view.classes, 55: TARGET_SETTINGS_CLASS}
        env = Env(self.view.env.objects + [dangling])
        view = OwnerView(env, merged, {})
        route = walk_settings_route(view, 55)
        self.assertEqual(route["danglingInstance"], 1)
        self.assertEqual(route["gameobjectLinked"], 0)
        self.assertEqual(route["routeComplete"], 0)

    def test_unlinked_go_returns_zero_on_route(self):
        orphan = _obj(56, "MonoBehaviour",
                      {"m_GameObject": "not-a-dict",
                       "m_Script": {"m_FileID": 0, "m_PathID": 80}})
        merged = {**self.view.classes, 56: TARGET_SETTINGS_CLASS}
        env = Env(self.view.env.objects + [orphan])
        view = OwnerView(env, merged, {})
        route = walk_settings_route(view, 56)
        self.assertEqual(route["danglingInstance"], 1)

    def test_depth_cap(self):
        # a chain longer than 32 must not expand further in the subtree
        env, classes = build_world()
        objs = list(env.objects)
        prev = 11
        chain = []
        for i in range(40):
            rect_pid = 500 + i
            go_pid = 600 + i
            objs.append(_obj(rect_pid, "RectTransform", _rect(
                rect_pid, go_pid,
                father={"m_FileID": 0, "m_PathID": prev},
                children=[rect_pid + 1])))
            objs.append(_obj(go_pid, "GameObject", _go(go_pid, [rect_pid])))
            chain.append(go_pid)
            prev = rect_pid
        view = OwnerView(Env(objs), classes, {})
        # start from box (10): descending beyond depth cap must stop
        tree = subtree_walk(view, 10)
        self.assertTrue(all(n["depth"] <= 32 for n in tree))


if __name__ == "__main__":
    unittest.main()
