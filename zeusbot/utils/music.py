from __future__ import annotations

from asyncio import get_event_loop
from typing import TYPE_CHECKING

from hikari import Snowflake
from lavaplayer import Lavalink, PlayList, TrackLoadFailed  # type: ignore

from . import Config, HikariUtility

if TYPE_CHECKING:
    from typing import Final

    from hikari import GuildVoiceChannel, SnowflakeishOr
    from tanjun.abc import Context


class MusicUtility:
    """The utility store for music-related operations."""

    __slots__ = ("_lavalink",)

    def __init__(self) -> None:
        self._lavalink = Lavalink(
            host=Config.LAVALINK_HOST,
            port=Config.LAVALINK_PORT,
            password=Config.LAVALINK_PASSWORD,
            user_id=Config.BOT_ID,
        )

    async def connect(self) -> None:
        self._lavalink.set_event_loop(get_event_loop())
        self._lavalink.connect()

    async def raw_voice_state_update(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        session_id: str,
        channel_id: Snowflake | None,
    ) -> None:
        await self._lavalink.raw_voice_state_update(
            guild_id,
            user_id,
            session_id,
            channel_id,
        )

    async def raw_voice_server_update(
        self,
        guild_id: Snowflake,
        endpoint: str,
        token: str,
    ) -> None:
        await self._lavalink.raw_voice_server_update(
            guild_id,
            endpoint,
            token,
        )

    async def join_voice(
        self,
        ctx: Context,
        voice_channel: SnowflakeishOr[GuildVoiceChannel] | None = None,
    ) -> None:
        """Join a voice channel."""

        if ctx.guild_id is None:
            await ctx.respond("Cannot use music component in DMs.")
            return

        if ctx.client.cache is None or ctx.client.shards is None:
            await ctx.respond("Internal error")
            return

        states = ctx.client.cache.get_voice_states_view_for_guild(
            ctx.guild_id,
        )
        voice_state = states.get(ctx.author.id)

        if not voice_state:
            if voice_channel:
                await ctx.client.shards.update_voice_state(
                    ctx.guild_id,
                    voice_channel,
                    self_deaf=True,
                )
                await self._lavalink.wait_for_connection(ctx.guild_id)
                mention = (
                    f"<#{voice_channel}>"
                    if isinstance(voice_channel, (Snowflake, int))
                    else voice_channel.mention
                )
                await ctx.respond(f"Connected to {mention}")
                return

            await ctx.respond(
                "You are not connected to a voice channel, "
                "and have not given a voice channel to connect to",
            )
            return

        await ctx.client.shards.update_voice_state(
            ctx.guild_id,
            voice_state.channel_id,
            self_deaf=True,
        )
        await self._lavalink.wait_for_connection(ctx.guild_id)
        await ctx.respond(f"Connected to <#{voice_state.channel_id}>")

    async def play(self, ctx: Context, song: str | None = None) -> None:
        """Play a song and/or add it to queue."""

        if ctx.guild_id is None:
            await ctx.respond("Cannot use music component in DMs.")
            return

        if ctx.client.cache is None or ctx.client.shards is None:
            return

        if not ctx.client.cache.get_voice_state(
            ctx.guild_id,
            ctx.client.shards.get_me().id,  # type: ignore
        ):
            await self.join_voice(ctx)
            return

        if song is None:
            await self._lavalink.pause(ctx.guild_id, False)
            return

        result = await self._lavalink.auto_search_tracks(song)

        if not result:
            await ctx.respond("Error")
            return

        if isinstance(result, TrackLoadFailed):
            await ctx.respond("Track unable to be loaded.")
            return

        if isinstance(result, PlayList):
            await self._lavalink.add_to_queue(
                ctx.guild_id,
                result.tracks,
                ctx.author.id,
            )
            await ctx.respond(f"Added {len(result.tracks)} to queue.")
            return

        await self._lavalink.play(
            ctx.guild_id,
            result[0],
            ctx.author.id,
        )
        await ctx.respond(f"Added {result[0].title} to queue.")

    async def stop(self, ctx: Context) -> None:
        """Stop the queue."""

        if ctx.guild_id is None:
            return

        await self._lavalink.stop(ctx.guild_id)
        await ctx.respond("Stopped playing.")

    async def disconnect(self, ctx: Context) -> None:
        """Disconnect from the voice channel."""

        if ctx.guild_id is None or ctx.client.shards is None:
            return

        await ctx.client.shards.update_voice_state(ctx.guild_id, None)
        await self._lavalink.wait_for_remove_connection(ctx.guild_id)
        await ctx.respond("Disconnected")

    async def skip(self, ctx: Context) -> None:
        """Skip to the next song."""

        if ctx.guild_id is None:
            return

        if not await self._lavalink.get_guild_node(ctx.guild_id):
            await ctx.respond("Node not available, so I can't skip.")
            return

        await self._lavalink.skip(ctx.guild_id)

    async def now_playing(self, ctx: Context) -> None:
        """Display the currently playing song."""

        if ctx.guild_id is None:
            return

        if (
            not (node := await self._lavalink.get_guild_node(ctx.guild_id))
            or not node.queue
        ):
            return

        fields = [
            ("Title", f"[{node.queue[0].title}]({node.queue[0].uri})", True),
            (
                "Position",
                f"{node.queue[0].position}/{node.queue[0].length}",
                True,
            ),
        ]

        embed = HikariUtility.build_embed(
            title="Now playing",
            fields=fields,
        )

        await ctx.respond(embed=embed)

    async def shuffle(self, ctx: Context) -> None:
        """Shuffle the queue."""

        if ctx.guild_id is None:
            return

        await self._lavalink.shuffle(ctx.guild_id)  # type: ignore
        await ctx.respond("Queue shuffled.")

    async def repeat(self, ctx: Context, status: bool) -> None:
        """Repeat song."""

        if ctx.guild_id is None:
            return

        await self._lavalink.repeat(ctx.guild_id, status)
        await ctx.respond("Repeating every song.")

    async def volume(self, ctx: Context, volume: int) -> None:
        """Set the volume."""

        if ctx.guild_id is None:
            return

        await self._lavalink.volume(ctx.guild_id, volume)
        await ctx.respond(f"Set volume to {volume}")

    async def queue(self, ctx: Context) -> None:
        """Show the queue."""

        if ctx.guild_id is None:
            return

        if (
            not (node := await self._lavalink.get_guild_node(ctx.guild_id))
            or not node.queue
        ):
            await ctx.respond("Error.")
            return

        embed = HikariUtility.build_embed(
            title="Queue",
            description="\n".join(
                f"{i + 1}. {track.title}"
                for i, track in enumerate(node.queue[:10])
            ),
            footer=(
                f"Requested by: {ctx.author.username}",
                HikariUtility.get_avatar_of_member(ctx.author),
            ),
        )
        await ctx.respond(embed=embed)

    async def seek(self, ctx: Context, position: int) -> None:
        """Set the position of the track."""

        if ctx.guild_id is None:
            return

        await self._lavalink.seek(ctx.guild_id, position)
        await ctx.respond("Seeked.")

    async def pause(self, ctx: Context) -> None:
        """Pasuse the playback."""

        if ctx.guild_id is None:
            return

        await self._lavalink.pause(ctx.guild_id, True)


__all__: Final = ("MusicUtility",)
