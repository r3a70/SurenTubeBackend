import json
from datetime import timedelta
import logging
import os
import random


from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from redis.exceptions import ConnectionError, AuthenticationError


from databases.redis import redis_db as redis
from utils.helper import extract_url_short_code


def extract_formats(*, url: str) -> list[dict] | None:

    try:
        short_code: str = extract_url_short_code(url=url)
        proxy: str = random.choice(os.getenv("PROXIES").split(","))

        if redis.get(short_code):
            formats: list[dict] = json.loads(redis.get(short_code))

        else:
            ytdl: YoutubeDL = YoutubeDL(
                {
                    "noplaylist": True,
                    "proxy": proxy
                }
            )
            formats: list[dict] = ytdl.extract_info(url=url, download=False)
            redis.set(short_code, json.dumps(formats), ex=timedelta(days=1))

    except (DownloadError, ConnectionError, AuthenticationError) as error:
        logging.error(error)
        formats = {}

    available_formats: dict = {
        "formats": []
    }

    best_audio_size, best_audio_format_id = 0, "0"

    for _format in formats['formats']:

        if (
            'filesize' in _format.keys() and _format.get("filesize")
            is not None and _format["vcodec"][0:7] != "av01.0."
        ):

            if _format.get('audio_ext') == 'none':

                if _format.get("ext") == "webm":

                    _format.update({"ext": "mkv", "video_ext": "mkv"})

                _format.update(
                    {
                        'filesize': _format["filesize"] + best_audio_size + 100 
                        if _format["acodec"] == "none" else _format["filesize"],
                        'type': "video",
                        "need_audio": _format["acodec"] == "none"
                    }
                )

                available_formats.get("formats").append(_format)

            elif _format.get('audio_ext') != 'none':

                best_audio_format_id = _format["format_id"]
                best_audio_size = _format['filesize']

                if _format.get("audio_ext") == "webm":

                    _format.update({"ext": "opus", "audio_ext": "opus"})

                _format.update({'type': 'audio', "need_audio": False})

                available_formats.get("formats").append(_format)

    for _format in ["mp3 medium", "mp3 best"]:

        format_id: str = "1000" if _format == "mp3 best" else "2000"
        available_formats.get("formats").append(
            {
                "filesize": best_audio_size * 2
                if _format == "mp3 medium" else best_audio_size * 3,
                "format_id": format_id,
                "format_note": f"{_format}",
                "width": None,
                "height": None,
                "url": None,
                "ext": "mp3",
                "resolution": None,
                "video_ext": None,
                "audio_ext": "mp3",
                "format": f"{format_id} {_format}",
                "type": "audio",
                "need_audio": False
            }
        )

    available_formats.update(
        {
            "id": formats['id'],
            "best_audio_format_id": best_audio_format_id,
            "title": formats['title'],
            "thumbnail": formats['thumbnail'],
            "description": formats['description'],
            "duration": formats['duration'],
            "view_count": formats['view_count'],
            "comment_count": formats['comment_count']
        }
    )

    return available_formats or None
