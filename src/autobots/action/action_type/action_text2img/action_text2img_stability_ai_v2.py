# from typing import Optional, Type
#
# from autobots.action.action.action_doc_model import ActionCreate
# from autobots.action.action_type.abc.IAction import IAction, ActionOutputType, ActionInputType, ActionConfigType
# from autobots.action.action_type.action_types import ActionType
# from autobots.action.action.common_action_models import TextObj
# from autobots.conn.stability.stability import get_stability
# from autobots.conn.stability.stability_data import StabilityReq
#
# class ActionCreateGenImageStabilityAi(ActionCreate):
#     type: ActionType = ActionType.text2img_stability_ai
#     config: StabilityReq
#     input: Optional[TextObj] = None
#     output: Optional[ImagesRes] = None
#
#
# class ActionGenImageStabilityAiV2(IAction[StabilityReq, TextObj, ImagesRes]):
#     type = ActionType.text2img_stability_ai
#
#     @staticmethod
#     def get_config_type() -> Type[ActionConfigType]:
#         return StabilityReq
#
#     @staticmethod
#     def get_input_type() -> Type[ActionInputType]:
#         return TextObj
#
#     @staticmethod
#     def get_output_type() -> Type[ActionOutputType]:
#         return ImagesRes
#
#     def __init__(self, action_config: StabilityReq):
#         super().__init__(action_config)
#
#     async def run_action(self, action_input: TextObj) -> ImagesRes:
#         self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.text}"
#         file_url = await get_stability().text_to_image(self.action_config)
#         images = [ImageRes(url=file_url.unicode_string())]
#         return ImagesRes(images=images)
