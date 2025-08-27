import discord
from discord.ext import commands, tasks
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 123456789012345678))
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")
RTMP_CHECK_URL = os.getenv("RTMP_CHECK_URL")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

last_live_id = None

async def fetch_json(session, url):
    async with session.get(url, timeout=8) as response:
        return await response.json()

async def check_youtube_live(session):
    if not YOUTUBE_CHANNEL_ID:
        return None
    url = f"https://www.youtube.com/channel/{YOUTUBE_CHANNEL_ID}/live"
    async with session.get(url) as response:
        text = await response.text()
        if "isLiveNow" in text:
            return {"title": "YouTube Live!", "url": url, "thumb": None}
    return None

async def check_twitch_live(session):
    if not TWITCH_USERNAME:
        return None
    url = f"https://www.twitch.tv/{TWITCH_USERNAME}"
    async with session.get(url) as response:
        text = await response.text()
        if '"isLiveBroadcast":true' in text:
            return {"title": f"{TWITCH_USERNAME} is live!", "url": url, "thumb": None}
    return None

async def check_rtmp_live(session):
    if not RTMP_CHECK_URL:
        return None
    try:
        data = await fetch_json(session, RTMP_CHECK_URL)
        if data.get("live"):
            return {
                "title": data.get("title", "RTMP Live Stream"),
                "url": data.get("url", RTMP_CHECK_URL),
                "thumb": data.get("thumbnail")
            }
    except:
        return None
    return None

@tasks.loop(seconds=30)
async def live_checker():
    global last_live_id
    async with aiohttp.ClientSession() as session:
        youtube_live = await check_youtube_live(session)
        twitch_live = await check_twitch_live(session)
        rtmp_live = await check_rtmp_live(session)

        live = youtube_live or twitch_live or rtmp_live
        if live:
            stream_id = live["url"]
            if stream_id != last_live_id:
                last_live_id = stream_id
                channel = bot.get_channel(DISCORD_CHANNEL_ID)
                if channel:
                    embed = discord.Embed(
                        title=live["title"],
                        url=live["url"],
                        description="🔴 We are now LIVE! Click to watch.",
                        color=discord.Color.red()
                    )
                    if live.get("thumb"):
                        embed.set_image(url=live["thumb"])
                    await channel.send(embed=embed)

@bot.command()
async def announce(ctx, url: str, *, title: str = "We're Live!"):
    """Manually announce a live stream."""
    embed = discord.Embed(
        title=title,
        url=url,
        description="🔴 Live now!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    live_checker.start()

bot.run(DISCORD_TOKEN)