from typing import Literal

from pydantic import BaseModel


class SpeechReq(BaseModel):
    input: str
    model: Literal["tts-1", "tts-1-hd"] = "tts-1"
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"
    response_format: Literal["mp3", "opus", "aac", "flac"] = "mp3"
    speed: float = 1.0
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    # extra_headers: Headers | None = None,
    # extra_query: Query | None = None,
    # extra_body: Body | None = None,
    # timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
