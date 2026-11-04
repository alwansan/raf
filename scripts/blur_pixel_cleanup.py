"""Source-locked Blur pixel-pass cleanup; original rendering body is retained."""
import re
def protect(source):
    signature='protected void ApplyPixelShader(RenderTexture target)'
    if source.count(signature)!=1:raise ValueError('Blur method identity drift')
    opening=source.index('{',source.index(signature));depth=1;end=opening+1
    while depth and end<len(source):
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    if depth:raise ValueError('Blur method braces')
    body=source[opening+1:end-1]
    match=re.search(r'FilterMode\s+(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<target>(?:target|\(\((?:UnityEngine\.)?Texture\)target\)))\.filterMode;',body)
    if match is None:raise ValueError('Blur filter capture drift')
    capture=match[0]
    allocation='RenderTexture temporary = RenderTexture.GetTemporary('
    cleanup=match['target']+'.filterMode = '+match['name']+';'
    release='RenderTexture.ReleaseTemporary(temporary);'
    if any(body.count(x)!=1 for x in (capture,allocation,cleanup,release)):
        raise ValueError('Blur cleanup contract drift')
    if body.index(capture)>body.index(allocation) or body.index(cleanup)>body.index(release):
        raise ValueError('Blur cleanup ordering drift')
    prefix,work=body.split(capture)
    work=work.replace(allocation,'temporary = RenderTexture.GetTemporary(',1)
    at=work.index(cleanup)
    if work[at+len(cleanup):].strip()!=release:raise ValueError('Blur trailing operations drift')
    work=work[:at].rstrip()
    result=(prefix+capture+'\n            RenderTexture temporary = null;\n            try\n            {\n'+
            work+'\n            }\n            finally\n            {\n                try\n                {\n                    '+cleanup+
            '\n                }\n                finally\n                {\n                    if (temporary != null)\n                        '+release+
            '\n                }\n            }\n        ')
    return source[:opening+1]+result+source[end-1:]

