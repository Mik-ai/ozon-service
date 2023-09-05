from db.orm.schema_public import MxProductsOzon, MxAsPrice
from db.alchemy_di import custom_orm_select
from external_api.ozon import OzonApi

import json_work, time


multiple_packages_attribute = {
    "attribute_id": 22073,
    "complex_id": 0,
    "values": [{"dictionary_value_id": 0, "value": "true"}],
}


def load_results() -> dict:
    return json_work.open_json("categories_to_process.json")


def save_results(categories_to_process: dict):
    json_work.save_json(categories_to_process, "categories_to_process.json")


def get_attribute_for_one_category(category_ids: int) -> dict:
    api = OzonApi()
    try:
        return api.request_one_category_attributes(category_ids)
    except:
        return []


def get_attribute_for_multiple_categories(category_ids: list) -> dict:
    api = OzonApi()
    try:
        return api.request_category_attributes(category_ids)
    except:
        return []


def process_one_category_attribute(category_attributes: list) -> str:
    if not category_attributes:
        return "bad_category"
    if [at for at in category_attributes for i in at["attributes"] if i["id"] == 22073]:
        return "do_update_category"
    else:
        return "not_update_category"


def process_multiple_category_attributes(category_ids: list) -> dict:
    result = {}
    try:
        category_attributes = get_attribute_for_multiple_categories(category_ids)
        if not category_attributes:
            raise Exception

        do_update = {
            str(at["category_id"]): "do_update_category"
            for at in category_attributes
            for i in at["attributes"]
            if i["id"] == 22073
        }
        do_not_update = {
            str(at["category_id"]): "not_update_category"
            for at in category_attributes
            if at["category_id"] not in do_update
        }
        return dict(do_not_update, **do_update)

    except:
        print(f"processing categories by 1")
        for category in category_ids:
            print(f"processing: {category}")
            attribute = get_attribute_for_one_category(category)
            result[str(category)] = process_one_category_attribute(attribute)
            print("going sleep")
            time.sleep(1)
    return result


def start_apend_attribute_on_have_barcode():
    categories_to_process = load_results()
    categories_to_process = [
        x
        for x in categories_to_process
        if categories_to_process[x] == "do_update_category"
    ]
    some_var = custom_orm_select(
        cls_from=[MxProductsOzon.marketplace_id, MxAsPrice.barcode],
        join_on=[MxAsPrice, MxAsPrice.product_id == MxProductsOzon.product_id],
        where_params=[
            MxProductsOzon.is_archived == False,
            MxProductsOzon.barcode == "",
            MxAsPrice.barcode != "",
            MxProductsOzon.category_id.in_(categories_to_process),
        ],
    )
    "marketplace_id" in some_var[1]._fields
    getattr(some_var[1], "marketplace_id")

    somlam = lambda a, k: [getattr(x, k) for x in a if k in x._fields]
    somlam(some_var, "marketplace_id")


def start_count_products_to_update():
    categories_to_process = load_results()

    bad_categories = [
        x for x in categories_to_process if categories_to_process[x] == "bad_category"
    ]

    list_of_keys = [
        x
        for x in categories_to_process
        if categories_to_process[x] == "do_update_category"
    ]

    nubmer_of_products = custom_orm_select(
        cls_from=MxProductsOzon,
        where_params=[MxProductsOzon.category_id.in_(list_of_keys)],
    )
    got_prod = [
        x
        for x in nubmer_of_products
        if x.state_name in ["Готов к продаже", "Продается"] and not x.is_archived
    ]
    not_got_prod = [
        x
        for x in nubmer_of_products
        if x.state_name not in ["Готов к продаже", "Продается"] and not x.is_archived
    ]
    archived = [x for x in nubmer_of_products if x.is_archived]
    with_barcode = [
        x for x in nubmer_of_products if not x.is_archived and x.barcode != ""
    ]
    with_barcode_got_prod = [
        x
        for x in nubmer_of_products
        if x.state_name in ["Готов к продаже", "Продается"]
        and not x.is_archived
        and x.barcode != ""
    ]
    with_barcode_not_got_prod = [
        x
        for x in nubmer_of_products
        if x.state_name not in ["Готов к продаже", "Продается"]
        and not x.is_archived
        and x.barcode != ""
    ]

    print(
        f"Всего: {len(nubmer_of_products)}\n"
        f"В архиве: {len(archived)}\n"
        f"Продаются и готовы к продаже: {len(got_prod)}\n"
        f"Не продаются: {len(not_got_prod)}\n"
        f"С штрихкодом: {len(with_barcode)}\n"
        f"С штрихкодом Продаются и готовы к продаже: {len(with_barcode_got_prod)}\n"
        f"С штрихкодом не готовы к продаже: {len(with_barcode_not_got_prod)}\n"
    )


def start_multiple_category_fix():
    # dict({"1":1,"2":2,"3":3},**{"1":4,"3":4}) example of what i'am doing

    categories_to_process = load_results()

    list_of_keys = [x for x in categories_to_process if categories_to_process[x] == ""]

    step = 20
    bulk_process = (
        list_of_keys[x : x + step] for x in range(0, len(list_of_keys), step)
    )

    for categories in bulk_process:
        print(f"processing categories, first is: {categories[0]}")
        processed_categories = process_multiple_category_attributes(categories)
        categories_to_process = dict(categories_to_process, **processed_categories)
        save_results(categories_to_process)
        print("going sleep")
        time.sleep(1)
