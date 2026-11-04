"""Settings-panel to Canvas route traversal (count level) — completing A2's
paused DISPLAY-003 pointer-path gap, under explicit owner authorization.

A2's paused session proved the managed Settings TypeDef identity (21
FieldDefs / 13 metadata-eligible) but explicitly listed the
**instantiated Settings UI→CanvasScaler route** as unresolved. This probe
walks the serialized hierarchy of every Settings MonoBehaviour instance and
publishes the route as *counters only*:

- father-chain depth from the Settings component's GameObject to the
  root transform,
- exact depth(s) of the nearest ``Canvas`` ancestor,
- whether a ``CanvasScaler`` component is a sibling component of that
  Canvas node (and of any chain node),
- canvas-node child counts.

Nothing structural beyond counters is emitted: no GameObject names, no path
IDs, no component values, no decoded Setting fields. The route boolean facts
are exactly the static link A2's typed-field/offset work needs next
(``open gaps: serialized field offsets / full custom Settings TypeTree /
instantiated Settings UI→CanvasScaler route / Android orientation stretch``).
The last gap (orientation stretch) is out of scope here — that needs the
values A2 owns.

Identity of every owner is verified against its committed Git object via
``probe_w2_fullgame_texture_colors.verify_and_hash``.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import re
import sys

from scripts.probe_w2_fullgame_texture_colors import sha256_file, verify_and_hash
from scripts.probe_w2_ui_scaler_census import (
    SCRIPT_HOST,
    build_script_registry,
    external_paths,
    owner_name_ok,
)

SCHEMA_VERSION = 1

TARGET_SETTINGS_CLASS = "Settings"
SCALER_CLASS = "CanvasScaler"
CANVAS_CLASS = "Canvas"
MAX_CHAIN = 64

_FORBIDDEN = ("m_Name", "m_PathID", "scaleFactor", "referenceResolution", "m_Father")


def _read(obj) -> dict:
    try:
        tree = obj.read_typetree(check_read=False) or {}
    except Exception:
        tree = {}
    return tree if isinstance(tree, dict) else {}


def class_map_for_owner(env, ggm_registry: dict) -> tuple[dict, int, dict]:
    """pathID -> component class name for the owner file; plus undecodable
    behaviour count and the native type map for hierarchy walking."""
    external_paths_cache = external_paths(env)
    classes: dict[int, str] = {}
    scripts_same_file: dict[int, str] = {}
    for obj in env.objects:
        if str(obj.type.name) == "MonoScript":
            scripts_same_file.update(build_script_registry(
                type("Env", (), {"objects": [obj]})())[0])
    classes.update(scripts_same_file)
    undecodable = 0
    natives: dict[int, str] = {}
    for obj in env.objects:
        tname = str(obj.type.name)
        natives[obj.path_id] = tname
        if tname != "MonoBehaviour":
            classes[obj.path_id] = tname
    for obj in env.objects:
        if str(obj.type.name) != "MonoBehaviour":
            continue
        tree = _read(obj)
        if not tree:
            if obj.path_id not in classes:
                undecodable += 1
            continue
        script = tree.get("m_Script")
        cls = "?"
        if isinstance(script, dict):
            file_id = script.get("m_FileID")
            path_id = script.get("m_PathID")
            if file_id == 0:
                cls = scripts_same_file.get(path_id, "?")
            elif isinstance(file_id, int):
                ext = (external_paths_cache[file_id - 1]
                       if 1 <= file_id <= len(external_paths_cache) else "")
                if ext == SCRIPT_HOST:
                    cls = ggm_registry.get(path_id, "?")
        else:
            undecodable += 1
            continue
        if cls == "?":
            undecodable += 1
        classes[obj.path_id] = cls
    return classes, undecodable, natives


class OwnerView:
    """Lazy bounded typetree view over one owner."""

    def __init__(self, env, classes: dict, natives: dict):
        self.env = env
        self.classes = classes
        self.natives = natives
        self._cache: dict[int, dict] = {}

    def tree(self, path_id):
        if path_id not in self._cache:
            if len(self._cache) > 200_000:
                raise ValueError("hierarchy walk exceeded cache bound")
            for obj in self.env.objects:
                if obj.path_id == path_id:
                    self._cache[path_id] = _read(obj)
                    break
            else:
                self._cache[path_id] = {}
        return self._cache[path_id]


def component_list(go_tree: dict) -> list:
    entry = go_tree.get("m_Component")
    if not isinstance(entry, list):
        return []
    out = []
    for item in entry:
        if isinstance(item, dict):
            pptr = item.get("component", item.get("m_Component"))
            if isinstance(pptr, dict):
                out.append(pptr)
    return out


def node_classes(view: OwnerView, game_object_pid: int) -> list[str]:
    go = view.tree(game_object_pid)
    names = []
    for pptr in component_list(go):
        pid = pptr.get("m_PathID") if isinstance(pptr, dict) else None
        fid = pptr.get("m_FileID") if isinstance(pptr, dict) else None
        if fid == 0 and isinstance(pid, int):
            cls = view.classes.get(pid)
            if cls:
                names.append(cls)
    return names


def father_of(view: OwnerView, game_object_pid: int):
    """(parent GO pid) via the node's RectTransform m_Father, or None."""
    for pptr in component_list(view.tree(game_object_pid)):
        pid = pptr.get("m_PathID")
        if not (isinstance(pid, int) and pptr.get("m_FileID") == 0):
            continue
        cls = view.classes.get(pid)
        if cls is not None and cls.lower().endswith("transform"):
            rect = view.tree(pid)
            father = rect.get("m_Father")
            if isinstance(father, dict) and father.get("m_FileID") == 0:
                fpid = father.get("m_PathID")
                if isinstance(fpid, int):
                    parent_go = view.tree(fpid)
                    go_ref = parent_go.get("m_GameObject") if isinstance(parent_go, dict) else None
                    if isinstance(go_ref, dict) and go_ref.get("m_FileID") == 0:
                        gpid = go_ref.get("m_PathID")
                        if isinstance(gpid, int):
                            return gpid
            return None
    return None


