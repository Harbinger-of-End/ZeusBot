from __future__ import annotations

import os
from enum import Enum, auto
from typing import TYPE_CHECKING

from hikari import Snowflake

if TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Dict,
        Final,
        List,
        Literal,
        Self,
        Tuple,
        Type,
    )


class EnvironmentVariables(str, Enum):
    """An enumeration of the environment variables."""

    TOKEN = auto()
    PREFIX = auto()
    VERSION = auto()
    SENTRY_DSN = auto()
    PSQL_HOST = auto()
    PSQL_PORT = auto()
    PSQL_USER = auto()
    PSQL_PASSWORD = auto()
    PSQL_DATABASE = auto()
    LAVALINK_HOST = auto()
    LAVALINK_PORT = auto()
    LAVALINK_PASSWORD = auto()
    HOME_GUILD_IDS = auto()
    AUTHOR_ID = auto()
    BOT_ID = auto()

    def __index__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class EnvironmentVariableMissingException(Exception):
    """
    The exception that is raised when a variable is missing in environment.
    """

    def __init__(self, name: str | EnvironmentVariables) -> None:
        super().__init__(
            f"Environment variable {name!r} missing in environment"
        )


env_set = False


def _load_dotenv() -> None:
    from pathlib import Path

    envfile = Path(__file__).parent.parent.parent / ".env"

    with envfile.open("r", encoding="utf-8") as env:
        in_env_vars = False

        for line in env:
            if line.startswith("#") and line[2:].strip() == "Hikari":
                in_env_vars = True
                continue

            if in_env_vars:
                if line == "\n":
                    in_env_vars = False
                    continue

                key, value = line.strip().split("=", 1)
                os.environ[key] = value

        global env_set
        env_set = True


class _MetaConfig(type):
    """
    A meta-class for the class :class:`Config`.
    This class exists solely for the purpose of executing the
    function :func:`_load_dotenv`
    """

    def __new__(
        cls,
        name: str,
        bases: Tuple[Type[Any]],
        namespace: Dict[str, Any],
        **kwargs: Any,
    ) -> Self:  # type: ignore
        if not env_set:
            _load_dotenv()

        self = super().__new__(
            cls,
            name,
            bases,
            namespace,
            **kwargs,
        )

        for member in EnvironmentVariables.__members__:
            if member == "HOME_GUILD_IDS":
                setattr(
                    self,
                    member,
                    self._get_environment_variable(member, True),
                )

            setattr(self, member, self._get_environment_variable(member))

        return self

    def _resolve_value(self, value: str | EnvironmentVariables) -> Any:
        _map: Dict[str, Callable[[str], Any]] = {
            "str": str,
            "list": lambda x: [
                self._resolve_value(e.strip()) for e in x.split(",")
            ],
            "Snowflake": Snowflake,
            "bool": lambda x: True
            if x == "True"
            else False
            if x == "False"
            else None,
            "int": int,
        }

        return _map[(v := value.split(":", 1))[0]](v[1])

    def _resolve_key(self, key: str | EnvironmentVariables) -> Any:
        try:
            return self._resolve_key(os.environ[key])

        except BaseException:
            return self._resolve_value(key)

    def _get_environment_variable(
        self,
        name: str | EnvironmentVariables,
        default: Any | None = None,
    ) -> Any:
        try:
            return self._resolve_key(name)

        except KeyError:
            if default is not None:
                return default

            raise EnvironmentVariableMissingException(name)


class Config(metaclass=_MetaConfig):
    """The configuration class for the bot."""

    if TYPE_CHECKING:
        TOKEN: str
        PREFIX: str
        VERSION: str
        SENTRY_DSN: str
        PSQL_HOST: str
        PSQL_PORT: int
        PSQL_USER: str
        PSQL_PASSWORD: str
        PSQL_DATABASE: str
        LAVALINK_HOST: str
        LAVALINK_PORT: int
        LAVALINK_PASSWORD: str
        HOME_GUILD_IDS: List[Snowflake] | Literal[True]
        AUTHOR_ID: Snowflake
        BOT_ID: Snowflake


__all__: Final = ("Config",)
