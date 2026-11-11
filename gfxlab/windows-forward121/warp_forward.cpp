#define NOMINMAX
#include <d3d11.h>
#include <wrl/client.h>
#include <array>
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <cstring>
#include <cstdint>

using Microsoft::WRL::ComPtr;
using Path = std::filesystem::path;
using Bytes = std::vector<unsigned char>;
constexpr UINT Side = 256;

void require(HRESULT hr, const char* context) {
    if (FAILED(hr)) throw std::runtime_error(std::string(context) + " HRESULT " + std::to_string(hr));
}

Bytes read(const Path& path) {
    std::ifstream in(path, std::ios::binary | std::ios::ate);
    auto size = in.tellg();
    if (size <= 0 || size > 32 * 1024 * 1024) throw std::runtime_error("Invalid input size");
    Bytes bytes(static_cast<size_t>(size));
    in.seekg(0);
    if (!in.read(reinterpret_cast<char*>(bytes.data()), size)) throw std::runtime_error("Short input");
    return bytes;
}

struct Draw {
    ComPtr<ID3D11Device> device;
    ComPtr<ID3D11DeviceContext> ctx;
    ComPtr<ID3D11Texture2D> target, staging;
    ComPtr<ID3D11RenderTargetView> color;
    ComPtr<ID3D11DepthStencilView> depth;

    UINT index_count = 0;
    ComPtr<ID3D11Texture2D> depth_source, depth_staging;

    Draw(bool shadow=false) {
        D3D_FEATURE_LEVEL actual{};
        D3D_FEATURE_LEVEL requested = D3D_FEATURE_LEVEL_11_0;
        require(D3D11CreateDevice(nullptr,D3D_DRIVER_TYPE_WARP,nullptr,0,&requested,1,
                                  D3D11_SDK_VERSION,&device,&actual,&ctx),"WARP device");
        if (actual != requested) throw std::runtime_error("Unexpected feature level");
        D3D11_TEXTURE2D_DESC desc{};
        desc.Width = desc.Height = Side;
        desc.MipLevels = desc.ArraySize = desc.SampleDesc.Count = 1;
        desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
        desc.BindFlags = D3D11_BIND_RENDER_TARGET;
        require(device->CreateTexture2D(&desc,nullptr,&target),"Color texture");
        require(device->CreateRenderTargetView(target.Get(),nullptr,&color),"Color view");
        desc.BindFlags = 0;
        desc.Usage = D3D11_USAGE_STAGING;
        desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
        require(device->CreateTexture2D(&desc,nullptr,&staging),"Readback texture");

        desc.Usage = D3D11_USAGE_DEFAULT;
        desc.CPUAccessFlags = 0;
        desc.BindFlags = D3D11_BIND_DEPTH_STENCIL;
        desc.Format = shadow ? DXGI_FORMAT_R24G8_TYPELESS : DXGI_FORMAT_D24_UNORM_S8_UINT;
        ComPtr<ID3D11Texture2D> ds;
        require(device->CreateTexture2D(&desc,nullptr,&ds),"Depth texture");
        D3D11_DEPTH_STENCIL_VIEW_DESC view{};
        view.Format=DXGI_FORMAT_D24_UNORM_S8_UINT;
        view.ViewDimension=D3D11_DSV_DIMENSION_TEXTURE2D;
        require(device->CreateDepthStencilView(ds.Get(),shadow ? &view : nullptr,&depth),"Depth view");
        if (shadow) {
            depth_source=ds;
            desc.BindFlags=0;
            desc.Usage=D3D11_USAGE_STAGING;
            desc.CPUAccessFlags=D3D11_CPU_ACCESS_READ;
            require(device->CreateTexture2D(&desc,nullptr,&depth_staging),"Shadow staging texture");
        }
        ID3D11RenderTargetView* rtv = color.Get();
        ctx->OMSetRenderTargets(1,&rtv,depth.Get());

        D3D11_RASTERIZER_DESC raster{};
        raster.FillMode = D3D11_FILL_SOLID;
        raster.CullMode = D3D11_CULL_NONE;
        raster.DepthClipEnable = TRUE;
        ComPtr<ID3D11RasterizerState> state;
        require(device->CreateRasterizerState(&raster,&state),"Raster state");
        ctx->RSSetState(state.Get());
        D3D11_VIEWPORT viewport{0,0,float(Side),float(Side),0,1};
        ctx->RSSetViewports(1,&viewport);
    }

