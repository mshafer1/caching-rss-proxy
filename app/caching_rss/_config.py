import typing

from decouple import config

RSS_ALLOWED_FEEDS: typing.Set[str] = set(config("RSS_ALLOWED_FEEDS", default="").split(","))

RSS_MAX_SIZE: int = config("RSS_MAX_SIZE", default=-1, cast=int)

RSS_STORAGE_PATH: str = config("RSS_STORAGE_PATH", default="./")
