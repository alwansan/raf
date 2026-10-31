"""Exact original serialized owners; exclude streams and dependencies."""
import re

SOURCE = re.compile(r'(?:(?:sharedassets\d+|resources)\.assets|level\d+|globalgamemanagers(?:\.assets)?)')


def serialized_sources(root):
    return sorted(path for path in root.iterdir() if path.is_file() and SOURCE.fullmatch(path.name))


def owned_objects(environment):
    return list(environment.file.objects.values())
