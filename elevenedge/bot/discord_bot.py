from __future__ import annotations

import os
from pathlib import Path

import discord
import requests
from discord import app_commands
from discord.ext import commands

API_BASE_URL = os.getenv('ELEVENEDGE_API_BASE_URL', 'http://localhost:8000')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


class ElevenEdgeBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self) -> None:
        await self.tree.sync()


bot = ElevenEdgeBot()


@bot.tree.command(name='upload', description='Upload a video file to ElevenEdge')
@app_commands.describe(video='Video attachment')
async def upload(interaction: discord.Interaction, video: discord.Attachment) -> None:
    await interaction.response.defer(thinking=True)
    local_path = Path('/tmp') / video.filename
    await video.save(local_path)

    with local_path.open('rb') as stream:
        response = requests.post(
            f'{API_BASE_URL}/videos/upload',
            files={'video': (video.filename, stream, 'video/mp4')},
            timeout=120,
        )

    if response.ok:
        payload = response.json()
        await interaction.followup.send(
            f"Video received. ID={payload['video_id']} status={payload['status']}"
        )
    else:
        await interaction.followup.send(f'Upload failed: {response.text}')


@bot.tree.command(name='search', description='Search transcript for a phrase')
@app_commands.describe(video_id='Video ID', query='Search text')
async def search(interaction: discord.Interaction, video_id: int, query: str) -> None:
    await interaction.response.defer(thinking=True)
    response = requests.post(
        f'{API_BASE_URL}/search/videos/{video_id}',
        json={'query': query, 'limit': 5},
        timeout=30,
    )
    if not response.ok:
        await interaction.followup.send(f'Search failed: {response.text}')
        return

    matches = response.json().get('matches', [])
    if not matches:
        await interaction.followup.send('No matches found.')
        return

    message = '\n'.join([f"{m['timestamp']} - {m['text']}" for m in matches])
    await interaction.followup.send(message)


@bot.tree.command(name='clip', description='Generate a clip from transcript timestamps')
@app_commands.describe(video_id='Video ID', start='Segment start', end='Segment end')
async def clip(interaction: discord.Interaction, video_id: int, start: float, end: float) -> None:
    await interaction.response.defer(thinking=True)
    response = requests.post(
        f'{API_BASE_URL}/clips/videos/{video_id}',
        json={'start': start, 'end': end, 'pre_roll_seconds': 5, 'post_roll_seconds': 5},
        timeout=120,
    )
    if not response.ok:
        await interaction.followup.send(f'Clip creation failed: {response.text}')
        return

    clip_path = response.json()['clip_path']
    await interaction.followup.send(file=discord.File(clip_path))


if __name__ == '__main__':
    if not DISCORD_TOKEN:
        raise RuntimeError('DISCORD_TOKEN env var is required')
    bot.run(DISCORD_TOKEN)
