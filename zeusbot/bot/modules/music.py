from __future__ import annotations

from hikari import GuildVoiceChannel
from tanjun import (
    Component,
    as_slash_command,
    injected,
    with_channel_slash_option,
    with_str_slash_option,
    with_int_slash_option,
    with_bool_slash_option,
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


@music_component.with_slash_command
@as_slash_command("skip", "Skip the song")
async def skip_slash(
    ctx: SlashContext,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.skip(ctx)


@music_component.with_slash_command
@as_slash_command("now-playing", "Display the currently playing song")
async def now_playing_slash(
    ctx: SlashContext,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.now_playing(ctx)


@music_component.with_slash_command
@as_slash_command("shuffle", "Shuffle the queue.")
async def shuffle_slash(
    ctx: SlashContext,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.shuffle(ctx)


@music_component.with_slash_command
@with_bool_slash_option("status", "Status to set repeat mode")
@as_slash_command("repeat", "Set repeat mode")
async def repeat_slash(
    ctx: SlashContext,
    status: bool,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.repeat(ctx, status)


@music_component.with_slash_command
@with_int_slash_option("level", "Level of volume to set")
@as_slash_command("volume", "Set the volume")
async def volume_slash(
    ctx: SlashContext,
    level: int,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.volume(ctx, level)


@music_component.with_slash_command
@as_slash_command("queue", "Display the queue")
async def queue_slash(
    ctx: SlashContext,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.queue(ctx)


@music_component.with_slash_command
@with_int_slash_option("position", "The position to seek to")
@as_slash_command("seek", "Seek the current track")
async def seek_slash(
    ctx: SlashContext,
    position: int,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.seek(ctx, position)


@music_component.with_slash_command
@as_slash_command("pause", "Pause the playback.")
async def pause_slash(
    ctx: SlashContext,
    *,
    client: ZeusClient = injected(type=ZeusClient),
) -> None:
    await client.music.pause(ctx)
