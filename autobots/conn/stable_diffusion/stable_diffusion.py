from autobots.conn.stable_diffusion.fetch_queued_image import fetch_queued_image
from autobots.conn.stable_diffusion.image_mixer import image_mixer
from autobots.conn.stable_diffusion.text2img import text2img
from autobots.conn.stable_diffusion.text2video import text2video


class StableDiffusion:

    def __init__(self, stable_diffusion_api_key):
        # self.api_key = stable_diffusion_api_key
        self.text2img = text2img
        self.image_mixer = image_mixer
        self.text2video = text2video
        self.fetch_queued_image = fetch_queued_image