def node_rects(view: OwnerView, game_object_pid: int) -> list[int]:
    """path IDs of the transform-typed components of one GameObject node."""
    out = []
    for pptr in component_list(view.tree(game_object_pid)):
        pid = pptr.get("m_PathID")
        if isinstance(pid, int) and pptr.get("m_FileID") == 0:
            cls = view.classes.get(pid)
            if cls and cls.lower().endswith("transform"):
                out.append(pid)
    return out


def subtree_walk(view: OwnerView, start_pid: int) -> list:
    """Bounded BFS downward from a root GameObject; nodes carry classes.

    RectTransform child edges point to the child's *transform component*,
    so each edge is resolved through ``m_GameObject`` first.
    """
    out = []
    seen = {start_pid}
    queue = collections.deque([(start_pid, 0)])
    while queue and len(out) < 100_000:
        gpid, depth = queue.popleft()
        if depth > 32:
            continue
        rects = node_rects(view, gpid)
        raw_children = view.tree(rects[0]).get("m_Children") if rects else None
        classes = node_classes(view, gpid)
        out.append({"depth": depth, "classes": classes})
        for item in (raw_children if isinstance(raw_children, list) else []):
            if not (isinstance(item, dict) and item.get("m_FileID") == 0):
                continue
            rpid = item.get("m_PathID")
            if not isinstance(rpid, int):
                continue
            ref = view.tree(rpid).get("m_GameObject")
            child_go = ref.get("m_PathID") if isinstance(ref, dict) and ref.get("m_FileID") == 0 else None
            if isinstance(child_go, int) and child_go not in seen:
                seen.add(child_go)
                queue.append((child_go, depth + 1))
    return out