    ComPtr<ID3D11Buffer> buffer(const Bytes& bytes, UINT bind) {
        D3D11_BUFFER_DESC desc{};
        desc.ByteWidth = static_cast<UINT>(bytes.size());
        desc.BindFlags = bind;
        desc.Usage = D3D11_USAGE_IMMUTABLE;
        D3D11_SUBRESOURCE_DATA data{bytes.data(),0,0};
        ComPtr<ID3D11Buffer> result;
        require(device->CreateBuffer(&desc,&data,&result),"Draw buffer");
        return result;
    }

    ComPtr<ID3D11ShaderResourceView> texture2d(const Bytes& data, bool srgb, bool cube, UINT width, UINT height, UINT levels) {
        D3D11_TEXTURE2D_DESC desc{};
        desc.Width = width;
        desc.Height = height;
        desc.MipLevels = levels;
        desc.ArraySize = cube ? 6 : 1;
        desc.Format = srgb ? DXGI_FORMAT_R8G8B8A8_UNORM_SRGB : DXGI_FORMAT_R8G8B8A8_UNORM;
        desc.SampleDesc.Count = 1;
        desc.Usage = D3D11_USAGE_IMMUTABLE;
        desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;
        desc.MiscFlags = cube ? D3D11_RESOURCE_MISC_TEXTURECUBE : 0;
        std::vector<D3D11_SUBRESOURCE_DATA> uploads;
        size_t offset = 0;
        for (UINT face=0; face<desc.ArraySize; ++face) {
            for (UINT mip=0; mip<levels; ++mip) {
                UINT w = std::max(1u, width >> mip), h = std::max(1u, height >> mip);
                size_t next = offset + size_t(w) * h * 4;
                if (next > data.size()) throw std::runtime_error("Wrong texture extent");
                uploads.push_back({data.data()+offset,w*4,0});
                offset=next;
            }
        }
        if (offset != data.size()) throw std::runtime_error("Wrong texture mip chain");
        ComPtr<ID3D11Texture2D> texture;
        require(device->CreateTexture2D(&desc,uploads.data(),&texture),"Material texture");
        ComPtr<ID3D11ShaderResourceView> view;
        require(device->CreateShaderResourceView(texture.Get(),nullptr,&view),"Material view");
        return view;
    }

    ComPtr<ID3D11ShaderResourceView> volume() {
        D3D11_TEXTURE3D_DESC desc{};
        desc.Width = desc.Height = desc.Depth = desc.MipLevels = 1;
        desc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
        desc.Usage = D3D11_USAGE_IMMUTABLE;
        desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;
        const std::array<unsigned char,4> black{0,0,0,255};
        D3D11_SUBRESOURCE_DATA data{black.data(),4,4};
        ComPtr<ID3D11Texture3D> texture;
        require(device->CreateTexture3D(&desc,&data,&texture),"Probe volume");
        ComPtr<ID3D11ShaderResourceView> view;
        require(device->CreateShaderResourceView(texture.Get(),nullptr,&view),"Probe volume view");
        return view;
    }

