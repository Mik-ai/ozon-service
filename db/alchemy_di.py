from config import engine, do_retry_on_fail
from db.orm.models import MxProductsOzon, MxAsPrice
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update


@do_retry_on_fail
def select_execute(stmt):
    with Session(engine) as session:
        return session.execute(stmt).all()


@do_retry_on_fail
def session_scalars(stmt):
    with Session(engine) as session:
        return session.scalars(stmt).all()

@do_retry_on_fail
def session_commit(stmt):
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


def custom_orm_select(
    cls_from: list,
    where_params: list = None,
    sql_limit: int = None,
    join_on: list = None,
):
    if isinstance(cls_from, list):
        stmt = select(*cls_from)
    else:
        stmt = select(cls_from)

    if join_on:
        stmt = stmt.join(*join_on)

    if where_params:
        stmt = stmt.where(*where_params)

    if sql_limit:
        stmt = stmt.limit(sql_limit)
    if isinstance(cls_from, list):
        return select_execute(stmt)
    return session_scalars(stmt)


def custom_orm_bulk_update(cls_to: list, data: dict):
    stmt = update(cls_to).values(data)
    session_commit(stmt)


def custom_upsert(cls_to: list, index_elements: list, data: dict, update_set: dict):
    stmt = insert(cls_to).values(data)
    stmt = stmt.on_conflict_do_update(
        index_elements=index_elements,
        set_={x: getattr(stmt.excluded, x) for x in update_set},
    )
    session_commit(stmt)
