"""Extract files from a Civ V .fpk pack (e.g. Resource/DX9/UITextures.fpk).
Usage: python tools/fpk_extract.py <pack.fpk> <out_dir> <name prefix> [<name prefix> ...]
Layout (worked out 2026-10-12): int32 version, 'FPK_', 2 bytes, int32 count; per entry: int32 name length, name,
padding to 4 bytes, int32, int32, int32 size, int32 offset (from the start of the file)."""
import os, struct, sys

pack, out_dir, prefixes = sys.argv[1], sys.argv[2], [p.lower() for p in sys.argv[3:]]
d = open(pack, 'rb').read()
pos = 10
count = struct.unpack_from('<I', d, pos)[0]
pos += 4
os.makedirs(out_dir, exist_ok=True)
for _ in range(count):
    n = struct.unpack_from('<I', d, pos)[0]
    pos += 4
    name = d[pos:pos + n].decode('latin-1')
    pos += n + ((4 - n % 4) % 4)
    _a, _b, size, offset = struct.unpack_from('<IIII', d, pos)
    pos += 16
    if any(name.lower().startswith(p) for p in prefixes):
        with open(os.path.join(out_dir, name), 'wb') as f:
            f.write(d[offset:offset + size])
        print(name, size)
