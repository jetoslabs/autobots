import gotrue
from fastapi import APIRouter, Depends

from autobots import SettingsProvider
from autobots.auth.security import get_user_from_access_token
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.stable_diffusion import StableDiffusion

router = APIRouter(tags=["action_results/stable_diffusion"])


@router.post("/fetch/stable_diffusion")
async def fetch_stable_diffusion(
        stable_diffusion_id: int,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        # db: Database = Depends(get_mongo_db)
) -> StableDiffusionRes:
    # Later do it through user keys
    key = SettingsProvider.sget().STABLE_DIFFUSION_API_KEY
    res = await StableDiffusion(key).fetch_queued_image(stable_diffusion_id)
    return res
