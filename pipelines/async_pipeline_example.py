import aiohttp
import asyncio

from business.products_async import MassProductsEditor
from external_api.ozon_async import OzonApi
from logger import Logger

from config import OZON_CREDENTIALS, batch_lengh_generator


async def update_task(products:list, **kwargs):
    """example of what u can build using async core of ozon_service

    Args:
        products list: products from DB, should have marketplace_id for collecting full_items from ozon by it,
    """
    async with kwargs["semaphore"]:
        print(f"start_updating_products first is: {products[0]}")
        api = OzonApi(session=kwargs["session"])
        editor = MassProductsEditor(api)
        await editor.collect_products(products)
        # editor.re_edit_name(re_pattern="",str_change="",test_word="")
        # await editor.commit_changes()


def create_tasks(products, **kwargs):
    """generating list of tasks, made for limiting amount of concurrent tasks by semaphore

    Args:
        products list: products from DB, should have marketplace_id for collecting full_items from ozon by it,
    """
    tasks = []
    marketplace_id_batches = batch_lengh_generator(data=products, step=1000)

    for id_batch in marketplace_id_batches:
        tasks.append(
            asyncio.create_task(update_task(products=id_batch, **kwargs))
        )


async def pipeline_with_session(products: list):
    """endpoint of editing products on ozon, created using thread pool pattern 

    Args:
        products list: products from DB, should have marketplace_id for collecting full_items from ozon by it,
    """
    semaphore = asyncio.Semaphore(3)
    async with aiohttp.ClientSession(headers=OZON_CREDENTIALS) as session:
        tasks = await create_tasks(
            products=products, semaphore=semaphore, session=session
        )
        await asyncio.gather(*tasks)


def main():
    my_logger = Logger("test", "async_tests")
    asyncio.run(pipeline_with_session())
