from typing import Any
from src.autobots.user.user_orm_model import UserORM
from motor.motor_asyncio import AsyncIOMotorDatabase

class UserPollGraphMarket:
    def __init__(self, user: UserORM, db: AsyncIOMotorDatabase):
        self.user = user
        self.db = db

    async def get_market_data(self, poll_graph_id: str) -> Any:
        """
        Fetch market data related to a specific poll graph.
        
        :param poll_graph_id: The ID of the poll graph.
        :return: Market data for the specified poll graph.
        """
        # Implement logic to fetch market data from the database
        market_data = await self.db.market_collection.find_one({"poll_graph_id": poll_graph_id})
        return market_data

    async def update_market_data(self, poll_graph_id: str, data: dict) -> bool:
        """
        Update market data for a specific poll graph.
        
        :param poll_graph_id: The ID of the poll graph.
        :param data: The data to update.
        :return: True if the update was successful, False otherwise.
        """
        result = await self.db.market_collection.update_one(
            {"poll_graph_id": poll_graph_id},
            {"$set": data}
        )
        return result.modified_count > 0

    async def delete_market_data(self, poll_graph_id: str) -> bool:
        """
        Delete market data for a specific poll graph.
        
        :param poll_graph_id: The ID of the poll graph.
        :return: True if the deletion was successful, False otherwise.
        """
        result = await self.db.market_collection.delete_one({"poll_graph_id": poll_graph_id})
        return result.deleted_count > 0