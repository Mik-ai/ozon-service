from db.orm.models import MxCategoryTreeMp
from db.orm.temp_models import MxSlCategory, MxSlItem
from config import engine

from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import distinct


def select_sl_item_distinct():
    with Session(engine) as session:
        stmt = select(distinct(MxSlItem.category_id)).where(MxSlItem.category_id != 0)
        return session.scalars(stmt).all()


def select_sl_categories_id_in(id_in: list[int]) -> MxSlCategory:
    with Session(engine) as session:
        stmt = select(MxSlCategory).where(MxSlCategory.id.in_(id_in))
        return session.scalars(stmt).all()


def select_all_sl_categories() -> list[MxSlCategory]:
    with Session(engine) as session:
        stmt = select(MxSlCategory)
        return session.scalars(stmt).all()


def upsert_category_tree(category_tree: list[dict]):
    with Session(engine) as session:
        stmt = insert(MxCategoryTreeMp).values(category_tree)
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                "marketplace_id",
                "leaf_category",
                "level",
            ],
            set_={
                "category_id": stmt.excluded.category_id,
                "updated_at": stmt.excluded.updated_at,
            },
        )
        session.execute(stmt)
        session.commit()


def process_sl_categories():
    sl_calegory_ids = select_sl_item_distinct()
    sl_calegories = select_sl_categories_id_in(sl_calegory_ids)

    tree_categories = [
        {
            "marketplace_id": 0,
            "leaf_category": sl_category.id,
            "level": index + 1,
            "category_id": x,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        for sl_category in sl_calegories
        for index, x in enumerate(sl_category.path.split("."))
    ]

    upsert_category_tree(tree_categories)
    print("done!")
