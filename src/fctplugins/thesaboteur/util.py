def fnv32hash(source: str):
    # Ported from SabTool
    # Hashing is based on Fowler–Noll–Vo hash function
    # Module 4294967296 is to keep the value in uint32
    FNV32Offset = 0x811C9DC5
    FNV32Prime = 0x1000193
    data = source.encode('ASCII')
    hash_value = FNV32Offset
    for current_byte in data:
        hash_value = FNV32Prime * (hash_value ^ (current_byte | 0x20))
        hash_value = hash_value % 4294967296
    result = ((hash_value ^ 0x2A) * FNV32Prime) % 4294967296
    return result
