# /// script
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "httpx",
#   "pydantic",
#   "loguru",
#   "tenacity",
#   "tqdm",
#   "anyio",
# ]
# ///

import os
import httpx
import uvicorn
import secrets
import itertools
import anyio
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from pydantic import BaseModel
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log
from tqdm import tqdm

# --- CONFIGURATION ---
PIXELDRAIN_API_KEY = "5f45f184-64bb-4eaa-be19-4a5f0459db49"
WEBHOOK_SECRET_KEY = "my_super_secret_webhook_key_123"
PORT = 5000

# --- PATH MARKERS ---
DOCKER_REC_MARKER = "/app/rec"
DOCKER_BASE = "/app"

# --- LOGGING CONFIG ---
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    f"{LOG_DIR}/uploader_{{time:YYYY-MM-DD}}.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="DEBUG",
    enqueue=True,
)

# --- RETRY SETTINGS ---
MAX_RETRIES = 3
RETRY_DELAY = 10

bar_position = itertools.count()

# --- UTILS ---

class UploadProgressGenerator:
    """An async iterator that yields chunks and updates tqdm for httpx 'content'."""

    def __init__(self, file_path, pbar):
        self.file_path = file_path
        self.pbar = pbar

    async def __aiter__(self):
        # anyio provides asynchronous file access compatible with httpx streaming
        async with await anyio.open_file(self.file_path, "rb") as f:
            while True:
                chunk = await f.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                self.pbar.update(len(chunk))
                yield chunk


# --- CORE LOGIC ---

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_fixed(RETRY_DELAY),
    before_sleep=before_sleep_log(logger, "DEBUG"),
    reraise=True,
)
async def execute_upload(file_path: str, filename: str, position: int):
    file_size = os.path.getsize(file_path)

    url = f"https://pixeldrain.com/api/file/{filename}"

    pbar = tqdm(
        total=file_size,
        unit="B",
        unit_scale=True,
        desc=f"🚀 {filename}",
        position=position,
        leave=False,
    )

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            # Create the async generator for the request body
            upload_gen = UploadProgressGenerator(file_path, pbar)

            # PUT with 'content' as an async iterable is the most stable stream method
            response = await client.put(
                url, auth=("", PIXELDRAIN_API_KEY), content=upload_gen
            )

            if response.status_code not in [200, 201]:
                logger.error(f"Server rejected PUT: {response.text}")
                raise Exception(f"Pixeldrain Error {response.status_code}")

            return response.json().get("id")
    finally:
        pbar.close()


async def process_and_upload(incoming_path: str):
    if incoming_path.startswith(DOCKER_REC_MARKER):
        rel_path = os.path.relpath(incoming_path, DOCKER_BASE)
        real_path = os.path.abspath(os.path.join(os.getcwd(), rel_path))
    else:
        real_path = incoming_path

    if not os.path.exists(real_path):
        logger.error(f"File not found: {real_path}")
        return

    filename = os.path.basename(real_path)
    pos = next(bar_position)

    try:
        logger.info(f"Stream Upload Started: {filename}")
        file_id = await execute_upload(real_path, filename, pos)
        logger.success(f"SUCCESS: {filename} -> https://pixeldrain.com/u/{file_id}")
    except Exception as e:
        logger.error(f"Failed to upload {filename} after {MAX_RETRIES} attempts.")
        logger.exception(e)


# --- WEB SERVER ---

app = FastAPI()


class OneLiveRecWebhook(BaseModel):
    id: str
    ts: str
    type: str
    data: Dict[str, Any]


@app.post("/webhook")
async def handle_webhook(
    payload: OneLiveRecWebhook, background_tasks: BackgroundTasks, key: str = Query(...)
):
    if not secrets.compare_digest(key, WEBHOOK_SECRET_KEY):
        raise HTTPException(status_code=403, detail="Forbidden")

    logger.debug(
        f"Received {payload.type} from {payload.data.get('platform')}-{payload.data.get('channel')}"
    )

    if payload.type == "video_transmux_finish":
        file_path = payload.data.get("output")
        if file_path:
            logger.info(f"Webhook Received: {os.path.basename(file_path)}")
            background_tasks.add_task(process_and_upload, file_path)
            return {"status": "success"}

    return {"status": "ignored"}


if __name__ == "__main__":
    logger.info(f"Uploader running at {os.getcwd()}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
