__all__ = [
    "ParentException",
    "PlaylistError",
    "AlbumError",
    "TrackError",
    "BaseClientError",
    "RequestError",
]

class ParentException(Exception):
    def __init__(self, message: str, error: str | None = None) -> None:
        super().__init__(message)
        self.error = error

class PlaylistError(ParentException):
    pass

class AlbumError(ParentException):
    pass

class TrackError(ParentException):
    pass

class BaseClientError(ParentException):
    pass

class RequestError(ParentException):
    pass