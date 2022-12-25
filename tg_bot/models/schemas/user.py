from sqlalchemy import Column, BigInteger, String, sql

from tg_bot.models.db_gino import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(15), primary_key=True)
    password = Column(String(30), primary_key=True)

    query: sql.Select
