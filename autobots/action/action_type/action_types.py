from enum import Enum


class ActionType(str, Enum):
    # text2text
    gen_text_llm_chat_openai = "gen_text_llm_chat_openai"
    gen_text_llm_chat_with_vector_search_openai = "gen_text_llm_chat_with_vector_search_openai"

    # text2img
    gen_image_dalle_openai = "gen_image_dalle_openai"
    gen_image_stability_ai = "gen_image_stability_ai"
    text2img_stable_diffusion = "text2img_stable_diffusion"

    # img2img
    image_mixer_stable_diffusion = "image_mixer_stable_diffusion"

    # text2video
    text2video_stable_diffusion = "text2video_stable_diffusion"


