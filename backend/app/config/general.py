import functools

import pydantic


class Settings(pydantic.BaseSettings):
    DATABASE_URL: pydantic.PostgresDsn

    class Config:
        case_sensitive = True


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()
