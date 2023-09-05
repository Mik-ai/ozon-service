from business.products import MassProductsEditor
import json_work
from db.orm.schema_public import MxAsPrice, MxProductsOzon
from db.alchemy_di import custom_orm_select
from logger import Logger

multiple_packages_attribute = {
    "attribute_id": 22073,
    "complex_id": 0,
    "values": [{"dictionary_value_id": 0, "value": "true"}],
}


def load_results() -> dict:
    return json_work.open_json("categories_to_process.json")


def start_set_attr_where_barcode_notempty_pipeline():
    logger = Logger("attr_where_barcode_notempty", "set_attr_pipeline")
    editor = MassProductsEditor()

    categories_to_process = load_results()
    categories_to_process = [
        x
        for x in categories_to_process
        if categories_to_process[x] == "do_update_category"
    ]
    items_from_db = custom_orm_select(
        cls_from=[MxProductsOzon.marketplace_id],
        where_params=[
            MxProductsOzon.is_archived == False,
            MxProductsOzon.category_id.in_(categories_to_process),
            MxProductsOzon.state_name.in_(["Готов к продаже", "Продается"]),
            MxProductsOzon.barcode != "",
        ],
    )

    step = 1000
    item_chunks = (
        items_from_db[x : x + step] for x in range(0, len(items_from_db), step)
    )

    for chunk in item_chunks:
        print(f"start processing chunk, first item is: {chunk[0].marketplace_id}")
        editor.collect_products(chunk)
        editor.add_attr(multiple_packages_attribute)
        editor.commit_changes()


def start_set_attr_where_barcode_empty_pipeline():
    logger = Logger("set_attr_where_barcode_pipeline", "set_attr_pipeline")
    editor = MassProductsEditor()

    categories_to_process = load_results()
    categories_to_process = [
        x
        for x in categories_to_process
        if categories_to_process[x] == "do_update_category"
    ]
    items_from_db = custom_orm_select(
        cls_from=[MxProductsOzon.marketplace_id, MxAsPrice.barcode],
        join_on=[MxAsPrice, MxAsPrice.product_id == MxProductsOzon.product_id],
        where_params=[
            MxProductsOzon.is_archived == False,
            MxProductsOzon.barcode == "",
            MxAsPrice.barcode != "",
            MxProductsOzon.category_id.in_(categories_to_process),
        ],
    )

    step = 1000
    item_chunks = (
        items_from_db[x : x + step] for x in range(0, len(items_from_db), step)
    )
    barcode_key = "barcode"

    for chunk in item_chunks:
        print(f"start processing chunk, first item is: {chunk[0].marketplace_id}")
        editor.collect_products(chunk)
        editor.add_attr(multiple_packages_attribute)
        editor.change_custom_field_by_key_from_items(barcode_key)
        editor.commit_changes()


def start_set_barcode_where_category_id_not_in():
    logger = Logger(
        "set_attr_where_barcode_pipeline", "set_attr_pipeline_where_category_id_not_in"
    )
    editor = MassProductsEditor()

    categories_to_process = load_results()
    categories_to_process = [
        x
        for x in categories_to_process
        if categories_to_process[x] == "do_update_category"
    ]
    items_from_db = custom_orm_select(
        cls_from=[MxProductsOzon.marketplace_id, MxAsPrice.barcode],
        join_on=[MxAsPrice, MxAsPrice.product_id == MxProductsOzon.product_id],
        where_params=[
            MxProductsOzon.is_archived == False,
            MxProductsOzon.barcode == "",
            MxProductsOzon.state_name.in_(["Готов к продаже", "Продается"]),
            MxAsPrice.barcode != "",
        ],
    )
    items_from_db = items_from_db[:140000]

    step = 1000
    item_chunks = (
        items_from_db[x : x + step] for x in range(0, len(items_from_db), step)
    )
    barcode_key = "barcode"
    for chunk in item_chunks:
        print(f"start processing chunk, first item is: {chunk[0].marketplace_id}")
        editor.collect_products(chunk)
        editor.change_custom_field_by_key_from_items(barcode_key)
        editor.commit_changes()
