/*
 * T2: private original Foam DXBC -> SPIR-V with two deliberately distinct,
 * source-register-indexed vkd3d explicit image/sampler binding interfaces.
 * Only public compiler return codes; no shader code/strings/paths printed.
 * Compiled bytes and input live exclusively under CI runner temp; never publish.
 * Reuse B18 vkd3d C ABI/API concept without changing B18's files.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <vkd3d_shader.h>

#define MAX_DXBC_BYTES (16u * 1024u * 1024u)
#define MAX_SPV_BYTES (2u * 1024u * 1024u)
#define MAX_SOURCE_TEXTURES 5u
#define MAX_SOURCE_CBS 3u
#define MAX_BINDINGS (2 * MAX_SOURCE_TEXTURES + MAX_SOURCE_CBS)

static int read_binary(const char *path, void **data, size_t *size)
{
    FILE *f = fopen(path, "rb");
    long n;
    void *mem;
    if (!f) return 1;
    if (fseek(f, 0, SEEK_END) || (n = ftell(f)) < 36
        || n > MAX_DXBC_BYTES || fseek(f, 0, SEEK_SET))
    {
        fclose(f);
        return 2;
    }
    mem = malloc((size_t)n);
    if (!mem)
    {
        fclose(f);
        return 3;
    }
    if (fread(mem, 1, (size_t)n, f) != (size_t)n)
    {
        free(mem);
        fclose(f);
        return 4;
    }
    fclose(f);
    *data = mem;
    *size = (size_t)n;
    return 0;
}

static void map_binding(struct vkd3d_shader_resource_binding *record,
        enum vkd3d_shader_descriptor_type kind, unsigned int slot,
        unsigned int set, unsigned int binding)
{
    memset(record, 0, sizeof(*record));
    record->type = kind;
    record->register_space = 0;
    record->register_index = slot;
    record->shader_visibility = VKD3D_SHADER_VISIBILITY_PIXEL;
    record->flags = (kind == VKD3D_SHADER_DESCRIPTOR_TYPE_CBV)
        ? VKD3D_SHADER_BINDING_FLAG_BUFFER :
          VKD3D_SHADER_BINDING_FLAG_IMAGE;
    record->binding.set = set;
    record->binding.binding = binding;
    record->binding.count = 1;
}

int main(int argc, char **argv)
{
    struct vkd3d_shader_resource_binding bindings[MAX_BINDINGS];
    struct vkd3d_shader_interface_info iface = {0};
    struct vkd3d_shader_compile_info info = {0};
    struct vkd3d_shader_code spv = {0};
    void *source = NULL;
    size_t size = 0;
    unsigned int count, cb_count, set, i, length = 0;
    FILE *out;
    int rc, result;
    char *end;
    if (argc != 6 || strlen(argv[3]) != 1
        || (argv[3][0] != 'A' && argv[3][0] != 'B' && argv[3][0] != 'D'))
        return 2;
    count = (unsigned int)strtoul(argv[4], &end, 10);
    if (*end || count > MAX_SOURCE_TEXTURES) return 3;
    cb_count = (unsigned int)strtoul(argv[5], &end, 10);
    if (*end || cb_count > MAX_SOURCE_CBS) return 4;
    if ((result = read_binary(argv[1], &source, &size))) return 10 + result;
    if (argv[3][0] != 'D')
    {
        set = argv[3][0] == 'A' ? 3 : 4;
        for (i = 0; i < count; ++i)
        {
            map_binding(&bindings[length++], VKD3D_SHADER_DESCRIPTOR_TYPE_SRV,
                    i, set, argv[3][0] == 'A' ? 11 + 4*i : 22 + 4*i);
            map_binding(&bindings[length++], VKD3D_SHADER_DESCRIPTOR_TYPE_SAMPLER,
                    i, set, argv[3][0] == 'A' ? 41 + 4*i : 52 + 4*i);
        }
        for (i = 0; i < cb_count; ++i)
            map_binding(&bindings[length++], VKD3D_SHADER_DESCRIPTOR_TYPE_CBV,
                    i, 0, i);
        iface.type = VKD3D_SHADER_STRUCTURE_TYPE_INTERFACE_INFO;
        iface.next = NULL;
        iface.bindings = bindings;
        iface.binding_count = length;
    }
    info.type = VKD3D_SHADER_STRUCTURE_TYPE_COMPILE_INFO;
    info.next = argv[3][0] == 'D' ? NULL : &iface;
    info.source.code = source;
    info.source.size = size;
    info.source_type = VKD3D_SHADER_SOURCE_DXBC_TPF;
    info.target_type = VKD3D_SHADER_TARGET_SPIRV_BINARY;
    info.options = NULL;
    info.option_count = 0;
    info.source_name = NULL;
    rc = vkd3d_shader_compile(&info, &spv, NULL);
    free(source);
    if (rc != 0 || !spv.code || spv.size < 20 || spv.size > MAX_SPV_BYTES)
    {
        if (spv.code) vkd3d_shader_free_shader_code(&spv);
        return rc < 0 ? 40 + ((-rc) > 50 ? 50 : -rc) : 5;
    }
    out = fopen(argv[2], "wb");
    if (!out)
    {
        vkd3d_shader_free_shader_code(&spv);
        return 6;
    }
    result = fwrite(spv.code, 1, spv.size, out) == spv.size ? 0 : 7;
    if (fclose(out) != 0) result = 8;
    vkd3d_shader_free_shader_code(&spv);
    return result;
}
