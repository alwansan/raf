/*
 * T3 VS/FS explicit VKD3D 1.2 resource contract compiler.
 *
 * The map file MUST be produced from the private, SHA-authenticated original
 * DXBC SHDR/SHEX DCL layout in a runner-private directory; never commit,
 * print or upload source register indices or mapped descriptor coordinates.
 *
 * The distinct explicit descriptor profiles are OUR test destinations,
 * NOT original Raft Vulkan bindings or Unity import validation. Success
 * means vkd3d accepted a compilation request, not that it honored it.
 * A separate, strict SPIR-V descriptor + whole-module parity check is
 * mandatory before claiming any mapping/provenance evidence.
 */
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vkd3d_shader.h>

#define T3_MAX_ROWS 64u
#define T3_MAX_DXBC (16u*1024u*1024u)
#define T3_MAX_SPV (8u*1024u*1024u)

struct t3_map
{
    struct vkd3d_shader_resource_binding rows[T3_MAX_ROWS];
    unsigned int count;
    char stage;
    char profile;
};

static int digits_unsigned(const char *s, unsigned int *out)
{
    unsigned long n;
    const unsigned char *p = (const unsigned char *)s;
    char *end = NULL;
    if (!*p) return 1;
    while (*p)
    {
        if (!isdigit(*p++)) return 1;
    }
    errno = 0;
    n = strtoul(s, &end, 10);
    if (errno || end == s || *end || n > UINT_MAX) return 1;
    *out = (unsigned int)n;
    return 0;
}

static int parse_map_line(const char *line, struct t3_map *m, unsigned int i)
{
    char kind, reg_text[24], set_text[24], binding_text[24], extra[2];
    unsigned int source, set, binding, j;
    struct vkd3d_shader_resource_binding *r;
    int tokens = sscanf(line, " %c %23s %23s %23s %1s",
            &kind, reg_text, set_text, binding_text, extra);
    if (tokens != 4 || digits_unsigned(reg_text, &source)
            || digits_unsigned(set_text, &set)
            || digits_unsigned(binding_text, &binding)
            || source > 4095u || set > 64u || binding > 4095u)
        return 1;
    r = &m->rows[i];
    memset(r, 0, sizeof(*r));
    switch (kind)
    {
        case 'C':
            r->type = VKD3D_SHADER_DESCRIPTOR_TYPE_CBV;
            /* A CBV is a buffer descriptor. Zero flags make the explicit
             * register invisible to VKD3D's descriptor-binding matcher. */
            r->flags = VKD3D_SHADER_BINDING_FLAG_BUFFER;
            break;
        case 'T':
            r->type = VKD3D_SHADER_DESCRIPTOR_TYPE_SRV;
            r->flags = VKD3D_SHADER_BINDING_FLAG_IMAGE;
            break;
        case 'S':
            r->type = VKD3D_SHADER_DESCRIPTOR_TYPE_SAMPLER;
            /* vkd3d-shader 1.2 applies IMAGE flag to sampler descriptor
             * selection too (RESOURCE_NONE falls into non-BUFFER branch). */
            r->flags = VKD3D_SHADER_BINDING_FLAG_IMAGE;
            break;
        case 'U':
            r->type = VKD3D_SHADER_DESCRIPTOR_TYPE_UAV;
            r->flags = VKD3D_SHADER_BINDING_FLAG_IMAGE;
            break;
        default: return 1;
    }
    r->register_space = 0;
    r->register_index = source;
    r->shader_visibility = m->stage == 'V' ?
        VKD3D_SHADER_VISIBILITY_VERTEX : VKD3D_SHADER_VISIBILITY_PIXEL;
    r->binding.set = set;
    r->binding.binding = binding;
    r->binding.count = 1;
    for (j = 0; j < i; ++j)
    {
        const struct vkd3d_shader_resource_binding *old = &m->rows[j];
        if ((old->type == r->type && old->register_index == source)
                || (old->binding.set == set && old->binding.binding == binding))
            return 1;
    }
    return 0;
}

