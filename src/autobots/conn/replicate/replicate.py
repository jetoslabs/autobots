import replicate

from src.autobots.conn.replicate.virtual_try_on.virtual_try_on import VirtualTryOn
from src.autobots.conn.replicate.yan_ops.yan_ops_face_swap import YanOpsFaceSwap
from src.autobots.core.settings import Settings, SettingsProvider


class Replicate:

    def __init__(self, api_key: str):
        self.client = replicate.client.Client(api_token=api_key)
        self.yan_ops_face_swap = YanOpsFaceSwap(self.client)
        self.virtual_try_on = VirtualTryOn(self.client)

    async def list_collections_namespace(self):
        collections = [collection for page in replicate.paginate(self.client.collections.list) for collection in page]
        return collections

    async def list_models(self):
        models = [model for page in replicate.paginate(self.client.models.list) for model in page]
        return models


def get_replicate(settings: Settings = SettingsProvider.sget()) -> Replicate:
    return Replicate(settings.REPLICATE_API_KEY)
