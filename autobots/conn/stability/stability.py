import io
import warnings
from typing import Any, Sequence

from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

from autobots.conn.stability.stability_data import StabilityReq, StabilityUpscaleReq
from autobots.core.settings import get_settings


class Stability:

    def __init__(
            self,
            host: str = get_settings().STABILITY_HOST,
            key: str = get_settings().STABILITY_KEY,
            engine: str = "stable-diffusion-xl-1024-v0-9",#"stable-diffusion-xl-beta-v2-2-2",
            upscale_engine: str = "stable-diffusion-x4-latent-upscaler",
            verbose: bool = True,
            wait_for_ready: bool = True
    ):
        # Set up our connection to the API.
        self.stability_api = client.StabilityInference(
            host=host,
            key=key,  # API Key reference.
            verbose=verbose,  # True,  # Print debug messages.
            engine=engine,  # "stable-diffusion-xl-beta-v2-2-2",  # Set the engine to use for generation.
            # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
            # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-diffusion-xl-beta-v2-2-2 stable-inpainting-v1-0 stable-inpainting-512-v2-0
        )

    async def text_to_image(self, stability_req: StabilityReq) -> bytes:
        # Set up our initial generation parameters.
        answers = self.stability_api.generate(
            prompt=stability_req.prompt,  # "expansive landscape rolling greens with blue daisies and weeping willow trees under a blue alien sky, masterful, ghibli",
            seed=stability_req.seed,  # 992446758,  # If a seed is provided, the resulting generated image will be deterministic.
            # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
            # Note: This isn't quite the case for CLIP Guided generations, which we tackle in the CLIP Guidance documentation.
            steps=stability_req.steps,  # Amount of inference steps performed on image generation. Defaults to 30.
            cfg_scale=stability_req.cfg_scale,  # 8.0,  # Influences how strongly your generation is guided to match your prompt.
            # Setting this value higher increases the strength in which it tries to match your prompt.
            # Defaults to 7.0 if not specified.
            width=stability_req.width,  # 512,  # Generation width, defaults to 512 if not included.
            height=stability_req.height,  # 512,  # Generation height, defaults to 512 if not included.
            samples=stability_req.samples,  # 1,  # Number of images to generate, defaults to 1 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M  # Choose which sampler we want to denoise our generation with.
            # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
            # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        )

        # Set up our warning to print to the console if the adult content classifier is tripped.
        # If adult content classifier is not tripped, save generated images.
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    # Save our generated images with their seed number as the filename.
                    img.save(str(artifact.seed) + ".png")
                    return artifact.binary

    async def upscale_image(self, stability_upscale_req: StabilityUpscaleReq) -> bytes:
        """
        https://platform.stability.ai/docs/features/image-upscaling
        :param stability_upscale_req:
        :type stability_upscale_req:
        :return:
        :rtype:
        """
        answers = self.stability_api.upscale(**stability_upscale_req.dict())

        # Set up our warning to print to the console if the adult content classifier is tripped.
        # If adult content classifier is not tripped, save our image.

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please submit a different image and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    big_img = Image.open(io.BytesIO(artifact.binary))
                    big_img.save("imageupscaled" + ".png")  # Save our image to a local file.
                    return artifact.binary