static int load_private_map(const char *path, const char *expected, struct t3_map *m)
{
    FILE *fp;
    char line[256], magic[16], stage[4], profile[4], count_text[24], extra[2];
    unsigned int count, i;
    int rc = 1;
    if (!expected || strlen(expected) != 1 || (*expected != 'A' && *expected != 'B'))
        return 1;
    fp = fopen(path, "rb");
    if (!fp) return 1;
    if (!fgets(line, sizeof(line), fp)
            || !strchr(line, '\n')
            || sscanf(line, " %15s %3s %3s %23s %1s",
                    magic, stage, profile, count_text, extra) != 4
            || strcmp(magic, "T3MAP1")
            || strlen(stage) != 1 || (stage[0] != 'V' && stage[0] != 'P')
            || strcmp(profile, expected)
            || digits_unsigned(count_text, &count)
            || !count || count > T3_MAX_ROWS)
        goto done;
    memset(m, 0, sizeof(*m));
    m->count = count;
    m->stage = stage[0];
    m->profile = profile[0];
    for (i = 0; i < count; ++i)
    {
        if (!fgets(line, sizeof(line), fp) || !strchr(line, '\n')
                || parse_map_line(line, m, i))
            goto done;
    }
    if (fgetc(fp) != EOF) goto done;
    rc = 0;
done:
    fclose(fp);
    return rc;
}

static int read_dxbc(const char *path, struct vkd3d_shader_code *source)
{
    FILE *fp;
    long n;
    void *mem;
    fp = fopen(path, "rb");
    if (!fp) return 1;
    if (fseek(fp, 0, SEEK_END) || (n = ftell(fp)) < 36
            || n > T3_MAX_DXBC || fseek(fp, 0, SEEK_SET))
    {
        fclose(fp);
        return 1;
    }
    mem = malloc((size_t)n);
    if (!mem)
    {
        fclose(fp);
        return 1;
    }
    if (fread(mem, 1, (size_t)n, fp) != (size_t)n)
    {
        free(mem);
        fclose(fp);
        return 1;
    }
    fclose(fp);
    source->code = mem;
    source->size = (size_t)n;
    return 0;
}

/* Classify compiler diagnostics IN-MEMORY only: never print vkd3d's raw
 * message because it can include private source registers and resource IDs.
 * Return fixed public enum-family codes, no positions or values. */
static int classify_private_error_message(const char *msg)
{
    const char *p;
    unsigned int kind = UINT_MAX;
    if (!msg) return 0;
    p = strstr(msg, "Could not find descriptor binding for type ");
    if (!p)
        p = strstr(msg, "Could not find binding for type ");
    if (p)
    {
        const char *after = strstr(p, "type ");
        if (after && sscanf(after, "type %x", &kind) == 1)
        {
            switch (kind)
            {
                case VKD3D_SHADER_DESCRIPTOR_TYPE_SRV: return 101;
                case VKD3D_SHADER_DESCRIPTOR_TYPE_UAV: return 102;
                case VKD3D_SHADER_DESCRIPTOR_TYPE_CBV: return 103;
                case VKD3D_SHADER_DESCRIPTOR_TYPE_SAMPLER: return 104;
                default: return 105;
            }
        }
        return 105;
    }
    if (strstr(msg, "descriptor binding") || strstr(msg, "Descriptor binding"))
        return 106;
    return 0;
}