    void bind_geometry(const Path& dir, const Path& pose = {}, bool shadow=false) {
        auto vs = read(dir/"vertex.dxbc");
        auto ps = read(dir/"fragment.dxbc");
        ComPtr<ID3D11VertexShader> vertex;
        ComPtr<ID3D11PixelShader> pixel;
        require(device->CreateVertexShader(vs.data(),vs.size(),nullptr,&vertex),"Original vertex DXBC");
        require(device->CreatePixelShader(ps.data(),ps.size(),nullptr,&pixel),"Original fragment DXBC");
        ctx->VSSetShader(vertex.Get(),nullptr,0);
        ctx->PSSetShader(pixel.Get(),nullptr,0);
        D3D11_INPUT_ELEMENT_DESC elements[] = {
            {"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0},
            {"NORMAL",0,DXGI_FORMAT_R32G32B32_FLOAT,0,12,D3D11_INPUT_PER_VERTEX_DATA,0},
            {"TEXCOORD",0,DXGI_FORMAT_R32G32_FLOAT,0,40,D3D11_INPUT_PER_VERTEX_DATA,0},
            {"TEXCOORD",1,DXGI_FORMAT_R32G32_FLOAT,1,0,D3D11_INPUT_PER_VERTEX_DATA,0},
            {"TANGENT",0,DXGI_FORMAT_R32G32B32A32_FLOAT,0,24,D3D11_INPUT_PER_VERTEX_DATA,0}
        };
        ComPtr<ID3D11InputLayout> layout;
        require(device->CreateInputLayout(elements,shadow ? 3 : 5,vs.data(),vs.size(),&layout),"Source signature");
        ctx->IASetInputLayout(layout.Get());
        const auto mesh=read(pose.empty() ? dir/"mesh.bin" : pose), indices=read(dir/"indices.bin");
        if (mesh.size()%48 || indices.size()%6) throw std::runtime_error("Wrong mesh shape");
        index_count=static_cast<UINT>(indices.size()/2);
        auto vb=buffer(mesh,D3D11_BIND_VERTEX_BUFFER);
        auto uv1=buffer(Bytes(mesh.size()/48*8,0),D3D11_BIND_VERTEX_BUFFER);
        auto ib=buffer(indices,D3D11_BIND_INDEX_BUFFER);
        ID3D11Buffer* streams[]{vb.Get(),uv1.Get()};
        UINT strides[]{48,8}, offsets[]{0,0};
        ctx->IASetVertexBuffers(0,2,streams,strides,offsets);
        ctx->IASetIndexBuffer(ib.Get(),DXGI_FORMAT_R16_UINT,0);
        ctx->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
    }

    void bind_textures(const Path& dir, const std::string& mode, bool additive=false) {
        Bytes black{0,0,0,255}, cube;
        for (int i=0; i<6; ++i) cube.insert(cube.end(),black.begin(),black.end());
        std::array<ComPtr<ID3D11ShaderResourceView>,7> textures;
        std::array<std::array<UINT,4>,3> layout{{{1024,1024,11,1},{1024,1024,11,1},{1024,1024,11,0}}};
        if (std::filesystem::exists(dir/"textures.bin")) {
            const auto manifest=read(dir/"textures.bin");
            if (manifest.size()!=sizeof(layout)) throw std::runtime_error("Wrong mip metadata size");
            std::memcpy(layout.data(),manifest.data(),manifest.size());
        }
        const std::array<const char*,3> files{"basecolor.rgba","metallic.rgba","normal.rgba"};
        for (size_t i=0; i<layout.size(); ++i) {
            const auto [width,height,levels,srgb]=layout[i];
            if (!width || !height || width>2048 || height>2048 || !levels || levels>12 || srgb>1)
                throw std::runtime_error("Invalid mip metadata");
            if (i==1 && mode=="nonmetal") textures[i]=texture2d(black,srgb!=0,false,1,1,1);
            else if (i==2 && mode=="flat") textures[i]=texture2d(Bytes{255,128,255,128},srgb!=0,false,1,1,1);
            else textures[i]=texture2d(read(dir/files[i]),srgb!=0,false,width,height,levels);
        }
        if (additive) {
            textures[3] = volume();
        } else {
            textures[3] = texture2d(Bytes{255,255,255,255},false,false,1,1,1);
            textures[4] = textures[5] = texture2d(cube,false,true,1,1,1);
            textures[6] = volume();
        }
        std::array<ID3D11ShaderResourceView*,7> views{};
        for (size_t i=0; i<textures.size(); ++i) views[i]=textures[i].Get();
        ctx->PSSetShaderResources(0,static_cast<UINT>(views.size()),views.data());

        std::array<ComPtr<ID3D11SamplerState>,6> samplers;
        std::array<ID3D11SamplerState*,6> handles{};
        for (UINT i=0; i<samplers.size(); ++i) {
            D3D11_SAMPLER_DESC desc{};
            desc.Filter=D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT;
            desc.AddressU=desc.AddressV=desc.AddressW=(additive ? i>=1 && i<=3 : i>=2 && i<=4)
                ? D3D11_TEXTURE_ADDRESS_WRAP : D3D11_TEXTURE_ADDRESS_CLAMP;
            desc.MaxLOD=D3D11_FLOAT32_MAX;
            desc.MaxAnisotropy=1;
            desc.ComparisonFunc=D3D11_COMPARISON_NEVER;
            require(device->CreateSamplerState(&desc,&samplers[i]),"Source sampler");
            handles[i]=samplers[i].Get();
        }
        ctx->PSSetSamplers(0,static_cast<UINT>(handles.size()),handles.data());
    }

    void set_additive_state(bool enabled, bool reject=false) {
        if (!enabled) {
            ctx->OMSetBlendState(nullptr,nullptr,0xffffffff);
            ctx->OMSetDepthStencilState(nullptr,0);
            return;
        }
        D3D11_BLEND_DESC blend{};
        auto& rt = blend.RenderTarget[0];
        rt.BlendEnable = TRUE;
        rt.SrcBlend = rt.DestBlend = D3D11_BLEND_ONE;
        rt.SrcBlendAlpha = D3D11_BLEND_ZERO;
        rt.DestBlendAlpha = D3D11_BLEND_ONE;
        rt.BlendOp = rt.BlendOpAlpha = D3D11_BLEND_OP_ADD;
        rt.RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;
        ComPtr<ID3D11BlendState> blend_state;
        require(device->CreateBlendState(&blend,&blend_state),"Additive blend");
        ctx->OMSetBlendState(blend_state.Get(),nullptr,0xffffffff);
        D3D11_DEPTH_STENCIL_DESC depth_desc{};
        depth_desc.DepthEnable = TRUE;
        depth_desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ZERO;
        depth_desc.DepthFunc = reject ? D3D11_COMPARISON_NEVER : D3D11_COMPARISON_LESS_EQUAL;
        ComPtr<ID3D11DepthStencilState> depth_state;
        require(device->CreateDepthStencilState(&depth_desc,&depth_state),"Additive depth");
        ctx->OMSetDepthStencilState(depth_state.Get(),0);
    }

    void render(const Path& dir, const std::string& mode, bool clear_target, bool additive=false, bool shadow=false) {
        std::string light = mode=="dark" ? "dark" : "light";
        std::array<ComPtr<ID3D11Buffer>,8> constants;
        std::array<ID3D11Buffer*,8> slots{};
        const UINT vs_count = additive || shadow ? 5 : 4;
        const UINT ps_count = shadow ? 1 : 8-vs_count;
        for (UINT i=0; i<vs_count+ps_count; ++i) {
            std::string stage = i<vs_count ? "vertex" : "fragment";
            constants[i]=buffer(read(dir/(stage+"-"+light+"-"+std::to_string(i<vs_count ? i : i-vs_count)+".bin")),
                                D3D11_BIND_CONSTANT_BUFFER);
            slots[i]=constants[i].Get();
        }
        ctx->VSSetConstantBuffers(0,vs_count,slots.data());
        ctx->PSSetConstantBuffers(0,ps_count,slots.data()+vs_count);
        const float clear[]{0,0,0,0};
        if (clear_target) {
            ctx->ClearRenderTargetView(color.Get(),clear);
            ctx->ClearDepthStencilView(depth.Get(),D3D11_CLEAR_DEPTH,1,0);
        }
        ctx->DrawIndexed(index_count,0,0);
    }

    void shadow_case(const Path& draw, const Path& textures, const Path& output, const std::string& mode) {
        Bytes material = mode=="transparent" ? Bytes{255,255,255,0} :
            mode=="solid" ? Bytes{255,255,255,255} : read(textures/"basecolor.rgba");
        const UINT extent=material.size()==4 ? 1 : 1024;
        auto image=texture2d(material,true,false,extent,extent,extent==1 ? 1 : 11);
        auto* resource=image.Get();
        ctx->PSSetShaderResources(0,1,&resource);
        D3D11_SAMPLER_DESC sampler{};
        sampler.Filter=D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT;
        sampler.AddressU=sampler.AddressV=sampler.AddressW=D3D11_TEXTURE_ADDRESS_WRAP;
        sampler.MaxLOD=D3D11_FLOAT32_MAX;
        sampler.MaxAnisotropy=1;
        sampler.ComparisonFunc=D3D11_COMPARISON_NEVER;
        ComPtr<ID3D11SamplerState> sampler_state;
        require(device->CreateSamplerState(&sampler,&sampler_state),"Shadow sampler");
        auto* sampler_handle=sampler_state.Get();
        ctx->PSSetSamplers(0,1,&sampler_handle);
        D3D11_DEPTH_STENCIL_DESC desc{};
        desc.DepthEnable=TRUE;
        desc.DepthFunc=D3D11_COMPARISON_LESS;
        desc.DepthWriteMask=mode=="depth-off" ? D3D11_DEPTH_WRITE_MASK_ZERO : D3D11_DEPTH_WRITE_MASK_ALL;
        ComPtr<ID3D11DepthStencilState> state;
        require(device->CreateDepthStencilState(&desc,&state),"Shadow depth state");
        ctx->OMSetDepthStencilState(state.Get(),0);
        render(draw,"light",true,false,true);
        ctx->OMSetRenderTargets(0,nullptr,nullptr);
        ctx->CopyResource(depth_staging.Get(),depth_source.Get());
        D3D11_MAPPED_SUBRESOURCE pixels{};
        require(ctx->Map(depth_staging.Get(),0,D3D11_MAP_READ,0,&pixels),"Shadow depth readback");
        std::ofstream out(output/(mode+".mask"),std::ios::binary);
        for (UINT y=0; y<Side; ++y) {
            const auto* row=static_cast<const unsigned char*>(pixels.pData)+(Side-1-y)*pixels.RowPitch;
            for (UINT x=0; x<Side; ++x) {
                uint32_t packed;
                std::memcpy(&packed,row+x*4,4);
                out.put((packed & 0x00ffffffu)==0x00ffffffu ? '\0' : static_cast<char>(255));
            }
        }
        ctx->Unmap(depth_staging.Get(),0);
        auto* rtv=color.Get();
        ctx->OMSetRenderTargets(1,&rtv,depth.Get());
        if (!out) throw std::runtime_error("Shadow mask write failed");
    }

    void capture(const Path& output, const std::string& mode) {
        ctx->CopyResource(staging.Get(),target.Get());
        D3D11_MAPPED_SUBRESOURCE pixels{};
        require(ctx->Map(staging.Get(),0,D3D11_MAP_READ,0,&pixels),"Original DXBC readback");
        // Output bottom-up to match the GLES reference byte order.
        std::ofstream out(output/(mode+".rgba"),std::ios::binary);
        for (UINT y=0; y<Side; ++y) {
            auto row=static_cast<const char*>(pixels.pData)+(Side-1-y)*pixels.RowPitch;
            out.write(row,Side*4);
        }
        ctx->Unmap(staging.Get(),0);
        if (!out) throw std::runtime_error("Readback write failed");
    }
};

int wmain(int argc,wchar_t** argv) {
    const std::wstring mode_flag = argc==6 ? argv[5] : L"";
    if (argc!=4 && argc!=5 && mode_flag!=L"add" && mode_flag!=L"animation" && mode_flag!=L"shadow") return 2;
    try {
        Draw draw(mode_flag==L"shadow");
        if (mode_flag==L"shadow") {
            draw.bind_geometry(argv[4],{},true);
            for (const auto& mode:{"native","solid","transparent","depth-off"})
                draw.shadow_case(argv[4],argv[2],argv[3],mode);
            return 0;
        }
        if (mode_flag==L"animation") {
            draw.bind_textures(argv[2],"light");
            for (int clip=0; clip<3; ++clip) {
                for (int pose=0; pose<5; ++pose) {
                    const auto name="C"+std::to_string(clip)+"P"+std::to_string(pose);
                    draw.bind_geometry(argv[1],Path(argv[4])/(name+".bin"));
                    draw.render(argv[1],"light",true);
                    draw.capture(argv[3],name);
                }
            }
            return 0;
        }
        draw.bind_geometry(argv[1]);
        for (const auto& mode:{"light","dark","flat","nonmetal"}) {
            draw.bind_textures(argv[2],mode);
            draw.render(argv[1],mode,true);
            draw.capture(argv[3],mode);
        }
        if (argc==5) {
            if (read(Path(argv[1])/"mesh.bin")!=read(Path(argv[4])/"mesh.bin"))
                throw std::runtime_error("Combined slots require one source mesh");
            draw.bind_textures(argv[2],"light");
            draw.render(argv[1],"light",true);
            draw.bind_geometry(argv[4]);
            draw.bind_textures(argv[4],"light");
            draw.render(argv[4],"light",false);
            draw.capture(argv[3],"combined");
        }
        if (argc==6) {
            const Path base=argv[1], add=argv[4];
            if (read(base/"mesh.bin")!=read(add/"mesh.bin") || read(base/"indices.bin")!=read(add/"indices.bin"))
                throw std::runtime_error("Additive pass must use the same indexed mesh");
            draw.bind_geometry(add);
            draw.bind_textures(argv[2],"light",true);
            draw.render(add,"light",true,true);
            draw.capture(argv[3],"add_only");
            for (const std::string mode:{"add_lit","add_off","add_reject"}) {
                draw.set_additive_state(false);
                draw.bind_geometry(base);
                draw.bind_textures(argv[2],"light");
                draw.render(base,"light",true);
                draw.bind_geometry(add);
                draw.bind_textures(argv[2],"light",true);
                draw.set_additive_state(true,mode=="add_reject");
                draw.render(add,mode=="add_off" ? "dark" : "light",false,true);
                draw.capture(argv[3],mode);
            }
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << "\n";
        return 1;
    }
}
