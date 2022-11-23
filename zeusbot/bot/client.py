from __future__ import annotations

# from asyncio import sleep
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from hikari import (
    StartingEvent,
    StoppingEvent,
    VoiceServerUpdateEvent,
    VoiceStateUpdateEvent,
)
from tanjun import Client

from zeusbot.utils import Config, HikariUtility, MusicUtility

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Dict, Mapping, Self, Type

    from alluka.abc import Client as AllukaClient
    from hikari import (
        GatewayBotAware,
        PartialCommand,
        PartialGuild,
        ShardAware,
        SnowflakeishOr,
        SnowflakeishSequence,
    )
    from hikari.api import (
        Cache,
        EventManager,
        InteractionServer,
        RESTClient,
        VoiceComponent,
    )


class ZeusClient(Client):
    """"""

    __slots__ = (
        *Client.__slots__,
        "session",
    )
    music = MusicUtility()
    hikari = HikariUtility
    logger = getLogger(__name__)

    def __init__(
        self,
        rest: RESTClient,
        *,
        cache: Cache | None = None,
        events: EventManager | None = None,
        server: InteractionServer | None = None,
        shards: ShardAware | None = None,
        voice: VoiceComponent | None = None,
        event_managed: bool = False,
        injector: AllukaClient | None = None,
        mention_prefix: bool = False,
        set_global_commands: SnowflakeishOr[PartialGuild] | bool = False,
        declare_global_commands: SnowflakeishSequence[PartialGuild]
        | SnowflakeishOr[PartialGuild]
        | bool = False,
        command_ids: Mapping[str, SnowflakeishOr[PartialCommand]]
        | None = None,
        message_ids: Mapping[str, SnowflakeishOr[PartialCommand]]
        | None = None,
        user_ids: Mapping[str, SnowflakeishOr[PartialCommand]] | None = None,
        _stack_level: int = 0,
    ) -> None:
        super().__init__(
            rest,
            cache=cache,
            events=events,
            server=server,
            shards=shards,
            voice=voice,
            event_managed=event_managed,
            injector=injector,
            mention_prefix=mention_prefix,
            set_global_commands=set_global_commands,
            declare_global_commands=declare_global_commands,
            command_ids=command_ids,
            message_ids=message_ids,
            user_ids=user_ids,
            _stack_level=_stack_level,
        )
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        events: Dict[Type[Any], Callable[[Any], Coroutine[Any, Any, None]]] = {
            StartingEvent: self.starting_event,
            StoppingEvent: self.stopping_event,
            VoiceServerUpdateEvent: self.voice_server_update_event,
            VoiceStateUpdateEvent: self.voice_state_update_event,
        }

        if self.events is None:
            return

        for event_type, callback in events.items():
            self.events.subscribe(event_type, callback)

    @classmethod
    def from_gateway_bot(
        cls,
        bot: GatewayBotAware,
        /,
        *,
        event_managed: bool = True,
        injector: AllukaClient | None = None,
        mention_prefix: bool = True,
        declare_global_commands: SnowflakeishSequence[PartialGuild]
        | SnowflakeishOr[PartialGuild]
        | bool = Config.HOME_GUILD_IDS,
        set_global_commands: SnowflakeishOr[PartialGuild] | bool = False,
        command_ids: Mapping[str, SnowflakeishOr[PartialCommand]]
        | None = None,
        message_ids: Mapping[str, SnowflakeishOr[PartialCommand]]
        | None = None,
        user_ids: Mapping[str, SnowflakeishOr[PartialCommand]] | None = None,
    ) -> Self:  # type: ignore
        return (
            cls(  # type: ignore
                rest=bot.rest,
                cache=bot.cache,
                events=bot.event_manager,
                shards=bot,
                voice=bot.voice,
                event_managed=event_managed,
                injector=injector,
                mention_prefix=mention_prefix,
                declare_global_commands=declare_global_commands,
                set_global_commands=set_global_commands,
                command_ids=command_ids,
                message_ids=message_ids,
                user_ids=user_ids,
                _stack_level=1,
            )
            .set_human_only()
            .set_hikari_trait_injectors(bot)
        )

    async def starting_event(self, _: StartingEvent) -> None:
        if self.shards is None or self.loop is None:
            return

        # if (me := self.shards.get_me()) is None:
        #     return

        await self.music.connect()

    async def stopping_event(self, _: StoppingEvent) -> None:
        if self.shards is None or self.loop is None:
            return

    async def voice_state_update_event(
        self,
        event: VoiceStateUpdateEvent,
    ) -> None:
        await self.music.raw_voice_state_update(
            event.guild_id,
            event.state.user_id,
            event.state.session_id,
            event.state.channel_id,
        )

    async def voice_server_update_event(
        self,
        event: VoiceServerUpdateEvent,
    ) -> None:
        await self.music.raw_voice_server_update(
            event.guild_id,
            event.endpoint or "",
            event.token,
        )

    def load_modules(self, *modules: str | Path) -> Self:  # type: ignore
        if modules:
            return super().load_modules(*modules)

        return super().load_modules(
            *(Path(__file__).parent / "modules").glob("*.py"),
        )

    def unload_modules(self, *modules: str | Path) -> Self:  # type: ignore
        if modules:
            return super().unload_modules(*modules)

        return super().unload_modules(
            *(Path(__file__).parent / "modules").glob("*.py"),
        )

    def reload_modules(self, *modules: str | Path) -> Self:  # type: ignore
        if modules:
            return super().reload_modules(*modules)

        return super().reload_modules(
            *(Path(__file__).parent / "modules").glob("/*.py"),
        )
