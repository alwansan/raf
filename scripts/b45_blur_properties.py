"""Restore precisely one SHA-pinned Blur texture property from serialized ShaderLab.

Narrow Unity 2021.3 / AssetRipper property model; original property names and
values remain private in temporary CI memory and are never logged or committed.
Any unhandled schema/flags/attributes fail closed, not a guessed default.
Reference: AssetRipper DummyShaderTextExporter and Unity ShaderProperties.
"""
import math
import re

from scripts.w1_depth_shaderlab import quoted

TEXTURE_DIMENSIONS = {1: "any", 2: "2D", 3: "3D", 4: "Cube", 5: "2DArray", 6: "CubeArray"}
# ShaderLab's standard default-texture identities; preserve the original string.
DEFAULT_TEXTURE_NAMES = {"", "white", "black", "gray", "grey", "bump",
                         "red", "linearGrey"}
PROPERTY_FIELDS = {"m_Name", "m_Description", "m_Attributes", "m_Type", "m_Flags",
                   "m_DefValue[0]", "m_DefValue[1]", "m_DefValue[2]",
                   "m_DefValue[3]", "m_DefTexture"}


def serialize_properties(parsed):
    """Emit exactly the original one-texture Blur property, or reject.

    This is intentionally narrower than an arbitrary ShaderLab deserializer.
    The SHA-pinned caller authenticates the original Shader object/parsed form.
    """
    if not isinstance(parsed, dict) or not isinstance(parsed.get("m_PropInfo"), dict):
        raise ValueError("Original shader property table missing")
    props = parsed["m_PropInfo"].get("m_Props")
    if not isinstance(props, list) or len(props) != 1:
        raise ValueError("Original Blur must have one serialized texture property")
    prop = props[0]
    if not isinstance(prop, dict) or set(prop) != PROPERTY_FIELDS:
        raise ValueError("Unrecognized original texture property fields")
    if type(prop["m_Type"]) is not int or prop["m_Type"] != 4:
        raise ValueError("Original Blur property not an authenticated texture")
    if type(prop["m_Flags"]) is not int or prop["m_Flags"] != 0:
        raise ValueError("Unsupported original shader property flags")
    if prop["m_Attributes"] != []:
        raise ValueError("Unsupported original texture property attributes")
    for index in range(4):
        value = prop[f"m_DefValue[{index}]"]
        if type(value) not in (float, int) or not math.isfinite(value) or value != 0:
            raise ValueError("Unexplained original texture numeric default")
    name, description = prop["m_Name"], prop["m_Description"]
    if not isinstance(name, str) or not re.fullmatch(r"[_A-Za-z][_A-Za-z0-9]{0,127}", name):
        raise ValueError("Unparseable original shader property identity")
    if not isinstance(description, str) or len(description) > 1024:
        raise ValueError("Unbounded original shader property label")
    # Serialized texture dimensions/defaults are separate from numeric defaults.
    tex = prop["m_DefTexture"]
    if not isinstance(tex, dict) or set(tex) != {"m_DefaultName", "m_TexDim"}:
        raise ValueError("Original texture default schema changed")
    dimension = tex["m_TexDim"]
    default = tex["m_DefaultName"]
    if type(dimension) is not int or dimension not in TEXTURE_DIMENSIONS:
        raise ValueError("Original texture dimension unsupported")
    if not isinstance(default, str) or default not in DEFAULT_TEXTURE_NAMES:
        raise ValueError("Original texture default requires exact recovery")
    return ("Properties {\n"
            + name + " (" + quoted(description) + ", " + TEXTURE_DIMENSIONS[dimension]
            + ") = " + quoted(default) + " {}\n"
            + "}")
