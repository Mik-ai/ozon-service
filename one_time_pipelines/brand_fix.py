from db.mx_products_ozon_brand_fix import (
    insert_by_orm_conflict_do_update,
)
from db.orm.schema_public import MxProductsOzonBrandFix, MxProductsOzon
from db import mx_products_ozon
from json_work import open_json, save_json
from logger import Logger

loger = Logger(group_name="test-brand-fix", name_file="brand-fix")


def search_brand_products(brand_name: str) -> list:
    products = mx_products_ozon.select_regex_in_name_or_descr(brand_name)
    return products


def process_brand_products(
    products: list[MxProductsOzon],
    brand_name: str,
) -> list[MxProductsOzonBrandFix]:
    products_fix = []
    for i in products:
        if not i.product_name and not i.product_description:
            continue

        model = MxProductsOzonBrandFix()

        model.marketpace_id = i.marketplace_id
        model.offer_id = i.offer_id
        model.brand_found = brand_name
        try:
            model.found_in_descr = (
                True if brand_name.lower() in i.product_name.lower() else False
            )
        except:
            loger.log_message_error(f"product: {i.marketplace_id} has bad name")
        try:
            model.found_in_name = (
                True if brand_name.lower() in i.product_description.lower() else False
            )
        except:
            loger.log_message_error(f"product: {i.marketplace_id} has bad description")
        products_fix.append(model)
    return products_fix


def export_brand_products(products: list[MxProductsOzonBrandFix]):
    if products:
        insert_by_orm_conflict_do_update(products)


def process_bad_brand_products(brands: dict):
    file_name = "brands.json"
    brands = open_json(file_name)
    for brand_name in brands:
        if not brands[brand_name] == "additional verification":
            continue

        print(f"processing: {brand_name}")
        try:
            products = search_brand_products(brand_name)
            products = process_brand_products(products)
            export_brand_products(products)

            brands[brand_name] = "additional verification processed"
            save_json(file_name=file_name, data=brands)
        except Exception as e:
            loger.log_message_error(
                message=f"can't process brand: {brand_name}", exception=e
            )
