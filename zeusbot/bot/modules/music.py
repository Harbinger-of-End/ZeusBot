from __future__ import annotations

from hikari import GuildVoiceChannel
from tanjun import (
    Component,
    as_slash_command,
    injected,
    with_channel_slash_option,
    with_str_slash_option,
)
from tanjun.abc import SlashContext

from zeusbot.bot.client import ZeusClient

music_component = Component(name="music")
loader = music_component.make_loader()


@music_component.with_slash_command
@with_str_slash_option("query", "A song, or a link", default=None)
@as_slash_command("play", "Play a song/Resume playback")
async def play_slash(
    ctx: SlashContext,
    query: str | None = None,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.play(ctx, query)


@music_component.with_slash_command
@with_channel_slash_option(
    "channel",
    "The channel to join in",
    types=[GuildVoiceChannel],
    default=None,  # type: ignore
)
@as_slash_command("connect", "Connect to a voice channel")
async def connect_slash(
    ctx: SlashContext,
    channel: GuildVoiceChannel | None = None,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.join_voice(ctx, channel)


@music_component.with_slash_command
@as_slash_command("disconnect", "Disconnect from the current voice channel")
async def disconnect_slash(
    ctx: SlashContext,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.disconnect(ctx)


@music_component.with_slash_command
@as_slash_command("stop", "Stop the current playback")
async def stop_slash(
    ctx: SlashContext,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.stop(ctx)
