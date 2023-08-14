from config import engine, do_retry_on_fail
from .orm.models import MxProductsOzon, MxAsPrice

from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import or_


def select_regex_in_name_or_descr(
    re_pattern: str, state_name_in: list[str] = None
) -> list[MxProductsOzon]:
    with Session(engine) as session:
        params = [
            or_(
                MxProductsOzon.product_description.regexp_match(re_pattern, "i"),
                MxProductsOzon.product_name.regexp_match(re_pattern, "i"),
            ),
            MxProductsOzon.is_archived == False,
        ]
        if state_name_in:
            params.append(MxProductsOzon.state_name.in_(state_name_in))

        stmt = select(MxProductsOzon).where(*params)
        result = session.scalars(stmt).all()
    return result


@do_retry_on_fail
def bulk_update(data: list[dict]):
    """update db values by pk

    Args:
        data (list[dict]): update data format:
    [
        {"marketplace_id": value, "update_field": "value"},
        {"marketplace_id": value, "update_field": "value"},
        {"marketplace_id": value, "update_field": "value"}
    ]
    """
    with Session(engine) as session:
        session.execute(update(MxProductsOzon), data)
        session.commit()


@do_retry_on_fail
def upsert_task_id(data: list[dict]):
    with Session(engine) as session:
        stmt = insert(MxProductsOzon).values(data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["marketpace_id"],
            set_={
                "task_id": stmt.excluded.task_id,
                "offer_id": stmt.excluded.offer_id,
                "updated_at": stmt.excluded.updated_at,
            },
        )
        session.execute(stmt)
        session.commit()