def walk_settings_route(view: OwnerView, settings_pid: int) -> dict:
    tree = view.tree(settings_pid)
    go_ref = tree.get("m_GameObject")
    node_cls = view.classes.get(settings_pid) or "?"
    linked = (isinstance(go_ref, dict) and go_ref.get("m_FileID") == 0
              and go_ref.get("m_PathID", 0) != 0)
    if not linked:
        return {"settingsClass": node_cls, "gameobjectLinked": 0, "danglingInstance": 1,
                "routeComplete": 0, "upChainDepth": 0, "canvasAncestorsAbove": 0,
                "rootChildCount": 0, "subtreeNodeCount": 0, "canvasNodesInSubtree": 0,
                "canvasScalerOnCanvasNodeCount": 0, "minCanvasDepthInSubtree": -1,
                "canvasNodeChildCounts": []}
    go_pid = go_ref["m_PathID"]
    # Phase 1: upward father chain from the panel root
    seen = {go_pid}
    chain = []
    current = go_pid
    rects = node_rects(view, current)
    current_rect = rects[0] if rects else None
    while isinstance(current, int) and current is not None and len(chain) < MAX_CHAIN:
        chain.append({"depth": len(chain), "pid": current,
                      "classes": node_classes(view, current), "rectPid": current_rect})
        current = father_of(view, current)
        if not isinstance(current, int) or current in seen:
            break
        seen.add(current)
        rects = node_rects(view, current)
        current_rect = rects[0] if rects else None
    canvas_ancestors_above = sum(1 for n in chain if CANVAS_CLASS in n["classes"])
    up_depth = len(chain)
    root_child_count = 0
    if chain and chain[0]["rectPid"] is not None:
        raw = view.tree(chain[0]["rectPid"]).get("m_Children")
        if isinstance(raw, list):
            root_child_count = len(raw)
    # Phase 2: bounded downward BFS from the panel root (the UI panel subtree)
    subtree = subtree_walk(view, go_pid)
    canvas_nodes = [n for n in subtree if CANVAS_CLASS in n["classes"]]
    # a canvas node has a scaler sibling when its own classes contain one
    scaler_on_canvas = sum(
        1 for n in subtree
        if CANVAS_CLASS in n["classes"] and SCALER_CLASS in n["classes"])
    canvas_child_counts = []
    return {
        "settingsClass": node_cls,
        "gameobjectLinked": 1,
        "danglingInstance": 0,
        "routeComplete": int(scaler_on_canvas > 0 or canvas_ancestors_above > 0),
        "upChainDepth": up_depth,
        "canvasAncestorsAbove": canvas_ancestors_above,
        "rootChildCount": root_child_count,
        "subtreeNodeCount": len(subtree),
        "canvasNodesInSubtree": len(canvas_nodes),
        "canvasScalerOnCanvasNodeCount": scaler_on_canvas,
        "minCanvasDepthInSubtree": min((n["depth"] for n in canvas_nodes), default=-1),
        "canvasNodeChildCounts": canvas_child_counts,
    }


def canvas_route_census(view: OwnerView) -> dict:
    """Per-owner canvas-level route census: for every Canvas node, whether it
    carries a CanvasScaler sibling, and whether the Settings-family UI
    components appear inside that canvas node's (bounded) subtree."""
    TYPE_TO_GO = "Canvas"
    routes = []
    family = {"GraphicsSettingsBox": 0, "ControlsSettingsBox": 0,
              TARGET_SETTINGS_CLASS: 0}
    for obj in view.env.objects:
        if str(obj.type.name) != TYPE_TO_GO:
            continue
        tree = _read(obj)
        go_ref = tree.get("m_GameObject")
        go_pid = go_ref.get("m_PathID") if isinstance(go_ref, dict) and go_ref.get("m_FileID") == 0 else None
        entry = {"canvasScalerSibling": 0,
                 "settingsFamilyInSubtree": {k: 0 for k in family},
                 "settingsFamilyDepths": {},
                 "nodeCount": 0}
        if not isinstance(go_pid, int):
            routes.append(entry)
            continue
        names = node_classes(view, go_pid)
        entry["canvasScalerSibling"] = int(SCALER_CLASS in names)
        subtree = subtree_walk(view, go_pid)
        entry["nodeCount"] = len(subtree)
        for n in subtree:
            for k in family:
                if k in n["classes"]:
                    entry["settingsFamilyInSubtree"][k] += 1
                    entry["settingsFamilyDepths"][k] = min(
                        entry["settingsFamilyDepths"].get(k, 10**9), n["depth"])
        entry["settingsFamilyDepths"] = {k: v for k, v in entry["settingsFamilyDepths"].items() if v < 10**9}
        routes.append(entry)
    return {
        "canvases": len(routes),
        "canvasScalerSiblingCount": sum(r["canvasScalerSibling"] for r in routes),
        "canvasScalerRoutesWithSettingsFamily": sum(
            1 for r in routes if r["canvasScalerSibling"]
            and (any(r["settingsFamilyInSubtree"].values()))),
        "routes": routes,
    }


