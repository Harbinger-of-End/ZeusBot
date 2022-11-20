from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from hikari import (
    Activity,
    ActivityType,
    GatewayBot,
    Intents,
    StartingEvent,
    Status,
    StoppingEvent,
)

from zeusbot.bot.client import ZeusClient
from zeusbot.utils import Config

if TYPE_CHECKING:
    from concurrent.futures import Executor
    from datetime import datetime
    from typing import Any, Callable, Coroutine, Dict, Final, Sequence, Type

    from hikari.impl import CacheSettings, HTTPSettings, ProxySettings


class ZeusBot(GatewayBot):
    """The client that connects to the Discord gateway."""

    __slots__ = (
        *GatewayBot.__slots__,
        "client",
    )
    logger = getLogger(__name__)

    def __init__(
        self,
        token: str = Config.TOKEN,
        *,
        allow_color: bool = True,
        banner: str | None = None,
        executor: Executor | None = None,
        force_color: bool = False,
        cache_settings: CacheSettings | None = None,
        http_settings: HTTPSettings | None = None,
        intents: Intents = Intents.ALL,
        auto_chunk_members: bool = True,
        logs: int | str | Dict[str, Any] | None = "INFO",
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: ProxySettings | None = None,
        rest_url: str | None = None,
    ) -> None:
        super().__init__(
            token,
            allow_color=allow_color,
            banner=banner,
            executor=executor,
            force_color=force_color,
            cache_settings=cache_settings,
            http_settings=http_settings,
            intents=intents,
            auto_chunk_members=auto_chunk_members,
            logs=logs,
            max_rate_limit=max_rate_limit,
            max_retries=max_retries,
            proxy_settings=proxy_settings,
            rest_url=rest_url,
        )
        self.client = ZeusClient.from_gateway_bot(self)
        self._subscribe_to_listeners()

    def _subscribe_to_listeners(self) -> None:
        events: Dict[Type[Any], Callable[[Any], Coroutine[Any, Any, None]]] = {
            StartingEvent: self.starting_event,
            StoppingEvent: self.stopping_event,
        }

        for event_type, callback in events.items():
            self.event_manager.subscribe(event_type, callback)

    def run(
        self,
        *,
        activity: Activity
        | None = Activity(
            name=f"for /help | Version {Config.VERSION}",
            type=ActivityType.WATCHING,
        ),
        afk: bool = False,
        asyncio_debug: bool | None = None,
        check_for_updates: bool = True,
        close_passed_executor: bool = False,
        close_loop: bool = True,
        coroutine_tracking_depth: int | None = None,
        enable_signal_handlers: bool | None = None,
        idle_since: datetime | None = None,
        ignore_session_start_limit: bool = False,
        large_threshold: int = 250,
        propagate_interrupts: bool = False,
        status: Status = Status.ONLINE,
        shard_ids: Sequence[int] | None = None,
        shard_count: int | None = None,
    ) -> None:
        self.client.load_modules()  # type: ignore

        super().run(
            activity=activity,
            afk=afk,
            asyncio_debug=asyncio_debug,
            check_for_updates=check_for_updates,
            close_passed_executor=close_passed_executor,
            close_loop=close_loop,
            coroutine_tracking_depth=coroutine_tracking_depth,
            enable_signal_handlers=enable_signal_handlers,
            idle_since=idle_since,
            ignore_session_start_limit=ignore_session_start_limit,
            large_threshold=large_threshold,
            propagate_interrupts=propagate_interrupts,
            status=status,
            shard_ids=shard_ids,
            shard_count=shard_count,
        )

    async def starting_event(self, _: StartingEvent) -> None:
        self.logger.info("Starting bot.")

    async def stopping_event(self, _: StoppingEvent) -> None:
        self.logger.info("Stopping bot.")


__all__: Final = ("ZeusBot",)
