from pydantic import BaseModel


class ActionData(BaseModel):
    name: str = ""
    # context: dict = {}


class Action:

    async def run(self, action_data: ActionData, *args, **kwargs) -> ActionData:
        """
        run an action
        :param action_data:
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError
