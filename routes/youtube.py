from typing import Any
import json
from uuid import uuid4


from fastapi import APIRouter, Query, status, Response


from models.youtube import Download, FindFormatsReponse, DownloadResponse, \
    DownloadExtra, ProgressBarResponse
from services import youtube_format_extractor
from services import youtube_downloader
from utils.helper import find_chosed_formats
from databases.redis import redis_db as redis
from enums.regex import Regex


youtube_router = APIRouter()


@youtube_router.get("/youtube", response_model=FindFormatsReponse)
def extract_formats(response: Response, url: str = Query(regex=Regex.YOUTUBE.value)) -> Any:

    extracted_formats: dict | None = youtube_format_extractor.extract_formats(url=url)
    result = FindFormatsReponse(
        success=extracted_formats is not None,
        message="data extracted successfully" if extracted_formats else "error happend",
        result=extracted_formats
    )
    response.status_code = status.HTTP_200_OK if extracted_formats else status.HTTP_400_BAD_REQUEST

    return result


@youtube_router.post("/youtube", response_model=DownloadResponse)
def download_from_youtube(response: Response, download: Download) -> Any:

    extracted_formats: list[dict] | None = youtube_format_extractor.extract_formats(
        url=download.url
    )
    format_id, ext, need_audio = find_chosed_formats(
        formats=extracted_formats, format_id=download.format_id
    )

    uuid: uuid4 = str(uuid4())
    if all([format_id, ext]):

        success, message = youtube_downloader.download_from_youtube(
            url=download.url,
            format_id=format_id,
            uuid=uuid,
            ext=ext,
            audio_format_id=extracted_formats["best_audio_format_id"],
            need_audio=need_audio
        )

    else:

        success = False
        message = "Provided format_id does not exists"

    response.status_code = status.HTTP_201_CREATED if success else status.HTTP_400_BAD_REQUEST
    return {
        "success": success,
        "message": message,
        "result": DownloadExtra(**download.dict(), uuid=uuid) if success else None
    }


@youtube_router.trace("/youtube", response_model=ProgressBarResponse)
def show_progress(
        response: Response,
        uuid: str = Query(min_length=16, max_length=64)
) -> Any:

    if redis.get(name=uuid):

        result = json.loads(redis.get(name=uuid))
        response.status_code = status.HTTP_200_OK

    else:
        result = {
            "status": None,
            "total_bytes": 0,
            "downloaded_bytes": 0,
            "eta": 0,
            "speed": 0,
            "elapsed": 0,
            "eta_str": "00:00",
            "speed_str": "0",
            "total_bytes_str": "0",
            "elapsed_str": "0",
            "percent_str": "0",
            "download_url": None
        }
        response.status_code = status.HTTP_404_NOT_FOUND

    return ProgressBarResponse(**result)
