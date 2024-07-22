from src.autobots.action.action_type.action_multimodal.action_multimodal_google_search.action_multimodal_google_search import \
    ActionMultimodalGoogleSearch
from src.autobots.action.action_type.action_audio2text.action_audio2text_transcription_openai import \
    ActionAudio2TextTranscriptionOpenai
from src.autobots.action.action_type.action_audio2text.action_audio2text_translation_openai import \
    ActionAudio2TextTranslationOpenai
from src.autobots.action.action_type.action_audio2text.action_audio2text_transcription_assemblyai import \
    ActionAudio2TextTranscriptionAssemblyai

from src.autobots.action.action_type.action_img2img.action_image_mixer_stable_diffusion import \
    ActionImageMixerStableDiffusion
from src.autobots.action.action_type.action_img2img.action_img2img_bulkedit_claid import ActionImg2BulkEditClaid
from src.autobots.action.action_type.action_img2img.action_img2img_edit_openai import ActionImg2ImgEditOpenai
from src.autobots.action.action_type.action_img2img.action_img2img_photoshoot_claid import ActionImg2ImgPhotoshootClaid
from src.autobots.action.action_type.action_img2img.action_img2img_variation_openai import ActionImg2ImgVariationOpenai
from src.autobots.action.action_type.action_mock.action_mock import MockAction
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.action_multimodal_assistant_openai import \
    ActionMultimodalAssistantOpenai
from src.autobots.action.action_type.action_text2audio.action_text2audio_speech_openai import ActionText2AudioSpeechOpenai
from src.autobots.action.action_type.action_text2img.action_text2img_dalle_openai_v2 import ActionGenImageDalleOpenAiV2
from src.autobots.action.action_type.action_text2img.action_text2img_imagine_midjourney import ActionText2ImgMidjourney
from src.autobots.action.action_type.action_text2img.action_text2img_midjourney_button import \
    ActionText2ImgMidjourneyButton
from src.autobots.action.action_type.action_text2img.action_text2img_search_image import ActionText2ImgSearchImage
from src.autobots.action.action_type.action_text2img.action_text2img_stable_diffusion import ActionText2ImgStableDiffusion
from src.autobots.action.action_type.action_text2text.action_text2text_api import ActionText2textAPI
from src.autobots.action.action_type.action_text2text.action_text2text_io_mapper.action_text2text_io_mapper import \
    ActionText2TextIOMapper
from src.autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import \
    ActionText2TextLlmChatOpenai
from src.autobots.action.action_type.action_text2text.action_text2text_llm_chat_claude import \
    ActionText2TextLlmChatclaude
from src.autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionText2TextLlmChatWithVectorSearchOpenai
# from src.autobots.action.action_type.action_text2text.action_multimodal_llm_chat_with_vector_search_openai import ActionMultiModalLlmChatWithVectorSearchOpenai
from src.autobots.action.action_type.action_text2text.action_text2text_read_urls import ActionText2TextReadUrl
from src.autobots.action.action_type.action_text2text.action_text2text_search_map import ActionText2TextSearchMaps
from src.autobots.action.action_type.action_text2text.action_text2text_search_web import ActionText2TextSearchWeb
from src.autobots.action.action_type.action_text2text.action_text2text_user_input import ActionText2textUserInput
from src.autobots.action.action_type.action_text2video.action_text2video_search_video import ActionText2VideoSearchVideo
from src.autobots.action.action_type.action_text2video.action_text2video_stable_diffusion import \
    ActionText2VideoStableDiffusion
from src.autobots.action.action_type.action_video2video.action_video2video_opus import ActionVideo2VideoOpus
from src.autobots.action.action_type.action_linkedin.action_linkedin import ActionLinkedInScrape

from src.autobots.action.action_type.action_types import ActionType

ACTION_MAP = {
    # multimodal
    ActionType.multimodal_assistant_openai: ActionMultimodalAssistantOpenai,
    ActionType.multimodal_google_search: ActionMultimodalGoogleSearch,
    # text2text
    ActionType.text2text_llm_chat_openai: ActionText2TextLlmChatOpenai,
    ActionType.text2text_llm_chat_claude: ActionText2TextLlmChatclaude,
    ActionType.text2text_llm_chat_with_vector_search_openai: ActionText2TextLlmChatWithVectorSearchOpenai,
    # ActionType.multimodal_llm_chat_with_vector_search_openai: ActionMultiModalLlmChatWithVectorSearchOpenai,
    ActionType.text2text_read_url: ActionText2TextReadUrl,
    ActionType.text2text_search_web: ActionText2TextSearchWeb,
    ActionType.text2text_search_maps: ActionText2TextSearchMaps,
    ActionType.text2text_io_mapper: ActionText2TextIOMapper,
    ActionType.text2text_user_input: ActionText2textUserInput,
    ActionType.text2text_api_call: ActionText2textAPI,

    # text2img
    ActionType.text2img_dalle_openai: ActionGenImageDalleOpenAiV2,
    ActionType.text2img_stable_diffusion: ActionText2ImgStableDiffusion,
    ActionType.text2img_search_image: ActionText2ImgSearchImage,
    ActionType.text2img_imagine_midjourney_ai: ActionText2ImgMidjourney,
    ActionType.text2img_button_midjourney_ai: ActionText2ImgMidjourneyButton,
    # img2img
    ActionType.image_mixer_stable_diffusion: ActionImageMixerStableDiffusion,
    ActionType.img2img_edit_openai: ActionImg2ImgEditOpenai,
    ActionType.img2img_variation_openai: ActionImg2ImgVariationOpenai,
    ActionType.img2img_bulk_edit_claid: ActionImg2BulkEditClaid,
    ActionType.img2img_photoshoot_claid: ActionImg2ImgPhotoshootClaid,
    # text2video
    ActionType.text2video_stable_diffusion: ActionText2VideoStableDiffusion,
    ActionType.text2video_search_video: ActionText2VideoSearchVideo,
    # text2audio
    ActionType.text2audio_speech_openai: ActionText2AudioSpeechOpenai,
    # audio2text
    ActionType.audio2text_transcription_openai: ActionAudio2TextTranscriptionOpenai,
    ActionType.audio2text_translation_openai: ActionAudio2TextTranslationOpenai,
    ActionType.audio2text_transcription_assemblyai: ActionAudio2TextTranscriptionAssemblyai,
    #video2video
    ActionType.video2video_opus: ActionVideo2VideoOpus,
    ActionType.action_linkedin: ActionLinkedInScrape,
    # mock
    ActionType.mock_action: MockAction,

}
