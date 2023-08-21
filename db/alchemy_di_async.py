from config import engine_async, retry_async
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update


@retry_async(5)
async def select_execute(stmt):
    """Used for select, return all values
    in case of select([MxProductOzon]) or select([MxProductOzon.marketplace_id, MxProductOzon.offer_id])
    return will be row of Sqlalchemy Row objects

    Args:
        stmt: sqlalchemy generated request

    Returns:
        Row: Sqlalchemy Row, can be treat as named tuple
    """
    async_session = async_sessionmaker(engine_async, expire_on_commit=True)
    async with async_session() as session:
        result = await session.execute(stmt)
        return result.all()


@retry_async(5)
async def session_scalars(stmt):
    """Used for select, return only first type of object, coulde be useful
    if result must be list of integers or list of orm objects

    example: select(MxProductOzon) or select(MxProductOzon,MxSlItem)
        will return only MxProductOzon items but sql will be generated for both
    example: select(MxProductOzon.marketplace_id) or select(MxProductOzon.marketplace_id, MxProductOzon.offer_id)
        will return list of marketplace_id only

    Args:
        stmt: sqlalchemy generated request

    Returns:
        list: list of whatever you request
    """
    async_session = async_sessionmaker(engine_async, expire_on_commit=True)
    async with async_session() as session:
        result = await session.scalars(stmt)
        return result.all()


@retry_async(5)
async def session_execute_commit(stmt):
    """Could be used for sqlalchemy requests that are not require to be return

    Args:
        stmt: sqlalchemy generated request
    """
    async_session = async_sessionmaker(engine_async, expire_on_commit=True)
    async with async_session() as session:
        await session.execute(stmt)
        await session.commit()


async def custom_orm_select(
    cls_from,
    where_params: list = None,
    sql_limit: int = None,
    join_on=None,
):
    """method for querying DB

    Args:
        cls_from: can be Orm object or list[OrmObj1,OrmObj2] or list[OrmObj1.field_1, OrmObj1.field_2, OrmObj2.field_2]
        where_params (list, optional): example: [MxProductOzon.marketplace_id.in_([123974,9384556...]), MxProductOzon.is_archived == False]
        sql_limit (int, optional): converts to sql limit command, do exactly same

        join_on (list or dict, optional):
        example: in case of list[OrmObjWillBeJoined, OrmObjWillBeJoined.joinable_field == OrmObjToJoin.another_joinable_field]
        in case of dict it should have the following fields:
            target: OrmObject,
            onclause: OrmObject.field == OrmObject2.field;
        optional fields:
            isouter:bool
            full:bool

    Returns:
        list: depends on what is called execute/scalars, will use scalars for individual objects, in case of list execute
    """
    stmt = select(*cls_from) if isinstance(cls_from, list) else select(cls_from)

    if join_on:
        stmt = (
            stmt.join(*join_on) if isinstance(join_on, list) else stmt.join(**join_on)
        )

    if where_params:
        stmt = stmt.where(*where_params)

    if sql_limit:
        stmt = stmt.limit(sql_limit)

    if isinstance(cls_from, list):
        return await select_execute(stmt)
    return await session_scalars(stmt)


@retry_async(5)
async def custom_orm_bulk_update(cls_to, data: list):
    """update db values by pk

    Args:
        data (list[dict]): update data format:
    [
        {"marketplace_id": value, "update_field": "value"},
        {"marketplace_id": value, "update_field": "value"},
        {"marketplace_id": value, "update_field": "value"}
    ]
    """
    async_session = async_sessionmaker(engine_async, expire_on_commit=True)
    async with async_session() as session:
        await session.execute(update(cls_to), data)
        await session.commit()


async def custom_insert_do_nothing(
    cls_to,
    index_elements: list[str],
    data: list[dict],
):
    stmt = (
        insert(cls_to)
        .values(data)
        .on_conflict_do_nothing(index_elements=index_elements)
    )
    session_execute_commit(stmt)


async def custom_upsert(
    cls_to, index_elements: list[str], data: list[dict], update_set: list[str]
):
    """perform postgesql insert on conflict do update

    Args:
        cls_to : orm object like MxProductOzon
        index_elements (list[str]): responsible for this sql part: CONFLICT (field, field2...)
        data (list[dict]): list like: [{"marketplace_id": value, "update_field": "value", "update_field2": "value2"}...]
        update_set (list[str]): what field should be changed on conflict
    """
    stmt = insert(cls_to).values(data)
    stmt = stmt.on_conflict_do_update(
        index_elements=index_elements,
        set_={x: getattr(stmt.excluded, x) for x in update_set},
    )
    session_execute_commit(stmt)
