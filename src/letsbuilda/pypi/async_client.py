"""The async client."""

from io import BytesIO
from typing import Final, Self

import xmltodict

try:
    from aiohttp import ClientSession
except ImportError as error:
    msg = "Please install letsbuilda[async] for async support!"
    raise ImportError(msg) from error

from .models import JSONPackageMetadata, RSSPackageMetadata


class PyPIServices:
    """A class for interacting with PyPI."""

    NEWEST_PACKAGES_FEED_URL: Final[str] = "https://pypi.org/rss/packages.xml"
    PACKAGE_UPDATES_FEED_URL: Final[str] = "https://pypi.org/rss/updates.xml"

    def __init__(self: Self, http_session: ClientSession) -> None:
        self.http_session = http_session

    async def get_rss_feed(self: Self, feed_url: str) -> list[RSSPackageMetadata]:
        """Get the new packages RSS feed."""
        async with self.http_session.get(feed_url) as response:
            response_text = await response.text()
            rss_data = xmltodict.parse(response_text)["rss"]["channel"]["item"]
            return [RSSPackageMetadata.build_from(package_data) for package_data in rss_data]

    async def get_package_metadata(
        self: Self,
        package_name: str,
        package_version: str | None = None,
    ) -> JSONPackageMetadata:
        """Get metadata for a package."""
        if package_version is not None:
            url = f"https://pypi.org/pypi/{package_name}/{package_version}/json"
        else:
            url = f"https://pypi.org/pypi/{package_name}/json"
        async with self.http_session.get(url) as response:
            return JSONPackageMetadata.from_dict(await response.json())

    async def fetch_bytes(
        self: Self,
        url: str,
    ) -> BytesIO:
        """Fetch bytes from a URL."""
        buffer = BytesIO()
        async with self.http_session.get(url) as response:
            buffer.write(await response.content.read())
        buffer.seek(0)
        return buffer