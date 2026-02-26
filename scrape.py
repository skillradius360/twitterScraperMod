import asyncio
from twikit import Client
from dotenv import load_dotenv
import os
import aiohttp
import re


load_dotenv()

DOWNLOAD_FOLDER = "images" # constants


USERNAME = os.getenv("USERNAME")
EMAIL = os.getenv("USERNAME")
PASSWORD = os.getenv("USERNAME")

client = Client(
    language="en-US",
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
)
async def make_auth():

    await client.login(
                auth_info_1=USERNAME,   
                auth_info_2=EMAIL,      
                password=PASSWORD,
                cookies_file="cookies.json" 
            )
    

async def fetchByGenre():
    try:
        print("Logging in...")

        await asyncio.sleep(3)  # small delay helps sometimes

        await client.login(
            auth_info_1=USERNAME,   # username
            auth_info_2=EMAIL,      # email
            password=PASSWORD,
            cookies_file="cookies.json"  # saves session cookies
        )

        print("Login successful ✅")

        print("Searching tweets...\n")

        tweets = await client.search_tweet("python", "Latest")

        for tweet in tweets:
            print("User:", tweet.user.name)
            print("Text:", tweet.text)
            print("Date:", tweet.created_at)
            print("-" * 50)

    except Exception as e:
        print("Error occurred:")
        print(e)


async def fetchById(tid):
    try:

        tweet_id = tid
        tweet = await client.get_tweet_by_id(tweet_id)

        print("User:", tweet.user.name)
        print("Text:", tweet.text)
        print("Date:", tweet.created_at)
        

        if tweet.media:
            print("\n--- Images ---\n")

            for media in tweet.media:
                if media.type == "photo":
                    print("Image URL:", media.media_url)

        else:
            print("No images found in this tweet.")

    except Exception as e:
        print(e)
        

async def findComments():
    
    tweet_id = "2026732499997704513"
    try:
        tweet = await client.get_tweet_by_id(tweet_id)

        print("\n--- Original Tweet ---")
        print(tweet.text)
        print("\n--- Replies ---\n")

        replies = await client.search_tweet(
            f"conversation_id:{tweet_id}",
            "Latest"
        )

        for reply in replies:
        
            if reply.id != tweet_id:
                print("User:", reply.user.name)
                print("Reply: ", reply.text)
                print("Date:", reply.created_at)
                print("-" * 50)
    except Exception as e:
        print(e)


async def fetchImageById(tid):

    try:
        tweet = await client.get_tweet_by_id(tid)

        print("User:", tweet.user.name)
        print("Text:", tweet.text)
        print("Date:", tweet.created_at)

        if not tweet.media:
            print("No images found in this tweet.")
            return None

        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

        image_urls = []

        async with aiohttp.ClientSession() as session:
            for index, media in enumerate(tweet.media):

                if media.type == "photo":
                    url = media.media_url

                    # Get highest quality version
                    # if "?format=" in url:
                    #     url = url.split("?")[0] + "?name=orig"

                    filepath = os.path.join(
                        DOWNLOAD_FOLDER,
                        f"{tid}_{index}.jpg"
                    )

                    async with session.get(url) as response:
                        if response.status == 200:
                            with open(filepath, "wb") as f:
                                f.write(await response.read())
                            print(f"Saved: {filepath}")
                            image_urls.append(url)
                        else:
                            print(f"Failed: {url}")

        return image_urls

    except Exception as e:
        print("Error:", e)
        return None



def extract_tweet_id(url_or_id: str) -> str:

    url_or_id = url_or_id.strip()

    if url_or_id.isdigit():
        return url_or_id

    match = re.search(r"/status/(\d+)", url_or_id)
    if match:
        return match.group(1)

    raise ValueError("Invalid tweet URL or ID")



async def main():
    await make_auth()
    data =  extract_tweet_id("https://x.com/Prof_Cheems/status/2026893332408852932/")
    await fetchImageById(data)
    # print(data)
    # await download_image(data,"img.jpg")
    # await findComments()


asyncio.run(main())