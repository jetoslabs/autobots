from enum import Enum


class ActionType(str, Enum):
    gen_text_llm_chat_openai = "gen_text_llm_chat_openai"

    gen_text_llm_chat_with_vector_search_openai = "gen_text_llm_chat_with_vector_search_openai"

    gen_image_dalle_openai = "gen_image_dalle_openai"
    gen_image_stability_ai = "gen_image_stability_ai"


