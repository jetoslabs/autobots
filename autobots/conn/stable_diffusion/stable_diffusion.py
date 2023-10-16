from autobots.conn.stable_diffusion.text2img import text2img


class StableDiffusion:

    def __init__(self, stable_diffusion_api_key):
        # self.api_key = stable_diffusion_api_key
        self.text2img = text2img
