from config import engine, do_retry_on_fail
from db.orm.schema_public import MxProductsOzon, MxAsPrice, MxProductsOzonBrandFix
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
def session_execute_commit(stmt):
    with Session(engine) as session:
        session.execute(stmt)
        session.commit()


def custom_orm_select(
    cls_from: list,
    where_params: list = None,
    sql_limit: int = None,
    join_on=None,
):
    stmt = select(*cls_from) if isinstance(cls_from, list) else select(cls_from)
    
    if join_on:
        stmt = (
            stmt.join(*join_on)
            if isinstance(join_on, list)
            else stmt.join(**join_on)
        )

    if where_params:
        stmt = stmt.where(*where_params)

    if sql_limit:
        stmt = stmt.limit(sql_limit)

    if isinstance(cls_from, list):
        return select_execute(stmt)
    return session_scalars(stmt)


@do_retry_on_fail
def custom_orm_bulk_update(cls_to, data: list):
    with Session(engine) as session:
        session.execute(update(cls_to), data)
        session.commit()


def custom_upsert(
    cls_to: list, index_elements: list, data: list[dict], update_set: list[str]
):
    stmt = insert(cls_to).values(data)
    stmt = stmt.on_conflict_do_update(
        index_elements=index_elements,
        set_={x: getattr(stmt.excluded, x) for x in update_set},
    )
    session_execute_commit(stmt)
