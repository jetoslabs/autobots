import hashlib


def gen_filename(data: str) -> str:
    return hashlib.sha3_512(data.encode('utf-8')).hexdigest()
