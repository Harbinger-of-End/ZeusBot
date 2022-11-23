from __future__ import annotations

from datetime import datetime
from random import randint
from typing import TYPE_CHECKING

from hikari import Color, Embed

if TYPE_CHECKING:
    from typing import List, Tuple

    from hikari import Colorish, InteractionMember, Member, Resourceish, User

    Fields = List[Tuple[str, str, bool]]
    Author = Tuple[str | None, str | None, Resourceish | None]
    Footer = Tuple[str | None, Resourceish | None]


class HikariUtility:
    """Hikari utility."""

    @staticmethod
    def random_color() -> Color:
        """Generate random color"""

        return Color(randint(0, 0xFFFFFF))  # nosec

    @classmethod
    def get_color_of_member(
        cls,
        member: Member | InteractionMember | None = None,
    ) -> Color:
        if member:
            return getattr(member.get_top_role(), "color", cls.random_color())

        return cls.random_color()

    @classmethod
    def build_embed(
        cls,
        /,
        *,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        color: Colorish | None = None,
        timestamp: datetime | None = None,
        fields: Fields | None = None,
        image: Resourceish | None = None,
        thumbnail: Resourceish | None = None,
        author: Author | None = None,
        footer: Footer | None = None,
    ) -> Embed:
        """Build embed from kwargs."""

        author_name, author_url, author_icon = author or (None, None, None)
        footer_text, footer_icon = footer or (None, None)

        embed = (
            Embed(
                title=title,
                description=description,
                url=url,
                color=color or cls.random_color(),
                timestamp=timestamp,
            )
            .set_author(name=author_name, url=author_url, icon=author_icon)
            .set_footer(footer_text, icon=footer_icon)
            .set_image(image)
            .set_thumbnail(thumbnail)
        )

        if fields:
            for name, value, inline in fields:
                embed.add_field(name, value, inline=inline)

        return embed

    @staticmethod
    def get_avatar_of_member(
        user: User,
    ) -> str:
        """Get the avatar url of member, with fallback to default avatar."""

        return getattr(user.avatar_url, "url", user.default_avatar_url.url)
