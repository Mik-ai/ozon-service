from db.alchemy_di_async import custom_orm_select, custom_orm_bulk_update
from db.orm.schema_public import MxProductsOzonBrandFix, MxProductsOzon
from business.products_async import MassProductsEditor
from external_api.ozon_async import OzonApi
from config import OZON_CREDENTIALS, batch_lengh_generator
from logger import Logger

import asyncio, aiohttp, re, logging, time


async def download_products_from_brand_fix() -> list:
    result = await custom_orm_select(
        cls_from=[
            MxProductsOzonBrandFix.marketplace_id,
            MxProductsOzonBrandFix.brand_found,
            MxProductsOzonBrandFix.found_in_name,
            MxProductsOzonBrandFix.found_in_descr,
        ],
        where_params=[
            MxProductsOzonBrandFix.do_delete == False,
            MxProductsOzonBrandFix.fixed != True,
        ],
    )
    return result


async def download_repair_products_from_brand_fix() -> list:
    result = await custom_orm_select(
        cls_from=[
            MxProductsOzonBrandFix.marketplace_id,
            MxProductsOzonBrandFix.brand_found,
            MxProductsOzonBrandFix.found_in_name,
            MxProductsOzonBrandFix.found_in_descr,
            MxProductsOzon.product_name,
            MxProductsOzon.product_description,
        ],
        join_on=[
            MxProductsOzon,
            MxProductsOzon.marketplace_id == MxProductsOzonBrandFix.marketplace_id,
        ],
        where_params=[
            MxProductsOzonBrandFix.fixed == True,
            MxProductsOzonBrandFix.do_delete == False,
        ],
    )
    return result


def edit_name(products_dict_item, full_item):
    if products_dict_item.found_in_name:
        full_item["name"] = re.sub(
            products_dict_item.brand_found,
            "",
            full_item["name"],
            flags=re.IGNORECASE,
        )
        try:
            if attr := [
                x for x in full_item["attributes"] if x["attribute_id"] == 4180
            ]:
                attr = attr[0]
                attr["values"][0]["value"] = re.sub(
                    products_dict_item.brand_found,
                    "",
                    attr["values"][0]["value"],
                    flags=re.IGNORECASE,
                )
        except IndexError:
            log_message = f"{time.ctime()} poduct name attribute not found, offer_id: {full_item['offer_id']}"
            logging.error(log_message)


def edit_description(products_dict_item, full_item):
    try:
        if attr := [x for x in full_item["attributes"] if x["attribute_id"] == 4191]:
            attr = attr[0]
            attr["values"][0]["value"] = re.sub(
                products_dict_item.brand_found,
                "",
                attr["values"][0]["value"],
                flags=re.IGNORECASE,
            )
    except IndexError:
        log_message = f"{time.ctime()} poduct descrition attribute not found, offer_id: {full_item['offer_id']}"
        logging.error(log_message)


def repair_name(products_item, full_item):
    if products_item.found_in_name:
        full_item["name"] = products_item.product_name
        try:
            if attr := [
                x for x in full_item["attributes"] if x["attribute_id"] == 4180
            ]:
                attr = attr[0]
                attr["values"][0]["value"] = products_item.product_name
        except IndexError:
            log_message = f"{time.ctime()} poduct name attribute not found, offer_id: {full_item['offer_id']}"
            logging.error(log_message)


def repair_description(products_item, full_item):
    try:
        if attr := [x for x in full_item["attributes"] if x["attribute_id"] == 4191]:
            attr = attr[0]
            attr["values"][0]["value"] = products_item.product_description
    except IndexError:
        log_message = f"{time.ctime()} poduct descrition attribute not found, offer_id: {full_item['offer_id']}"
        logging.error(log_message)


async def repair_task(products, **kwargs):
    async with kwargs["semaphore"]:
        print(f"start_updating_products first is: {products[0].marketplace_id}")
        api = OzonApi(session=kwargs["session"])
        editor = MassProductsEditor(api)
        await editor.collect_products(products)

        products_dict = {x.marketplace_id: x for x in products}
        full_items_dict = {x["id"]: x for x in editor.full_items}

        for marketplace_id in products_dict:
            if products_dict[marketplace_id].found_in_name:
                repair_name(
                    products_dict[marketplace_id], full_items_dict[marketplace_id]
                )
            if products_dict[marketplace_id].found_in_descr:
                repair_description(
                    products_dict[marketplace_id], full_items_dict[marketplace_id]
                )

        await editor.commit_changes()
        brand_fix_update = [
            {"marketplace_id": x.marketplace_id, "fixed": True} for x in products
        ]
        await custom_orm_bulk_update(MxProductsOzonBrandFix, brand_fix_update)


async def task(products, **kwargs):
    async with kwargs["semaphore"]:
        print(f"start_updating_products first is: {products[0].marketplace_id}")
        api = OzonApi(session=kwargs["session"])
        editor = MassProductsEditor(api)
        await editor.collect_products(products)

        products_dict = {x.marketplace_id: x for x in products}
        full_items_dict = {x["id"]: x for x in editor.full_items}

        for marketplace_id in products_dict:
            if products_dict[marketplace_id].found_in_name:
                edit_name(
                    products_dict[marketplace_id],
                    full_items_dict[marketplace_id],
                )
            if products_dict[marketplace_id].found_in_descr:
                edit_description(
                    products_dict[marketplace_id],
                    full_items_dict[marketplace_id],
                )

        await editor.commit_changes()
        brand_fix_update = [
            {"marketplace_id": x.marketplace_id, "fixed": True} for x in products
        ]
        await custom_orm_bulk_update(MxProductsOzonBrandFix, brand_fix_update)


async def create_tasks(products, **kwargs):
    tasks = []
    marketplace_id_batches = batch_lengh_generator(data=products, step=1000)

    for id_batch in marketplace_id_batches:
        tasks.append(asyncio.create_task(repair_task(products=id_batch, **kwargs)))
    return tasks


async def pipeline_with_session():
    products = await download_repair_products_from_brand_fix()
    semaphore = asyncio.Semaphore(3)
    async with aiohttp.ClientSession(headers=OZON_CREDENTIALS) as session:
        tasks = await create_tasks(
            products=products, semaphore=semaphore, session=session
        )
        await asyncio.gather(*tasks)


def start_main():
    my_logger = Logger("brand_fix", "brand_fix_from_ozon_brand_fix")
    asyncio.run(pipeline_with_session())
