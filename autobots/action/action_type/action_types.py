from enum import Enum


class ActionType(str, Enum):
    # text2text
    text2text_llm_chat_openai = "text2text_llm_chat_openai"
    text2text_llm_chat_with_vector_search_openai = "text2text_llm_chat_with_vector_search_openai"
    text2text_read_url = "text2text_read_url"
    text2text_search_web = "text2text_search_web"
    text2text_search_maps = "text2text_search_maps"
    text2text_io_mapper = "text2text_io_mapper"

    # text2img
    text2img_dalle_openai = "text2img_dalle_openai"
    text2img_stability_ai = "text2img_stability_ai"
    text2img_stable_diffusion = "text2img_stable_diffusion"

    # img2img
    image_mixer_stable_diffusion = "image_mixer_stable_diffusion"
    img2img_stable_diffusion = "img2img_stable_diffusion"
    img2img_edit_openai = "img2img_edit_openai"
    img2img_variation_openai = "img2img_variation_openai"

    # text2video
    text2video_stable_diffusion = "text2video_stable_diffusion"

    # text2audio
    text2audio_speech_openai = "text2audio_openai"

    # audio2text
    audio2text_transcription_openai = "audio2text_transcription_openai"
    audio2text_translation_openai = "audio2text_translation_openai"

    # mock
    mock_action = "mock_action"


