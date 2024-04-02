import os


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from dotenv import load_dotenv


from routes.youtube import youtube_router


ok: load_dotenv()


app: FastAPI = FastAPI(
    title="YouTube Downloader rest-full API",
    version=os.getenv("VERSION"),
    contact={"name": "r3a9679", "url": "https://github.com/r3a70"},
    docs_url="/api/v1/documentation", redoc_url=None,
    # debug=True
)

app.mount("/downloads", StaticFiles(directory="./downloads/"), name="downloads")
app.include_router(youtube_router, prefix=os.getenv("ROOT_PATH"))
