from typing import List, Protocol

from pydantic import BaseModel

from src.autobots.data_model.data import MetaData


class KnowledgeMeta(BaseModel):
    pass


class Knowledge(MetaData):
    meta: KnowledgeMeta


class KnowledgeCreate(BaseModel):
    pass


class KnowledgeFind(BaseModel):
    pass


class KnowledgeUpdate(BaseModel):
    pass


class KnowledgeDelete(BaseModel):
    pass


class KnowledgeProtocol(Protocol[Knowledge]):
    @staticmethod
    async def create_knowledge(params: KnowledgeCreate) -> List[Knowledge]: ...

    @staticmethod
    async def get_knowledge(params: KnowledgeFind) -> Knowledge: ...

    @staticmethod
    async def update_knowledge(params: KnowledgeUpdate) -> List[Knowledge]: ...

    @staticmethod
    async def delete_knowledge(params: KnowledgeDelete) -> List[Knowledge]: ...

    @staticmethod
    async def find_knowledge(find_knowledge: KnowledgeFind) -> List[Knowledge]: ...
