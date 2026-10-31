"""Bounded read-only random access to already supplied split archive parts."""
import bisect
import io
from pathlib import Path


class ArchivePartsReader(io.RawIOBase):
    def __init__(self, paths, max_read=16 * 1024 * 1024):
        super().__init__()
        if not paths or max_read <= 0:
            raise ValueError('Archive parts and a positive read bound are required')
        self._files = []
        self._starts = [0]
        self._position = 0
        self._max_read = max_read
        try:
            for path in paths:
                source = Path(path).open('rb')
                self._files.append(source)
                self._starts.append(self._starts[-1] + Path(path).stat().st_size)
        except Exception:
            self.close()
            raise

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self._position

    def seek(self, offset, whence=io.SEEK_SET):
        if self.closed:
            raise ValueError('Reader is closed')
        origins = {io.SEEK_SET: 0, io.SEEK_CUR: self._position, io.SEEK_END: self._starts[-1]}
        if whence not in origins or offset + origins[whence] < 0:
            raise ValueError('Invalid archive seek')
        self._position = origins[whence] + offset
        return self._position

    def read(self, size=-1):
        if self.closed:
            raise ValueError('Reader is closed')
        remaining = max(0, self._starts[-1] - self._position)
        size = remaining if size < 0 else min(size, remaining)
        if size > self._max_read:
            raise ValueError('Archive read exceeds the bounded buffer size')
        result = bytearray()
        while size:
            index = bisect.bisect_right(self._starts, self._position) - 1
            source = self._files[index]
            source.seek(self._position - self._starts[index])
            chunk = source.read(min(size, self._starts[index + 1] - self._position))
            if not chunk:
                raise EOFError('An archive part changed or was truncated')
            result.extend(chunk)
            size -= len(chunk)
            self._position += len(chunk)
        return bytes(result)

    def readinto(self, buffer):
        data = self.read(len(buffer))
        buffer[:len(data)] = data
        return len(data)

    def close(self):
        for source in getattr(self, '_files', []):
            source.close()
        super().close()