int main(int argc, char **argv)
{
    struct t3_map mapping;
    struct vkd3d_shader_interface_info interface = {0};
    struct vkd3d_shader_compile_info info = {0};
    struct vkd3d_shader_code source = {0}, spv = {0};
    char *private_messages = NULL;
    int classified = 0;
    FILE *output;
    size_t written;
    int rc;
    /* Private source-only control: same C ABI and DXBC, but no interface
     * map. A compiler success here and failure under A/B isolates mapping
     * semantics; neither success implies source shader renders in Unity. */
    int baseline = argc == 4 && !strcmp(argv[3], "D");
    if (argc == 2 && !strcmp(argv[1], "--self-test-error-classification"))
    {
        char fixture[192];
        snprintf(fixture, sizeof(fixture),
            "E0000: Could not find descriptor binding for type %#x, "
            "space 0, registers [99:99].",
            (unsigned int)VKD3D_SHADER_DESCRIPTOR_TYPE_CBV);
        if (classify_private_error_message(fixture) != 103 ||
            classify_private_error_message("not a vkd3d message") != 0)
            return 2;
        puts("T3_PUBLIC_SYNTHETIC_DIAGNOSTIC_CLASSIFIER_OK=true");
        return 0;
    }
    if (argc == 2 && !strcmp(argv[1], "--self-test-type-flags"))
    {
        static const char *test_rows[] = {
            "C 2 4 37", "T 3 4 38", "S 1 4 39", "U 0 4 40"
        };
        static const unsigned int expected[] = {
            VKD3D_SHADER_BINDING_FLAG_BUFFER,
            VKD3D_SHADER_BINDING_FLAG_IMAGE,
            VKD3D_SHADER_BINDING_FLAG_IMAGE,
            VKD3D_SHADER_BINDING_FLAG_IMAGE
        };
        unsigned int i;
        memset(&mapping, 0, sizeof(mapping));
        mapping.stage = 'V';
        mapping.count = 4;
        for (i = 0; i < 4; ++i)
        {
            if (parse_map_line(test_rows[i], &mapping, i) ||
                    mapping.rows[i].flags != expected[i])
                return 2;
        }
        puts("T3_VKD3D_PUBLIC_DESCRIPTOR_TYPE_FLAGS_SYNTHETIC_OK=true");
        return 0;
    }
    if (argc == 4 && !strcmp(argv[1], "--check-map"))
    {
        rc = load_private_map(argv[2], argv[3], &mapping);
        if (!rc) puts("T3_EXPLICIT_MAP_SYNTAX_ACCEPTED_ONLY");
        return rc ? 2 : 0;
    }
    if (!baseline && (argc != 5 || load_private_map(argv[3], argv[4], &mapping)))
        return 2;
    if (read_dxbc(argv[1], &source))
        return 3;
    interface.type = VKD3D_SHADER_STRUCTURE_TYPE_INTERFACE_INFO;
    interface.next = NULL;
    interface.bindings = mapping.rows;
    interface.binding_count = mapping.count;
    info.type = VKD3D_SHADER_STRUCTURE_TYPE_COMPILE_INFO;
    info.next = baseline ? NULL : &interface;
    info.source = source;
    info.source_type = VKD3D_SHADER_SOURCE_DXBC_TPF;
    info.target_type = VKD3D_SHADER_TARGET_SPIRV_BINARY;
    info.options = NULL;
    info.option_count = 0;
    info.source_name = NULL;
    /* Never pass debug-log output pointer: source names can be private. */
    info.log_level = VKD3D_SHADER_LOG_ERROR;
    rc = vkd3d_shader_compile(&info, &spv, &private_messages);
    /* Never print, persist or upload compiler messages. Identify only
     * broad public descriptor-family failure category from private memory. */
    if (rc != 0)
        classified = classify_private_error_message(private_messages);
    vkd3d_shader_free_messages(private_messages);
    free((void *)source.code);
    if (rc != 0 || !spv.code || spv.size < 20 || spv.size > T3_MAX_SPV)
    {
        if (spv.code) vkd3d_shader_free_shader_code(&spv);
        return classified ? classified : (rc < 0 ? 40 + ((-rc) > 49 ? 49 : -rc) : 4);
    }
    output = fopen(argv[2], "wb");
    if (!output)
    {
        vkd3d_shader_free_shader_code(&spv);
        return 5;
    }
    written = fwrite(spv.code, 1, spv.size, output);
    rc = fclose(output);
    if (written != spv.size || rc)
    {
        vkd3d_shader_free_shader_code(&spv);
        return 6;
    }
    vkd3d_shader_free_shader_code(&spv);
    return 0;
}
