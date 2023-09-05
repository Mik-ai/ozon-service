import aiohttp, aiocache, asyncio

from db.alchemy_di_async import custom_orm_select
from db.orm.schema_public import MxProductsOzon, MxProductsOzonBrandFix
from business.products_async import MassProductsEditor
from external_api.ozon_async import OzonApi
from json_work import open_json
from logger import Logger
from itertools import compress

from config import OZON_CREDENTIALS, batch_lengh_generator

brand_names_queue = asyncio.Queue()
to_process_items_queue = asyncio.Queue()

cache_marketplace_ids = aiocache.caches.get("default")


async def download_task():
    while True:
        brand_name = await brand_names_queue.get()
        print(f"start_downloading: {brand_name}")
        regex_brand = f"([^a-zа-я]|^){brand_name}([^a-zа-я]|$)"
        data_from_db = await custom_orm_select(
            cls_from=[MxProductsOzon.marketplace_id],
            join_on={
                "target": MxProductsOzonBrandFix,
                "onclause": MxProductsOzonBrandFix.marketplace_id
                == MxProductsOzon.marketplace_id,
                "isouter": True,
                "full": True,
            },
            where_params=[
                MxProductsOzonBrandFix.marketplace_id == None,
                MxProductsOzon.product_name.regexp_match(regex_brand, "i"),
                MxProductsOzon.product_description.regexp_match(regex_brand, "i"),
            ],
        )
        if not data_from_db:
            brand_names_queue.task_done()
            continue

        print(f"{brand_name} found items")

        items_from_cache = await cache_marketplace_ids.multi_get(
            [x.marketplace_id for x in data_from_db]
        )
        data_from_db = list(
            compress(data_from_db, [True if not x else False for x in items_from_cache])
        )
        await cache_marketplace_ids.multi_set(
            [(x.marketplace_id, x.marketplace_id) for x in data_from_db]
        )
        batches = batch_lengh_generator(data=data_from_db, step=1000)

        for batch in batches:
            to_process_items_queue.put_nowait((batch, regex_brand))
        brand_names_queue.task_done()


async def process_task(session: aiohttp.ClientSession):
    while True:
        data_from_db, regex_brand = await to_process_items_queue.get()
        print(f"start processing: {regex_brand}")
        editor = MassProductsEditor(OzonApi(session))
        await editor.collect_products(data_from_db)
        editor.re_edit_desc(regex_brand, "")
        editor.re_edit_name(regex_brand, "")
        await editor.commit_changes()
        print("process done!")
        to_process_items_queue.task_done()


async def pipeline_with_session():
    brands_json = open_json("brands.json")
    brands = [
        x for x in brands_json if brands_json[x] != "additional verification processed"
    ]
    for brand in brands:
        brand_names_queue.put_nowait(brand)

    count_of_dowloaders = 3
    count_of_processors = 3

    async with aiohttp.ClientSession(headers=OZON_CREDENTIALS) as session:
        download_tasks = [
            asyncio.create_task(download_task()) for x in range(count_of_dowloaders)
        ]
        process_tasks = [
            asyncio.create_task(process_task(session))
            for x in range(count_of_processors)
        ]

        await brand_names_queue.join()
        await to_process_items_queue.join()

        for task in download_tasks:
            task.cancel()

        for task in process_tasks:
            task.cancel()


def main():
    my_logger = Logger("test_edit_async_brand_fix")
    asyncio.run(pipeline_with_session())
