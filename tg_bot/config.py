from dataclasses import dataclass
from typing import List
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: List[int]
    use_redis: bool


@dataclass
class DbConfig:
    user: str
    password: str
    ip: str
    database: str
    postgres_uri: str


@dataclass
class Miscellaneous:
    banned_users: List[int]


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS")
        ),
        db=DbConfig(
            user=env.str("PG_USER"),
            password=env.str("PG_PASSWORD"),
            ip=env.str("PG_IP"),
            database=env.str("DB_NAME"),
            postgres_uri=env.str("POSTGRES_URI")
        ),
        misc=Miscellaneous(
            banned_users=list(map(int, env.list("BANNED_USERS")))
        )
    )
