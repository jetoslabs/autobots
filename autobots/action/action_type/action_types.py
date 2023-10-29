from enum import Enum


class ActionType(str, Enum):
    # text2text
    text2text_llm_chat_openai = "text2text_llm_chat_openai"
    text2text_llm_chat_with_vector_search_openai = "text2text_llm_chat_with_vector_search_openai"

    # text2img
    text2img_dalle_openai = "text2img_dalle_openai"
    text2img_stability_ai = "text2img_stability_ai"
    text2img_stable_diffusion = "text2img_stable_diffusion"

    # img2img
    image_mixer_stable_diffusion = "image_mixer_stable_diffusion"

    # text2video
    text2video_stable_diffusion = "text2video_stable_diffusion"


