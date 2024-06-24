from enum import Enum


class ActionType(str, Enum):
    # multimodal
    multimodal_assistant_openai = "multimodal_assistant_openai"
    multimodal_google_search = "multimodal_google_search"

    # text2text
    text2text_llm_chat_openai = "text2text_llm_chat_openai"
    text2text_llm_chat_claude = "text2text_llm_chat_claude"
    text2text_llm_chat_with_vector_search_openai = "text2text_llm_chat_with_vector_search_openai"
    text2text_read_url = "text2text_read_url"
    text2text_search_web = "text2text_search_web"
    text2text_search_maps = "text2text_search_maps"
    text2text_io_mapper = "text2text_io_mapper"
    text2text_user_input= "text2text_user_input"

    # text2img
    text2img_dalle_openai = "text2img_dalle_openai"
    text2img_stability_ai = "text2img_stability_ai"
    text2img_stable_diffusion = "text2img_stable_diffusion"
    text2img_search_image = "text2img_search_image"
    text2img_imagine_midjourney_ai = "text2img_imagine_midjourney_ai"
    text2img_button_midjourney_ai = "text2img_button_midjourney_ai"

    # img2img
    image_mixer_stable_diffusion = "image_mixer_stable_diffusion"
    img2img_stable_diffusion = "img2img_stable_diffusion"
    img2img_edit_openai = "img2img_edit_openai"
    img2img_variation_openai = "img2img_variation_openai"
    img2img_bulk_edit_claid = "img2img_bulk_edit_claid"
    img2img_photoshoot_claid = "img2img_photoshoot_claid"

    # text2video
    text2video_stable_diffusion = "text2video_stable_diffusion"
    text2video_search_video = "text2video_search_video"

    #video2video
    video2video_opus = "video2video_opus"
    # text2audio
    text2audio_speech_openai = "text2audio_openai"

    # audio2text
    audio2text_transcription_openai = "audio2text_transcription_openai"
    audio2text_translation_openai = "audio2text_translation_openai"

    # mock
    mock_action = "mock_action"


