from config import engine, do_retry_on_fail
from .orm.models import MxProductsOzonBrandFix

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert


@do_retry_on_fail
def insert_by_orm_conflict_do_nothing(brand_fix_list: list[MxProductsOzonBrandFix]):
    with Session(engine) as session:
        dict_values = [x.__dict__ for x in brand_fix_list]
        for i in dict_values:
            i.pop("_sa_instance_state")

        session.execute(
            insert(MxProductsOzonBrandFix)
            .values(dict_values)
            .on_conflict_do_nothing(index_elements=["marketpace_id"])
        )
        session.commit()


@do_retry_on_fail
def insert_by_orm_conflict_do_update(brand_fix_list: list[MxProductsOzonBrandFix]):
    with Session(engine) as session:
        dict_values = [x.__dict__ for x in brand_fix_list]
        for i in dict_values:
            i.pop("_sa_instance_state")

        stmt = insert(MxProductsOzonBrandFix).values(dict_values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["marketpace_id"],
            set_={
                "brand_found": stmt.excluded.brand_found,
                "found_in_name": stmt.excluded.found_in_name,
                "found_in_descr": stmt.excluded.found_in_descr,
            },
        )

        session.execute(stmt)
        session.commit()
