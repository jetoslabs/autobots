from autobots.action.action_type.action_audio2text.action_audio2text_transcription_openai import \
    ActionAudio2TextTranscriptionOpenai
from autobots.action.action_type.action_audio2text.action_audio2text_translation_openai import \
    ActionAudio2TextTranslationOpenai
from autobots.action.action_type.action_img2img.action_image_mixer_stable_diffusion import \
    ActionImageMixerStableDiffusion
from autobots.action.action_type.action_img2img.action_img2img_edit_openai import ActionImg2ImgEditOpenai
from autobots.action.action_type.action_img2img.action_img2img_variation_openai import ActionImg2ImgVariationOpenai
from autobots.action.action_type.action_text2audio.action_text2audio_speech_openai import ActionText2AudioSpeechOpenai
from autobots.action.action_type.action_text2img.action_text2img_dalle_openai_v2 import ActionGenImageDalleOpenAiV2
from autobots.action.action_type.action_text2img.action_text2img_search_image import ActionText2ImgSearchImage
from autobots.action.action_type.action_text2img.action_text2img_stable_diffusion import ActionText2ImgStableDiffusion
from autobots.action.action_type.action_text2img.action_text2img_midjourney import ActionText2ImgMidjourney
from autobots.action.action_type.action_text2text.action_text2text_io_mapper.action_text2text_io_mapper import \
    ActionText2TextIOMapper
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import \
    ActionText2TextLlmChatOpenai
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionText2TextLlmChatWithVectorSearchOpenai
from autobots.action.action_type.action_text2text.action_text2text_read_url import ActionText2TextReadUrl
from autobots.action.action_type.action_text2text.action_text2text_search_map import ActionText2TextSearchMaps
from autobots.action.action_type.action_text2text.action_text2text_search_web import ActionText2TextSearchWeb
from autobots.action.action_type.action_text2video.action_text2video_search_video import ActionText2VideoSearchVideo
from autobots.action.action_type.action_text2video.action_text2video_stable_diffusion import \
    ActionText2VideoStableDiffusion
from autobots.action.action_type.action_types import ActionType

ACTION_MAP = {
    # text2text
    ActionType.text2text_llm_chat_openai: ActionText2TextLlmChatOpenai,
    ActionType.text2text_llm_chat_with_vector_search_openai: ActionText2TextLlmChatWithVectorSearchOpenai,
    ActionType.text2text_read_url: ActionText2TextReadUrl,
    ActionType.text2text_search_web: ActionText2TextSearchWeb,
    ActionType.text2text_search_maps: ActionText2TextSearchMaps,
    ActionType.text2text_io_mapper: ActionText2TextIOMapper,
    # text2img
    ActionType.text2img_dalle_openai: ActionGenImageDalleOpenAiV2,
    ActionType.text2img_stable_diffusion: ActionText2ImgStableDiffusion,
    ActionType.text2img_search_image: ActionText2ImgSearchImage,
    ActionType.text2img_midjourney_ai: ActionText2ImgMidjourney,
    # img2img
    ActionType.image_mixer_stable_diffusion: ActionImageMixerStableDiffusion,
    ActionType.img2img_edit_openai: ActionImg2ImgEditOpenai,
    ActionType.img2img_variation_openai: ActionImg2ImgVariationOpenai,
    # text2video
    ActionType.text2video_stable_diffusion: ActionText2VideoStableDiffusion,
    ActionType.text2video_search_video: ActionText2VideoSearchVideo,
    # text2audio
    ActionType.text2audio_speech_openai: ActionText2AudioSpeechOpenai,
    # audio2text
    ActionType.audio2text_transcription_openai: ActionAudio2TextTranscriptionOpenai,
    ActionType.audio2text_translation_openai: ActionAudio2TextTranslationOpenai,
    # mock
    # ActionType.mock_action: "mock_action"
}
