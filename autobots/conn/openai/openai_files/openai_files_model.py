from os import PathLike
from typing import Mapping, IO, Literal

from autobots.conn.openai.openai_common_models import OpenaiExtraValues


class FileList(OpenaiExtraValues):
    purpose: str | None = None


class FileCreate(OpenaiExtraValues):
    file: IO[bytes] | bytes | PathLike[str] | PathLike | tuple[
        str | None, IO[bytes] | bytes | PathLike[str] | PathLike] | tuple[
              str | None, IO[bytes] | bytes | PathLike[str] | PathLike, str | None] | tuple[
              str | None, IO[bytes] | bytes | PathLike[str] | PathLike, str | None, Mapping[str, str]]
    purpose: Literal["fine-tune", "assistants"]


class FileDelete(OpenaiExtraValues):
    file_id: str


class FileRetrieve(OpenaiExtraValues):
    file_id: str


class FileContent(OpenaiExtraValues):
    file_id: str
