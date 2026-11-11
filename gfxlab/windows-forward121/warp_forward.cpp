#include <d3d11.h>
#include <wrl/client.h>
#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <cstring>

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

    Draw() {
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
        desc.Format = DXGI_FORMAT_D24_UNORM_S8_UINT;
        ComPtr<ID3D11Texture2D> ds;
        require(device->CreateTexture2D(&desc,nullptr,&ds),"Depth texture");
        require(device->CreateDepthStencilView(ds.Get(),nullptr,&depth),"Depth view");
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

    ComPtr<ID3D11ShaderResourceView> texture2d(const Bytes& data, bool srgb, bool cube, UINT size, UINT levels) {
        D3D11_TEXTURE2D_DESC desc{};
        desc.Width = desc.Height = size;
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
                UINT width = size >> mip;
                size_t next = offset + size_t(width) * width * 4;
                if (width == 0 || next > data.size()) throw std::runtime_error("Wrong texture extent");
                uploads.push_back({data.data()+offset,width*4,0});
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

    void bind_geometry(const Path& dir) {
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
        require(device->CreateInputLayout(elements,5,vs.data(),vs.size(),&layout),"Source signature");
        ctx->IASetInputLayout(layout.Get());
        const auto mesh=read(dir/"mesh.bin"), indices=read(dir/"indices.bin");
        if (mesh.size()!=1666*48 || indices.size()!=2388*6) throw std::runtime_error("Wrong mesh shape");
        auto vb=buffer(mesh,D3D11_BIND_VERTEX_BUFFER);
        auto uv1=buffer(Bytes(1666*8,0),D3D11_BIND_VERTEX_BUFFER);
        auto ib=buffer(indices,D3D11_BIND_INDEX_BUFFER);
        ID3D11Buffer* streams[]{vb.Get(),uv1.Get()};
        UINT strides[]{48,8}, offsets[]{0,0};
        ctx->IASetVertexBuffers(0,2,streams,strides,offsets);
        ctx->IASetIndexBuffer(ib.Get(),DXGI_FORMAT_R16_UINT,0);
        ctx->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
    }

    void bind_textures(const Path& dir, const std::string& mode) {
        Bytes black{0,0,0,255}, cube;
        for (int i=0; i<6; ++i) cube.insert(cube.end(),black.begin(),black.end());
        std::array<ComPtr<ID3D11ShaderResourceView>,7> textures;
        textures[0] = texture2d(read(dir/"basecolor.rgba"),true,false,1024,11);
        textures[1] = mode=="nonmetal" ? texture2d(black,true,false,1,1)
            : texture2d(read(dir/"metallic.rgba"),true,false,1024,11);
        textures[2] = mode=="flat" ? texture2d(Bytes{255,128,255,128},false,false,1,1)
            : texture2d(read(dir/"normal.rgba"),false,false,1024,11);
        textures[3] = texture2d(Bytes{255,255,255,255},false,false,1,1);
        textures[4] = textures[5] = texture2d(cube,false,true,1,1);
        textures[6] = volume();
        std::array<ID3D11ShaderResourceView*,7> views{};
        for (size_t i=0; i<textures.size(); ++i) views[i]=textures[i].Get();
        ctx->PSSetShaderResources(0,static_cast<UINT>(views.size()),views.data());

        std::array<ComPtr<ID3D11SamplerState>,6> samplers;
        std::array<ID3D11SamplerState*,6> handles{};
        for (UINT i=0; i<samplers.size(); ++i) {
            D3D11_SAMPLER_DESC desc{};
            desc.Filter=D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT;
            desc.AddressU=desc.AddressV=desc.AddressW=(i>=2 && i<=4)
                ? D3D11_TEXTURE_ADDRESS_WRAP : D3D11_TEXTURE_ADDRESS_CLAMP;
            desc.MaxLOD=D3D11_FLOAT32_MAX;
            desc.MaxAnisotropy=1;
            desc.ComparisonFunc=D3D11_COMPARISON_NEVER;
            require(device->CreateSamplerState(&desc,&samplers[i]),"Source sampler");
            handles[i]=samplers[i].Get();
        }
        ctx->PSSetSamplers(0,static_cast<UINT>(handles.size()),handles.data());
    }

    void capture(const Path& dir, const Path& output, const std::string& mode) {
        std::string light = mode=="dark" ? "dark" : "light";
        std::array<ComPtr<ID3D11Buffer>,8> constants;
        std::array<ID3D11Buffer*,8> slots{};
        for (UINT i=0; i<slots.size(); ++i) {
            std::string stage = i<4 ? "vertex" : "fragment";
            constants[i]=buffer(read(dir/(stage+"-"+light+"-"+std::to_string(i%4)+".bin")),
                                D3D11_BIND_CONSTANT_BUFFER);
            slots[i]=constants[i].Get();
        }
        ctx->VSSetConstantBuffers(0,4,slots.data());
        ctx->PSSetConstantBuffers(0,4,slots.data()+4);
        const float clear[]{0,0,0,0};
        ctx->ClearRenderTargetView(color.Get(),clear);
        ctx->ClearDepthStencilView(depth.Get(),D3D11_CLEAR_DEPTH,1,0);
        ctx->DrawIndexed(2388*3,0,0);
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
    if (argc!=4) return 2;
    try {
        Draw draw;
        draw.bind_geometry(argv[1]);
        for (const auto& mode:{"light","dark","flat","nonmetal"}) {
            draw.bind_textures(argv[2],mode);
            draw.capture(argv[1],argv[3],mode);
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << "\n";
        return 1;
    }
}
