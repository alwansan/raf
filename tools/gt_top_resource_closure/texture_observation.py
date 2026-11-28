"""Scoped original texture observations; no asset writes or GPU acceptance."""
import re
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts import t3_normalmap_dxt5_semantic as normal
from scripts.gt_validate_texture2darray_flipbook import png_dimensions

def semantic_observation(tree, before, after, raw):
    fmt, space, usage = (tree.get(k) for k in ("m_TextureFormat", "m_ColorSpace", "m_LightmapFormat"))
    result = {"source_format": fmt if type(fmt) is int and 0 < fmt <= 255 else None,
              "source_color_space": space if type(space) is int and space in (0,1) else None,
              "source_usage": usage if type(usage) is int and 0 <= usage <= 11 else None,
              "raw_RGBA_match": raw["rgba8_samples_equal"],
              "source_declared_transform_tested": False,
              "source_declared_transform_match": False}
    if raw["rgba8_samples_equal"]:
        result["status"] = "RAW_MATCH"
        return result
    # Only the source-declared mode and supported codec/color space may
    # authorize this known pinned AssetRipper transformation, never a fit.
    if (fmt, space, usage) != (normal.DXT5, 0, normal.NORMALMAP_DXT5NM):
        result["status"] = "RAW_MISMATCH_TRANSFORM_NOT_ADMITTED"
        return result
    expected = normal.semantic_rgba_input(before.convert("RGBA"), format_code=fmt,
                                          color_space=space, lightmap_format=usage)
    observation = pixels.compare_pixels(expected, after)
    result.update(source_declared_transform_tested=True,
                  source_declared_transform_match=observation["rgba8_samples_equal"],
                  transformed_rgb_mismatch_pixels=observation["rgb_mismatch_pixels"],
                  transformed_alpha_mismatch_pixels=observation["alpha_mismatch_pixels"],
                  status="SOURCE_DECLARED_UNPACK_MATCH" if observation["rgba8_samples_equal"]
                  else "SOURCE_DECLARED_UNPACK_MISMATCH")
    return result

def array_source(tree):
    result = {}
    for key in ("m_Width","m_Height","m_Depth","m_MipCount"):
        value = tree.get(key)
        if type(value) is not int or not 0 < value <= 65536:
            raise ValueError("invalid_selected_array_geometry")
        result[key[2:].lower()] = value
    fmt = tree.get("m_Format", tree.get("m_TextureFormat"))
    result["format_enum"] = fmt if type(fmt) is int and 0 <= fmt <= 65535 else None
    stream = tree.get("m_StreamData")
    size = stream.get("size") if isinstance(stream, dict) else None
    result["stream_bytes"] = size if type(size) is int and 0 <= size <= 2**40 else None
    inline = tree.get("m_ImageData", tree.get("image data"))
    result["inline_data_bytes"] = len(inline) if isinstance(inline,(bytes,bytearray,list,tuple)) else None
    result["explicit_empty_stream_and_inline"] = result["stream_bytes"] == 0 and result["inline_data_bytes"] == 0
    result["payload_presence_unknown"] = result["stream_bytes"] is None or result["inline_data_bytes"] is None
    return result

def array_png_observation(source, path, meta, fid, kind):
    if fid != 18700000 or kind not in (2,3):
        raise ValueError("selected_array_wrong_importer_fileID")
    if len(re.findall(r"(?m)^TextureImporter:[ \t]*$", meta)) != 1:
        raise ValueError("selected_array_TextureImporter_missing")
    fields = {}
    for name in ("textureShape", "flipbookRows", "flipbookColumns"):
        hits = re.findall(r"(?m)^[ \t]*" + name + r":[ \t]*(\d+)[ \t]*$", meta)
        fields[name] = int(hits[0]) if len(hits) == 1 else None
    w,h = png_dimensions(path)
    sw,sh,depth = source["width"],source["height"],source["depth"]
    aligned = w % sw == 0 and h % sh == 0
    columns,rows = (w//sw,h//sh) if aligned else (None,None)
    all_cells = aligned and columns*rows == depth
    grid = bool(all_cells and fields["textureShape"] == 4
                and fields["flipbookColumns"] == columns and fields["flipbookRows"] == rows)
    return {"status": "ARRAY_GRID_MATCH_PIXELS_UNPROVEN" if grid else "ARRAY_GRID_INCOMPLETE",
            "textureShape": fields["textureShape"], "flipbookRows": fields["flipbookRows"],
            "flipbookColumns": fields["flipbookColumns"], "png_width":w, "png_height":h,
            "all_source_sized_cells_present": bool(all_cells), "importer_grid_matches":grid,
            "layer_pixel_values_verified": False}
