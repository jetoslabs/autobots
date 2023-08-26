from enum import Enum


class ActionType(str, Enum):
    gen_text_llm_chat_openai = "gen_text_llm_chat_openai"

    gen_image_dalle_openai = "gen_image_dalle_openai"
    gen_image_stability_ai = "gen_image_stability_ai"
    # gen_text: GenText
    # gen_image: GenImage
    # gen_video: GenVideo
