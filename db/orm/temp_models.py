from config import engine
from sqlalchemy import Table, Column, Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import TEXT


class Base(DeclarativeBase):
    pass


class MxAsProduct(Base):
    __table__ = Table(
        "mx_as_Product",
        Base.metadata,
        autoload_with=engine,
    )


class Photo(Base):
    __table__ = Table(
        "Photo",
        Base.metadata,
        Column("PhotoId", Integer, primary_key=True),
        autoload_with=engine,
    )


class MxAsPrice(Base):
    __table__ = Table("mx_as_Price", Base.metadata, autoload_with=engine)


class MxSlCategory(Base):
    __table__ = Table(
        "mx_sl_category",
        Base.metadata,
        autoload_with=engine,
    )


class MxSlItem(Base):
    __table__ = Table(
        "mx_sl_item",
        Base.metadata,
        autoload_with=engine,
    )
