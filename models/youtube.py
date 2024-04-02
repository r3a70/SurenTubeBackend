from pydantic import BaseModel
from pydantic.types import Union, List, UUID4


class Formats(BaseModel):

    filesize: Union[int, None]
    format_id: str
    format_note: str
    height: Union[int, None]
    width: Union[int, None]
    url: Union[str, None]
    ext: str
    resolution: Union[str, None]
    video_ext: Union[str, None]
    audio_ext: Union[str, None]
    format: str
    type: str
    need_audio: bool


class ExtractedFormats(BaseModel):

    id: Union[str, None]
    best_audio_format_id: Union[str, None]
    title: Union[str, None]
    thumbnail: Union[str, None]
    description: Union[str, None]
    duration: Union[int, None]
    view_count: Union[int, None]
    comment_count: Union[int, None]
    formats: Union[List[Formats], None]


class FindFormatsReponse(BaseModel):

    success: bool
    message: str
    result: Union[ExtractedFormats, None]


class Download(BaseModel):

    url: str
    format_id: str


class DownloadExtra(BaseModel):

    uuid: UUID4


class DownloadResponse(BaseModel):

    success: bool
    message: str
    result: Union[DownloadExtra, None]


class ProgressBarResponse(BaseModel):

    status: Union[str, None]
    total_bytes: Union[int, str, None]
    downloaded_bytes: Union[int, str, None]
    eta: Union[int, str, None]
    speed: Union[float, None]
    elapsed: Union[float, None]
    eta_str: Union[str, None]
    speed_str: Union[str, None]
    total_bytes_str: Union[str, None]
    elapsed_str: Union[str, None]
    percent_str: Union[str, None]
    download_url: Union[str, None]
