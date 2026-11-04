"""Add a read-only same-instance pointer trace to the exact pinned exporter.

Only the disposable public tool checkout is patched. Original game inputs and
exported assets are untouched. The trace is private and must never be uploaded.
"""
import argparse
import hashlib
from pathlib import Path

PIN = '3f2400364e25332361f53737446ee69a534ca1e8fc9bae072d580fac1c617ed6'
ANCHOR = '\t\tProjectAssetContainer container = new ProjectAssetContainer(this, options, fileCollection.FetchAssets(), collections);'


def patch(root, helper):
    directory = root / 'Source/AssetRipper.Export.UnityProjects'
    target = directory / 'ProjectExporter.cs'
    raw = target.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Pinned exporter source changed; refusing instrumentation')
    source = raw.decode('utf-8')
    if source.count(ANCHOR) != 1:
        raise ValueError('Exporter container hook is ambiguous')
    destination = directory / 'RaftExportLineage.cs'
    if destination.exists():
        raise FileExistsError('Trace source already exists')
    destination.write_bytes(helper.read_bytes())
    try:
        target.write_bytes(source.replace(ANCHOR, ANCHOR + '\n\t\tRaftExportLineage.Capture(container, collections);').encode('utf-8'))
    except BaseException:
        target.write_bytes(raw)
        destination.unlink()
        raise


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-source', type=Path, required=True)
    p.add_argument('--helper', type=Path, required=True)
    a = p.parse_args()
    patch(a.tool_source, a.helper)
