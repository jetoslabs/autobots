from autobots.action.action import Action, ActionData
from autobots.conn.stability.stability import get_stability
from autobots.conn.stability.stability_data import StabilityReq


class StabilityChatData(ActionData):
    stability_req: StabilityReq
    image_bytes: bytes = None
    # context: List[Message] = []


class StabilityChat(Action):

    async def run(self, action_data: StabilityChatData, *args, **kwargs) -> StabilityChatData:
        img_bytes = await get_stability().text_to_image(action_data.stability_req)
        action_data.image_bytes = img_bytes
        return action_data # Don't return action_data as it is not new, same input object is modified
