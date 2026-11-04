/*
 * B18 source-free vkd3d-shader explicit resource register remapper.
 *
 * Input DXBC and output SPIR-V live only in $RUNNER_TEMP. No source,
 * shaders, decompiled names or private bytes are printed/published.
 * This verifies source t0/t1/u0 -> *chosen* descriptor mapping, not Unity
 * runtime FindKernel lookup nor Android import/driver execution.
 */
#include <stddef.h>
#include <vkd3d_shader.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MAX_DXBC_BYTES (16u * 1024u * 1024u)
#define MAX_SPV_BYTES (1u * 1024u * 1024u)

static int read_private(const char *path, void **ptr, size_t *bytes)
{
    FILE *file = fopen(path, "rb");
    long size;
    void *data;
    if (!file) return 1;
    if (fseek(file, 0, SEEK_END) || (size = ftell(file)) < 36
        || size > MAX_DXBC_BYTES || fseek(file, 0, SEEK_SET))
    {
        fclose(file);
        return 2;
    }
    data = malloc((size_t)size);
    if (!data)
    {
        fclose(file);
        return 3;
    }
    if (fread(data, 1, (size_t)size, file) != (size_t)size)
    {
        free(data);
        fclose(file);
        return 4;
    }
    fclose(file);
    *ptr = data;
    *bytes = (size_t)size;
    return 0;
}

static void map_binding(struct vkd3d_shader_resource_binding *record,
        enum vkd3d_shader_descriptor_type kind, unsigned int source,
        unsigned int set, unsigned int binding)
{
    memset(record, 0, sizeof(*record));
    record->type = kind;
    record->register_space = 0;
    record->register_index = source;
    record->shader_visibility = VKD3D_SHADER_VISIBILITY_COMPUTE;
    /* Without IMAGE the compiler cannot resolve typed Texture2D SRV/UAV. */
    record->flags = VKD3D_SHADER_BINDING_FLAG_IMAGE;
    record->binding.set = set;
    record->binding.binding = binding;
    record->binding.count = 1;
}

int main(int argc, char **argv)
{
    struct vkd3d_shader_resource_binding mapped[3];
    struct vkd3d_shader_interface_info interface = {0};
    struct vkd3d_shader_compile_info info = {0};
    struct vkd3d_shader_code spv = {0};
    void *input = NULL;
    size_t bytes = 0;
    unsigned int set, a, b, c;
    FILE *output;
    int rc;
    if (argc != 4 || (strcmp(argv[3], "A") && strcmp(argv[3], "B") && strcmp(argv[3], "D")))
        return 2;
    if (!strcmp(argv[3], "A"))
    {
        set = 3;
        a = 11;
        b = 17;
        c = 23;
    }
    else
    {
        set = 4;
        a = 29;
        b = 13;
        c = 31;
    }
    if (read_private(argv[1], &input, &bytes))
        return 3;
    map_binding(&mapped[0], VKD3D_SHADER_DESCRIPTOR_TYPE_SRV, 0, set, a);
    map_binding(&mapped[1], VKD3D_SHADER_DESCRIPTOR_TYPE_SRV, 1, set, b);
    map_binding(&mapped[2], VKD3D_SHADER_DESCRIPTOR_TYPE_UAV, 0, set, c);
    interface.type = VKD3D_SHADER_STRUCTURE_TYPE_INTERFACE_INFO;
    interface.next = NULL;
    interface.bindings = mapped;
    interface.binding_count = 3;
    info.type = VKD3D_SHADER_STRUCTURE_TYPE_COMPILE_INFO;
    /* D is a private baseline control with no explicit mapping. */
    info.next = strcmp(argv[3], "D") ? &interface : NULL;
    info.source.code = input;
    info.source.size = bytes;
    info.source_type = VKD3D_SHADER_SOURCE_DXBC_TPF;
    info.target_type = VKD3D_SHADER_TARGET_SPIRV_BINARY;
    info.options = NULL;
    info.option_count = 0;
    info.source_name = NULL;
    /* Passing NULL suppresses diagnostic text containing private identifiers. */
    rc = vkd3d_shader_compile(&info, &spv, NULL);
    free(input);
    if (rc != 0 || !spv.code || spv.size < 20 || spv.size > MAX_SPV_BYTES)
    {
        if (spv.code) vkd3d_shader_free_shader_code(&spv);
        /* Public numeric vkd3d return code ONLY; no private diagnostic text. */
        return rc < 0 ? (unsigned int)(40 + ((-rc) > 50 ? 50 : -rc)) : 4;
    }
    output = fopen(argv[2], "wb");
    if (!output)
    {
        vkd3d_shader_free_shader_code(&spv);
        return 5;
    }
    {
        size_t written = fwrite(spv.code, 1, spv.size, output);
        int closed = fclose(output);
        rc = written == spv.size && closed == 0 ? 0 : 6;
    }
    vkd3d_shader_free_shader_code(&spv);
    return rc;
}
