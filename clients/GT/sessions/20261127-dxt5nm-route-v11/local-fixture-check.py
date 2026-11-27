"""Independently reconstruct the authored C# V11 block pattern; no exporter or original assets."""
from PIL import Image
from io import BytesIO
from struct import pack
from math import isqrt
from hashlib import sha256

def dds(raw,w,h):
    hdr=pack('<7I',124,0x81007,h,w,len(raw),0,1)+bytes(44)+pack('<II4s5I',32,4,b'DXT5',0,0,0,0,0)+pack('<5I',0x1000,0,0,0,0)
    assert len(hdr)==124
    return Image.open(BytesIO(b'DDS '+hdr+raw)).convert('RGBA').transpose(Image.Transpose.FLIP_TOP_BOTTOM)

def authored(i):
    raw=bytearray()
    for b in range(5):
        six=(b+i)&1; a0,a1=(0,200) if six else (240,16); aidx=cidx=0
        for y in range(4):
            for x in range(4):
                p=4*y+x; ai=(x+2*y+b+i)%8
                if six and x==0 and y<2: ai=6+y
                aidx|=ai<<(3*p); cidx|=((x+y+b+2*i)%4)<<(2*p)
        c0,c1=(0x43e0,0xbff0) if six else (0xfc10,0x079f)
        if b==0:c1=c0
        raw.extend(bytes((a0,a1))+aidx.to_bytes(6,'little')+pack('<HHI',c0,c1,cidx))
    return bytes(raw)

def norm(im,swap=False,invert_y=False):
    result=Image.new('RGBA',im.size); pix=[]
    for r,g,b,a in im.getdata():
        x,y=(g,a) if swap else (a,g)
        if invert_y:y=255-y
        z=(isqrt(max(0,255**2-(2*x-255)**2-(2*y-255)**2))+255)//2
        pix.append((x,y,z,r))
    result.putdata(pix);return result

images=[]
for i in range(2):
    raw=authored(i); packed=dds(raw[:64],5,7); normal=norm(packed); images.append(normal)
    z=[p[2] for p in normal.getdata()]; print(i,sha256(raw[:64]).hexdigest(),sha256(normal.tobytes()).hexdigest(),'pixels',len(z),'interior',sum(v>127 for v in z),'clamped',z.count(127))
    assert any(v>127 for v in z) and 127 in z
    for name,img in [('packed',packed),('swap',norm(packed,swap=True)),('Y',norm(packed,invert_y=True)),('vertical',normal.transpose(Image.Transpose.FLIP_TOP_BOTTOM)),('horizontal',normal.transpose(Image.Transpose.FLIP_LEFT_RIGHT))]:
        n=sum(a!=b for a,b in zip(img.getdata(),normal.getdata()));print(' ',name,n);assert n
assert images[0].tobytes()!=images[1].tobytes()
print('LOCAL INDEPENDENT FIXTURE NONDEGENERACY PASS (not actual export)')
