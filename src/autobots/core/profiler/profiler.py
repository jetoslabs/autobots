from typing import Any, Dict

import psutil


class Profiler:

    @staticmethod
    async def profile_memory() -> Dict[str, Any]:
        virtual_memory = psutil.virtual_memory()
        return virtual_memory.__dict__
