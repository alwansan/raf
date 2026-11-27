"""Strict modern native GLTextureSettings, independent of importer/GPU."""
from dataclasses import dataclass

from scripts.b15_texture_sampler_parity import FIELDS, original_sampler
from scripts.b22_verify_material_scalars import _float_bits


NAMES=tuple(k for k,_ in FIELDS)


class Unproven(ValueError):
    pass


class Mismatch(ValueError):
    pass


@dataclass(frozen=True)
class Proof:
    values: tuple


def need(ok,reason):
    if not ok:
        raise Unproven(reason)


def proof(tree, *, exported=False):
    settings=tree.get("m_TextureSettings") if type(tree) is dict else None
    need(type(settings) is dict,"missing_native_texture_sampler")
    need(set(NAMES)<=set(settings),"missing_native_texture_sampler_field")
    # Modern three-axis schema only. No single WrapMode alias or importer
    # defaults. The generated native YAML writes serializedVersion: 2.
    extra=set(settings)-set(NAMES)
    need(not extra or (exported and extra=={"serializedVersion"} and
         type(settings["serializedVersion"]) is int and settings["serializedVersion"]==2),
         "unsupported_native_texture_sampler_schema")
    try:
        values=original_sampler(tree)
        bias=_float_bits(settings["m_MipBias"])
    except (ValueError,OverflowError,TypeError):
        raise Unproven("invalid_native_texture_sampler_value") from None
    # B15's broader range is narrowed for native FilterMode: Point/Bilinear/
    # Trilinear. -100 is not a proved native value; no unset equivalence.
    need(0<=values[0]<=2 and values[2]!=-100.0,
         "invalid_native_texture_sampler_value")
    return Proof((values[0],values[1],bias,*values[3:]))


def safe_proof(tree, *, exported=False):
    try:
        return proof(tree,exported=exported)
    except Unproven as exc:
        return str(exc)


def compare(source,actual):
    need(isinstance(source,Proof),source if type(source) is str else "missing_source_texture_sampler_proof")
    need(isinstance(actual,Proof),actual if type(actual) is str else "missing_export_texture_sampler_proof")
    for name,before,after in zip(NAMES,source.values,actual.values,strict=True):
        if before!=after:
            raise Mismatch("same_route_texture_sampler_"+name.removeprefix("m_")+"_drift")
    return len(NAMES)
