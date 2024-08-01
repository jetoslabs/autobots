from functools import lru_cache
from typing import List, Optional, Any, Literal

from fastapi import UploadFile
from loguru import logger
from pydantic import BaseModel, ValidationError, Field
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError
from unstructured_client.models.operations import PartitionResponse, PartitionRequest

from src.autobots.core.settings import Settings, SettingsProvider


class PartitionParametersParams(BaseModel):
    # files: Optional[Files]
    # r"""The file to extract"""
    chunking_strategy: Optional[Literal["by_title"]] = Field(default=None)
    r"""Use one of the supported strategies to chunk the returned elements. Currently supports: by_title"""
    combine_under_n_chars: Optional[int] = Field(default=None)
    r"""If chunking strategy is set, combine elements until a section reaches a length of n chars. Default: 500"""
    coordinates: Optional[bool] = Field(default=None)
    r"""If true, return coordinates for each element. Default: false"""
    encoding: Optional[str] = Field(default=None)
    r"""The encoding method used to decode the text input. Default: utf-8"""
    extract_image_block_types: Optional[List[str]] = Field(default=None)
    r"""The types of elements to extract, for use in extracting image blocks as base64 encoded data stored in metadata fields"""
    gz_uncompressed_content_type: Optional[str] = Field(default=None)
    r"""If file is gzipped, use this content type after unzipping"""
    hi_res_model_name: Optional[Literal["detectron2_onnx", "yolox", "yolox_quantized", "chipper"]] = Field(default=None)
    r"""The name of the inference model used when strategy is hi_res"""
    """https://unstructured-io.github.io/unstructured/best_practices/models.html
    List of Available Models in the Partitions:
    1. detectron2_onnx is a Computer Vision model by Facebook AI that provides object detection and segmentation algorithms with ONNX Runtime. It is the fastest model with the hi_res strategy.
    2. yolox is a single-stage real-time object detector that modifies YOLOv3 with a DarkNet53 backbone.
    3. yolox_quantized: runs faster than YoloX and its speed is closer to Detectron2.
    4. chipper (beta version): the Chipper model is Unstructured’s in-house image-to-text model based on transformer-based Visual Document Understanding (VDU) models.
    """
    include_page_breaks: Optional[bool] = Field(default=None)
    r"""If True, the output will include page breaks if the filetype supports it. Default: false"""
    languages: Optional[List[str]] = Field(default=None)
    r"""The languages present in the document, for use in partitioning and/or OCR"""
    max_characters: Optional[int] = Field(default=None)
    r"""If chunking strategy is set, cut off new sections after reaching a length of n chars (hard max). Default: 1500"""
    multipage_sections: Optional[bool] = Field(default=None)
    r"""If chunking strategy is set, determines if sections can span multiple sections. Default: true"""
    new_after_n_chars: Optional[int] = Field(default=None)
    r"""If chunking strategy is set, cut off new sections after reaching a length of n chars (soft max). Default: 1500"""
    output_format: Optional[str] = Field(default=None)
    r"""The format of the response. Supported formats are application/json and text/csv. Default: application/json."""
    overlap: Optional[int] = Field(default=None)
    r"""A prefix of this many trailing characters from prior text-split chunk is applied to second and later chunks formed from oversized elements by text-splitting. Default: None"""
    overlap_all: Optional[bool] = Field(default=None)
    r"""When True, overlap is also applied to 'normal' chunks formed by combining whole elements. Use with caution as this can introduce noise into otherwise clean semantic units. Default: None"""
    pdf_infer_table_structure: Optional[bool] = Field(default=None)
    r"""If True and strategy=hi_res, any Table Elements extracted from a PDF will include an additional metadata field, 'text_as_html', where the value (string) is a just a transformation of the data into an HTML <table>."""
    skip_infer_table_types: Optional[List[str]] = Field(default=None)
    r"""The document types that you want to skip table extraction with. Default: ['pdf', 'jpg', 'png']"""
    split_pdf_page: Optional[bool] = Field(default=None)
    r"""Should the pdf file be split at client. Ignored on backend."""
    strategy: Optional[Literal["fast", "hi_res", "auto"]] = Field(default=None)
    r"""The strategy to use for partitioning PDF/image. Options are fast, hi_res, auto. Default: auto"""
    xml_keep_tags: Optional[bool] = Field(default=None)
    r"""If True, will retain the XML tags in the output. Otherwise it will simply extract the text from within the tags. Only applies to partition_xml."""


class PartitionResponseElementMetadata(BaseModel):
    filename: Optional[str]
    filetype: Optional[str]
    page_number: Optional[int] = None
    languages: Optional[List[str]] = []
    links: Optional[List[Any]] = None


class PartitionResponseElement(BaseModel):
    type: Optional[str]
    element_id: Optional[str]
    metadata: Optional[PartitionResponseElementMetadata]
    text: Optional[str]


class UnstructuredIO:

    def __init__(self, unstructured_api_key: str, unstructured_url: str):
        self.client = UnstructuredClient(
            api_key_auth=unstructured_api_key,
            server_url=unstructured_url
        )

    async def get_file_chunks(self, file: UploadFile, partition_parameters_params: PartitionParametersParams) -> List[str]:
        strings = []
        try:
            req = await self._build_PartitionRequest(file, partition_parameters_params)
            res: PartitionResponse | None = await self._get_PartitionResponse(req)
            elements = await self.get_file_partition_elements(res)

            for element in elements:
                strings.append(element.text)

            if partition_parameters_params.combine_under_n_chars == 0:
                # return full text if chunk_size is 0
                string = "".join(strings)
                return [string]
            else:
                return strings
        except Exception as e:
            logger.error(str(e))
        return strings

    async def _build_PartitionRequest(
            self, file: UploadFile, partition_parameters_params: PartitionParametersParams
    ) -> PartitionRequest:
        req = shared.PartitionParameters(
            # Note that this currently only supports a single file
            # files=file,
            files=shared.Files(
                content=await file.read(),
                file_name=file.filename,
            ),
            # Other partition params
            **partition_parameters_params.model_dump(exclude_none=True)
            # chunking_strategy="by_title",
            # combine_under_n_chars=chunk_size,
            # pdf_infer_table_structure=True,
            # hi_res_model_name=None,
            # strategy="hi_res",
        )
        req1 = PartitionRequest(
            partition_parameters=req,
        )
        return req1

    async def _get_PartitionResponse(
            self, req: PartitionRequest
    ) -> PartitionResponse | None:
        res: PartitionResponse | None = None
        try:
            res: PartitionResponse = self.client.general.partition(req)
        except SDKError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
        if not res or res.status_code != 200:
            logger.error(f"Error in extracting data from file {req.partition_parameters.files.file_name}")
        return res
        # res_str = ("\n\n".join([str(el) for el in res.elements]))

    async def get_file_partition_elements(self, partition_response: PartitionResponse | None) -> List[PartitionResponseElement]:
        elements = []
        for element_dict in partition_response.elements:
            try:
                element = PartitionResponseElement.model_validate(element_dict)
                elements.append(element)
            except ValidationError as e:
                logger.error(str(e))
            except Exception as e:
                logger.error(str(e))
        return elements


@lru_cache
def get_unstructured_io(settings: Settings = SettingsProvider.sget()) -> UnstructuredIO:
    return UnstructuredIO(
        unstructured_api_key=settings.UNSTRUCTURED_API_KEY,
        unstructured_url=settings.UNSTRUCTURED_URL,
    )
