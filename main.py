import asyncio
import os
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from twikit import Client
from dotenv import load_dotenv

load_dotenv()

# -----------------------
# Config
# -----------------------

DOWNLOAD_FOLDER = "images"

USERNAME = os.getenv("USERNAME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

client = Client(
    language="en-US",
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
)

app = FastAPI()

# -----------------------
# Login once on startup
# -----------------------

@app.on_event("startup")
async def startup_event():
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD,
        cookies_file="cookies.json"
    )
    print("Logged in successfully")


# -----------------------
# Request Model
# -----------------------

class TweetRequest(BaseModel):
    tweet_id: str


# -----------------------
# Image Fetch Function
# -----------------------

async def fetchImageById(tid: str):
    tweet = await client.get_tweet_by_id(tid)

    if not tweet.media:
        return []

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    image_urls = []

    async with aiohttp.ClientSession() as session:
        for index, media in enumerate(tweet.media):

            if media.type == "photo":
                url = media.media_url

                if "?format=" in url:
                    url = url.split("?")[0] + "?name=orig"

                filepath = os.path.join(
                    DOWNLOAD_FOLDER,
                    f"{tid}_{index}.jpg"
                )

                async with session.get(url) as response:
                    if response.status == 200:
                        with open(filepath, "wb") as f:
                            f.write(await response.read())

                        image_urls.append({
                            "url": url,
                            "saved_as": filepath
                        })

    return image_urls


# -----------------------
# API Endpoint
# -----------------------

@app.post("/fetch-images")
async def fetch_images(data: TweetRequest):
    try:
        images = await fetchImageById(data.tweet_id)

        return {
            "tweet_id": data.tweet_id,
            "image_count": len(images),
            "images": images
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))