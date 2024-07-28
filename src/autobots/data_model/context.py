from pydantic import BaseModel, Field

from src.autobots.core.utils import gen_uuid


class Context(BaseModel):
    # trace_id: str = str(gen_uuid())
    trace_id: str = Field(default_factory=lambda: str(gen_uuid()))
    user_id: str | None = None

    # def to_dict(self) -> Dict[str, Any]:
    #     return self.model_dump(exclude_none=True)


class ContextData(BaseModel):
    ctx: Context
