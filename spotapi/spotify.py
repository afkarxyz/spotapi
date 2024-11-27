from __future__ import annotations

import json
from typing import Any
from collections.abc import Mapping, Generator
from spotapi.types.annotations import enforce

from spotapi.exceptions import PlaylistError, TrackError, AlbumError
from spotapi.http.request import TLSClient
from spotapi.client import BaseClient

__all__ = ["PublicPlaylist", "PublicTrack", "PublicAlbum", "PlaylistError", "TrackError", "AlbumError"]


@enforce
class PublicPlaylist:
    """
    Allows you to get all public information on a playlist.
    No login is required.

    Parameters
    ----------
    playlist (Optional[str]): The Spotify URI of the playlist.
    client (TLSClient): An instance of TLSClient to use for requests.
    """

    __slots__ = (
        "base",
        "playlist_id",
        "playlist_link",
    )

    def __init__(
        self,
        playlist: str | None = None,
        /,
        *,
        client: TLSClient = TLSClient("chrome_120", "", auto_retries=3),
    ) -> None:
        self.base = BaseClient(client=client)

        if playlist:
            self.playlist_id = (
                playlist.split("playlist/")[-1] if "playlist" in playlist else playlist
            )
            self.playlist_link = f"https://open.spotify.com/playlist/{self.playlist_id}"

    def get_playlist_info(
        self, limit: int = 25, *, offset: int = 0
    ) -> Mapping[str, Any]:
        """Gets the public playlist information"""
        if not self.playlist_id:
            raise ValueError("Playlist ID not set")

        url = "https://api-partner.spotify.com/pathfinder/v1/query"
        params = {
            "operationName": "fetchPlaylist",
            "variables": json.dumps(
                {
                    "uri": f"spotify:playlist:{self.playlist_id}",
                    "offset": offset,
                    "limit": limit,
                }
            ),
            "extensions": json.dumps(
                {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": self.base.part_hash("fetchPlaylist"),
                    }
                }
            ),
        }

        resp = self.base.client.post(url, params=params, authenticate=True)

        if resp.fail:
            raise PlaylistError("Could not get playlist info", error=resp.error.string)

        if not isinstance(resp.response, Mapping):
            raise PlaylistError("Invalid JSON")

        return resp.response

    def paginate_playlist(self) -> Generator[Mapping[str, Any], None, None]:
        """
        Generator that fetches playlist information in chunks

        Note: If total_tracks <= 343, then there is no need to paginate
        """
        UPPER_LIMIT: int = 343
        # We need to get the total playlists first
        playlist = self.get_playlist_info(limit=UPPER_LIMIT)
        total_count: int = playlist["data"]["playlistV2"]["content"]["totalCount"]

        yield playlist["data"]["playlistV2"]["content"]

        if total_count <= UPPER_LIMIT:
            return

        offset = UPPER_LIMIT
        while offset < total_count:
            yield self.get_playlist_info(limit=UPPER_LIMIT, offset=offset)["data"][
                "playlistV2"
            ]["content"]
            offset += UPPER_LIMIT


@enforce
class PublicTrack:
    """
    Allows you to get all public information on a track.
    No login is required.

    Parameters
    ----------
    track (Optional[str]): The Spotify URI of the track.
    client (TLSClient): An instance of TLSClient to use for requests.
    """

    __slots__ = (
        "base",
        "track_id",
        "track_link",
    )

    def __init__(
        self,
        track: str | None = None,
        /,
        *,
        client: TLSClient = TLSClient("chrome_120", "", auto_retries=3),
    ) -> None:
        self.base = BaseClient(client=client)

        if track:
            self.track_id = track.split("track/")[-1] if "track" in track else track
            self.track_link = f"https://open.spotify.com/track/{self.track_id}"

    def get_track_info(self) -> Mapping[str, Any]:
        """Gets the public track information"""
        if not self.track_id:
            raise ValueError("Track ID not set")

        url = "https://api-partner.spotify.com/pathfinder/v1/query"
        params = {
            "operationName": "getTrack",
            "variables": json.dumps(
                {
                    "uri": f"spotify:track:{self.track_id}",
                }
            ),
            "extensions": json.dumps(
                {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": self.base.part_hash("getTrack"),
                    }
                }
            ),
        }

        resp = self.base.client.post(url, params=params, authenticate=True)

        if resp.fail:
            raise TrackError("Could not get track info", error=resp.error.string)

        if not isinstance(resp.response, Mapping):
            raise TrackError("Invalid JSON")

        return resp.response

@enforce
class PublicAlbum:
    """
    Allows you to get all public information on an album.
    No login is required.

    Parameters
    ----------
    album (Optional[str]): The Spotify URI of the album.
    client (TLSClient): An instance of TLSClient to use for requests.
    """

    __slots__ = (
        "base",
        "album_id",
        "album_link",
    )

    def __init__(
        self,
        album: str | None = None,
        /,
        *,
        client: TLSClient = TLSClient("chrome_120", "", auto_retries=3),
    ) -> None:
        self.base = BaseClient(client=client)

        if album:
            self.album_id = album.split("album/")[-1] if "album" in album else album
            self.album_link = f"https://open.spotify.com/album/{self.album_id}"

    def get_album_info(
        self, limit: int = 25, *, offset: int = 0, locale: str = 'en'
    ) -> Mapping[str, Any]:
        """Gets the public album information"""
        if not self.album_id:
            raise ValueError("Album ID not set")

        url = "https://api-partner.spotify.com/pathfinder/v1/query"
        params = {
            "operationName": "getAlbum",
            "variables": json.dumps(
                {
                    "uri": f"spotify:album:{self.album_id}",
                    "offset": offset,
                    "limit": limit,
                    "locale": locale  # Add locale parameter
                }
            ),
            "extensions": json.dumps(
                {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": self.base.part_hash("getAlbum"),
                    }
                }
            ),
        }

        resp = self.base.client.post(url, params=params, authenticate=True)

        if resp.fail:
            raise AlbumError("Could not get album info", error=resp.error.string)

        if not isinstance(resp.response, Mapping):
            raise AlbumError("Invalid JSON")

        return resp.response

    def paginate_album_tracks(self, locale: str = 'en') -> Generator[Mapping[str, Any], None, None]:
        """
        Generator that fetches album tracks information in chunks
        
        Note: If total_tracks <= 50, then there is no need to paginate
        """
        UPPER_LIMIT: int = 50
        # We need to get the total tracks first
        album = self.get_album_info(limit=UPPER_LIMIT, locale=locale)
        total_count: int = album["data"]["albumUnion"]["tracks"]["totalCount"]

        yield album["data"]["albumUnion"]["tracks"]

        if total_count <= UPPER_LIMIT:
            return

        offset = UPPER_LIMIT
        while offset < total_count:
            yield self.get_album_info(limit=UPPER_LIMIT, offset=offset, locale=locale)["data"][
                "albumUnion"
            ]["tracks"]
            offset += UPPER_LIMIT