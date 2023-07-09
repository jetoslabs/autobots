import hashlib


def gen_hash(data: str) -> str:
    return hashlib.sha3_512(data.encode('utf-8')).hexdigest()
