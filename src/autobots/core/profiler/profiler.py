import json
import time
from typing import Any, Dict

import psutil
import gc
import sys
import _pickle as cPickle

from loguru import logger

from src.autobots.conn.aws.aws_s3 import get_s3


class Profiler:

    @staticmethod
    async def do_memory_profile() -> Dict[str, Any]:
        profile_memory = await Profiler.profile_memory()
        logger.bind(profile_memory=profile_memory).info("Profile memory")
        if profile_memory.get("available_mb") <= 500:
            filename = f"memory_dump_{round(time.time())}"
            logger.info(f"Saving memory_dump to s3: {filename}")
            await Profiler.memory_dump(filename)
            await Profiler.save_to_s3(filename)
            logger.info(f"Saved memory_dump to s3: {filename}")
        return profile_memory

    @staticmethod
    async def profile_memory() -> Dict[str, Any]:
        virtual_memory = psutil.virtual_memory()
        percent = virtual_memory.percent
        total = virtual_memory.total / 1000000
        available = virtual_memory.available / 1000000
        used = virtual_memory.used / 1000000
        free = virtual_memory.free / 1000000
        return {
            "percent": percent,
            "total_mb": total,
            "available_mb": available,
            "used_mb": used,
            "free_mb": free
        }

    @staticmethod
    async def memory_dump(filename: str) -> None:
        with open(f"{filename}.pickle", 'wb') as dump:
            xs = []
            for obj in gc.get_objects():
                try:
                    i = id(obj)
                    size = sys.getsizeof(obj, 0)
                    #    referrers = [id(o) for o in gc.get_referrers(obj) if hasattr(o, '__class__')]
                    referents = [id(o) for o in gc.get_referents(obj) if hasattr(o, '__class__')]
                    if hasattr(obj, '__class__'):
                        cls = str(obj.__class__)
                        xs.append({'id': i, 'class': cls, 'size': size, 'referents': referents})
                except Exception as e:
                    logger.error(str(e))
            cPickle.dump(xs, dump)

    @staticmethod
    async def save_to_s3(filename: str):
        s3 = get_s3(object_prefix="system/")
        obj = cPickle.load(open(f"{filename}.pickle", "rb"))
        obj_str = json.dumps(obj)
        await s3.put(obj_str, f"{filename}.pickle")
