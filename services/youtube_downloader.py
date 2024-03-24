from datetime import datetime
from threading import Thread
from queue import Queue
from uuid import uuid4
import json


from pymongo.results import InsertOneResult


from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError


from databases.redis import redis_db as redis
from databases.mongodb import mongo_db as mongodb
from utils.helper import remove_color_tags


class YouTubeDownloaderThread(Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):

        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.target(*self.args)
        except (DownloadError, ExtractorError) as e:
            redis.set(
                name=self.kwargs['uuid'],
                value=remove_color_tags(str(e))
            )
            self.kwargs['queue'].put(False)


def download_from_youtube(
    *, url: str, format_id: str, uuid: str, ext: str = "",
    audio_format_id: str = "", need_audio: bool = False
) -> tuple[bool, str]:

    if mongodb.test.find_one({"uuid": uuid}):

        # return False, "uuid is duplicate"
        pass

    name: str = f"{str(uuid4())}"
    queue: Queue = Queue()

    if ext == "mp3":

        ytdl: YoutubeDL = YoutubeDL(
            {
                "format": "bestaudio/best",
                "progress_hooks": [
                    lambda d: progress_bar(d, uuid, queue, f"{name}.{ext}")
                ],
                "outtmpl": f"./downloads/{name}",
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': ext,
                    'preferredquality': "320" if audio_format_id == "1000" else "192"
                }]
            }
        )

    else:

        final_format_id: str = format_id if not need_audio else f"{format_id}+{audio_format_id}"
        ytdl: YoutubeDL = YoutubeDL(
            {
                "format": final_format_id,
                "progress_hooks": [lambda d: progress_bar(d, uuid, queue, f"{name}.{ext}")],
                "outtmpl": f"./downloads/{name}.{ext}",
                "merge_output_format": ext
            }
        )

    t1: YouTubeDownloaderThread = YouTubeDownloaderThread(
        target=ytdl.download, args=([url],), kwargs={
            "uuid": uuid, "queue": queue
        }
    )
    t1.start()

    status: bool = queue.get()
    if status:

        _: InsertOneResult = mongodb.test.insert_one(
            {
                "uuid": uuid,
                "create_at": datetime.utcnow()
            }
        )

    return status, "file will be downloaded as soon as possible"


def progress_bar(d, uuid: str, queue: Queue, name: str) -> None:

    queue.put(True)

    if d['status'] == "downloading":

        redis.set(
            name=uuid,
            value=json.dumps(
                {
                    "status": d['status'],
                    "total_bytes": d['total_bytes'],
                    "downloaded_bytes": d['downloaded_bytes'],
                    "eta": d['eta'],
                    "speed": d['speed'],
                    "elapsed": d['elapsed'],
                    "eta_str": remove_color_tags(input_str=d['_eta_str']),
                    "speed_str": remove_color_tags(input_str=d['_speed_str']),
                    "total_bytes_str": remove_color_tags(input_str=d['_total_bytes_str']),
                    "elapsed_str": remove_color_tags(input_str=d['_elapsed_str']),
                    "percent_str": remove_color_tags(input_str=d['_percent_str'])
                }
            )
        )

    else:
        redis.set(
            name=uuid,
            value=json.dumps(
                {
                    "status": d['status'],
                    "total_bytes": d['total_bytes'],
                    "downloaded_bytes": d['downloaded_bytes'],
                    "eta": 0,
                    "speed": d['speed'],
                    "elapsed": d['elapsed'],
                    "eta_str": "00:00",
                    "speed_str": remove_color_tags(input_str=d['_speed_str']),
                    "total_bytes_str": remove_color_tags(input_str=d['_total_bytes_str']),
                    "elapsed_str": remove_color_tags(input_str=d['_elapsed_str']),
                    "percent_str": remove_color_tags(input_str=d['_percent_str'])
                }
            )
        )

        redis.json().set(
            name=f"upload:{uuid}",
            path=".",
            obj={}
        )