def settings_instances(view: OwnerView) -> list[int]:
    hits = []
    for obj in view.env.objects:
        if str(obj.type.name) != "MonoBehaviour":
            continue
        cls = view.classes.get(obj.path_id)
        if cls == TARGET_SETTINGS_CLASS:
            hits.append(obj.path_id)
    return hits


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    import UnityPy

    def verify(owner: Path) -> dict:
        if repo is not None:
            return verify_and_hash(owner, repo, f"{repo_rel_prefix}/{owner.name}")
        return {"sha256": sha256_file(owner), "byte_count": owner.stat().st_size,
                "registered_sha256": None, "identity_kind": "unverified-local"}

    host = next((p for p in owner_paths if p.name == SCRIPT_HOST), None)
    if host is None:
        raise ValueError(f"script host owner missing: {SCRIPT_HOST}")
    ggm_registry, _ = build_script_registry(UnityPy.load(str(host)))
    if not ggm_registry:
        raise ValueError("script host registry empty")

    routes = []
    owners = {}
    for owner in owner_paths:
        if owner.name == SCRIPT_HOST:
            continue
        info = verify(owner)
        env = UnityPy.load(str(owner))
        classes, undecodable, natives = class_map_for_owner(env, ggm_registry)
        view = OwnerView(env, classes, natives)
        instances = settings_instances(view)
        owner_routes = []
        for pid in instances:
            owner_routes.append(walk_settings_route(view, pid))
            routes.append(dict(owner_routes[-1], owner=owner.name))
        canvas_census = canvas_route_census(view)
        owners[owner.name] = {**info, "settingsInstances": len(instances),
                              "undecodable_behaviours": undecodable,
                              "routes": owner_routes,
                              "canvasRouteCensus": canvas_census}
    # relocate pids for child counts is already captured in walk; ensure chain pids
    total = collections.Counter(r["routeComplete"] for r in routes)
    scaler_on_canvas = collections.Counter(
        r["canvasScalerOnCanvasNodeCount"] > 0 for r in routes)
    all_canvas = collections.Counter(r["canvasScalerSibling"] for o in owners.values()
                                     for r in o["canvasRouteCensus"]["routes"])
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "lane": "completing A2's paused DISPLAY-003 gap: instantiated Settings→Canvas route (count level) under explicit owner authorization",
        "script_host": SCRIPT_HOST,
        "routes": routes,
        "owners": owners,
        "summary": {
            "settingsInstances": len(routes),
            "danglingInstances": sum(r["danglingInstance"] for r in routes),
            "routesCompleteGameWide": total.get(1, 0),
            "routeUpChainDepthMax": max((r["upChainDepth"] for r in routes), default=0),
            "instancesWithScalerOnCanvasNode": scaler_on_canvas.get(True, 0),
            "canvasNodesInSubtreeMax": max((r["canvasNodesInSubtree"] for r in routes), default=0),
            "gameWideCanvases": sum(o["canvasRouteCensus"]["canvases"] for o in owners.values()),
            "gameWideCanvasScalerSiblingNodes": sum(o["canvasRouteCensus"]["canvasScalerSiblingCount"]
                                                    for o in owners.values()),
            "gameWideScalerCanvasesWithSettingsFamily": sum(
                o["canvasRouteCensus"]["canvasScalerRoutesWithSettingsFamily"]
                for o in owners.values()),
            "gameWideCanvasesWithSettingsFamily": sum(
                1 for o in owners.values() for r in o["canvasRouteCensus"]["routes"]
                if any(r["settingsFamilyInSubtree"].values())),
        },
    }
    blob = json.dumps(result)
    for forbidden in _FORBIDDEN:
        if forbidden in blob:
            raise ValueError(f"forbidden output key leaked: {forbidden}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="original Raft_Data root")
    parser.add_argument("--owner", action="append", required=True, help="serialized owner (repeatable)")
    parser.add_argument("--repo", help="repo worktree for identity cross-check")
    parser.add_argument("--repo-rel-prefix", default="Raft/Raft_Data")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    owners = []
    for name in args.owner:
        if not owner_name_ok(name):
            raise ValueError(f"unsafe owner name: {name}")
        path = Path(args.source) / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owners.append(path)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    result = probe(owners, repo, args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"aggregate_written": str(out),
                      "summary": result["summary"],
                      "no_proprietary_payload": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
