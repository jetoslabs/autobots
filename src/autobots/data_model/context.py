from pydantic import BaseModel

from src.autobots.core.utils import gen_uuid


class Context(BaseModel):
    trace_id: str = str(gen_uuid())
    span: str | None = None
    user_id: str | None = None

    # def to_dict(self) -> Dict[str, Any]:
    #     return self.model_dump(exclude_none=True)


class ContextData(BaseModel):
    ctx: Context
