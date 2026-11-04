"""Prove engine-owned Shader PPtrs directly, without a summary receipt.

Re-read original bytes, the pinned private engine table, same-instance collection
trace, actual Material YAML, and .meta reachability. Water programs remain a
separate contract. Nothing is written into the Unity project.
"""
import json
from pathlib import Path

from scripts.verify_export_lineage import source_graph, actual_graph, font_importers, check
from scripts.w1_verify_engine_export import exact_table, original_keys, original_binding_map, verify_histogram
from scripts.w1_audit_export_material_shaders import inventory


def verify(project, source, trace, database, reader):
    graph = inventory(Path(project))
    if not graph['reference_inventory_complete']:
        raise ValueError('Actual initial export references are incomplete')
    table = exact_table(json.loads(Path(database).read_text()), json.loads(Path(reader).read_text()))
    keys = original_keys(Path(source))
    engine, custom = original_binding_map(keys, table)
    if len(engine) != 25 or len(custom) != 140:
        raise ValueError('Original game Shader classification changed')
    edges, shaders, fonts = source_graph(Path(source), include_fonts=True)
    linkage = check(json.loads(Path(trace).read_text()), edges, shaders, actual_graph(Path(project)), font_importers(Path(project)), fonts)
    coverage = verify_histogram(graph, engine)
    if coverage['source_mapped_internal_references'] <= 0:
        raise ValueError('No authenticated engine Shader references in actual export')
    return {**linkage, **coverage, 'engine_owned_shader_references_verified': True,
            'custom_water_programs_verified': False, 'changes_to_project': 0}
