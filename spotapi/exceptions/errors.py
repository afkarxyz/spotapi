__all__ = [
    "ParentException",
    "RequestError",
    "BaseClientError",
    "TrackError",
    "AlbumError",
    "PlaylistError",
]

class ParentException(Exception):
    def __init__(self, message: str, error: str | None = None) -> None:
        super().__init__(message)
        self.error = error

class RequestError(ParentException):
    pass

class BaseClientError(ParentException):
    pass

class TrackError(ParentException):
    pass

class AlbumError(ParentException):
    pass

class PlaylistError(ParentException):
    pass
