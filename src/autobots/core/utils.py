import hashlib
import random
import string
import uuid


def gen_hash(data: str) -> str:
    return hashlib.sha3_512(data.encode("utf-8")).hexdigest()


def gen_uuid() -> uuid.UUID:
    # This function (uuid4) guarantees the random no. and doesn’t compromise with privacy.
    trace_id: uuid.UUID = uuid.uuid4()
    return trace_id


def gen_random_str(k: int = 9) -> str:
    random_str = "".join(random.choices(string.hexdigits, k=k))
    return random_str
