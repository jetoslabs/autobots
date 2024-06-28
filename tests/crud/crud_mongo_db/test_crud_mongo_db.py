import pytest
from pydantic import BaseModel, Field, ConfigDict

from src.autobots import SettingsProvider
from src.autobots.data_model.context import Context
from src.autobots.crud.crud_mongo_db.crud_mongo_db import MongoDBCRUD
from src.autobots.crud.crud_protocol import CreateData, FindManyData, CrudBaseData


class MongoDbDocCreate(BaseModel):
    text: str
    number: int


class MongoDbDocFind(BaseModel):
    text: str


class MongoDbDoc(BaseModel):
    id: str = Field(..., alias='_id')
    text: str
    number: int

    model_config = ConfigDict(populate_by_name=True)


@pytest.mark.asyncio
async def test_crud_mongo_db_happy_path(set_test_settings):
    ctx = Context()
    settings = SettingsProvider.sget()
    name = "test_crud_mongo_db_happy_path"
    # client_gen = MongoDBCRUD.client_agen(ctx, settings)
    client = await MongoDBCRUD.client()
    try:
        for i in range(10):
            try:
                db = await MongoDBCRUD.database(ctx, settings, client)
                # db = MongoDBCRUD.database()
                collection = await MongoDBCRUD.collection(ctx, settings, db, name)
                await collection.drop()
                # MongoDBCRUD.create_one(ctx, collection, MongoDbDoc, MongoDbDoc(text="test", number=1))
                assert collection.name is not None
                crud_base_data = CrudBaseData(
                    ctx=ctx,
                    data_source=collection,
                    data_type=MongoDbDoc,
                    lite_data_type=MongoDbDoc,
                )
                create_data = CreateData(
                    create_params=MongoDbDocCreate(text="test", number=i),
                    **crud_base_data.model_dump(exclude_none=True)
                )
                created = await MongoDBCRUD.create([create_data])
                assert created is not None
                # await collection.insert_one({"text": "test", "number": i})
                find_many_data = FindManyData(
                    find_params=MongoDbDocFind(text="test"),
                    **crud_base_data.model_dump(exclude_none=True)
                )
                count = await MongoDBCRUD.count(find_many_data)
                assert count == 1
            except Exception as e:
                assert e is None
    finally:
        await MongoDBCRUD.close_client(ctx, client)
