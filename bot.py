import logging
import os


from pyrogram import Client
# from apscheduler.schedulers.asyncio import AsyncIOScheduler


from dotenv import load_dotenv


ok: load_dotenv()


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.INFO)

app: Client = Client(
    name="youtubedl-api",
    api_id=os.getenv("TELEGRAM_BOT_API_ID"),
    api_hash=os.getenv("TELEGRAM_BOT_API_HASH"),
    bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
    workers=int(os.getenv("MAX_WORKERS")),
    max_concurrent_transmissions=int(os.getenv("MAX_WORKERS")) // 2
)

# scheduler: AsyncIOScheduler = AsyncIOScheduler()
# scheduler.add_job(
#     run_upload_to_telegram_jobs, "interval", minutes=1, kwargs={"bot": app}
# )

if __name__ == "__main__":

    # scheduler.start()
    app.run()
