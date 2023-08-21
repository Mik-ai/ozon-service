from config import engine_async, retry_async
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import update

from db.orm.models import MxProductsOzon


@retry_async(5)
async def bulk_update(data: list):
    """update db values by pk

    Args:
        data (list[dict]): update data format:
    [
        {"marketplace_id": value, "update_field": "value"},
        {"marketplace_id": value, "update_field": "value"},
        {"marketplace_id": value, "update_field": "value"}
    ]
    """
    async_session = async_sessionmaker(engine_async, expire_on_commit=False)
    async with async_session() as session:
        await session.execute(update(MxProductsOzon), data)
        await session.commit()
