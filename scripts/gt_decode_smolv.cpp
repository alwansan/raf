#include "smolv.h"
#include <iostream>
#include <iterator>
#include <vector>

int main()
{
    const std::vector<char> encoded(
        std::istreambuf_iterator<char>(std::cin), std::istreambuf_iterator<char>{});
    const size_t size = smolv::GetDecodedBufferSize(encoded.data(), encoded.size());
    if (size < 20 || size > 16 * 1024 * 1024)
        return 1;
    std::vector<char> decoded(size);
    if (!smolv::Decode(encoded.data(), encoded.size(), decoded.data(), size))
        return 2;
    std::cout.write(decoded.data(), decoded.size());
    return std::cout ? 0 : 3;
}
