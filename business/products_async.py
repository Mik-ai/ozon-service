from .converter import NECESSARY_FIELDS_FOR_OZON_EXPORT

from datetime import datetime

from db import mx_products_ozon_async
from db.orm.models import MxProductsOzon
from external_api.ozon_async import OzonApi

import re
import logging
import time


class MassProductsEditor:
    def __init__(self, ozon_api: OzonApi) -> None:
        self.__api = ozon_api

    def __re_sub_i(self, input: str, str_pattern: str, str_change: str) -> str:
        """internal method of editing str by regex, with ignorecase flag

        Args:
            input (str): str to edit
            str_pattern (str): regex pattern
            str_change (str): str to swap

        Returns:
            str: edited str
        """
        re_pattern = re.compile(str_pattern, re.IGNORECASE)

        return re.sub("(,$)|(, \.)", ".", re_pattern.sub(str_change, input).strip())

    async def collect_products(self, items: list) -> None:
        """set items and start collectings full_items

        Args:
            items (list): list of items from mx_product_ozon
        """
        self.items = items
        market_product_ids = [x.marketplace_id for x in self.items]
        await self.__collect_full_items(market_product_ids)
        self.items = [
            x
            for x in self.items
            if x.marketplace_id in [m["id"] for m in self.full_items]
        ]
        if not isinstance(self.items[0], MxProductsOzon):
            self.items.sort()
        if missing_products := [x for x in items if x not in self.items]:
            self.__log_missing_products(missing_products)

    def __log_missing_products(self, missing_products: list):
        """Here I am trying to catch products for which ozon cannot return information/attributes.

        Args:
            missing_products (list): list of products
        """
        messages = [
            f"{time.ctime()} warning, no attribute or info for product: {x.marketplace_id}"
            for x in missing_products
        ]
        for message in messages:
            logging.warning(message)

    def __log_test_word(self, test_word: str, check_str: str):
        """used for tracking unmodified string in case of name/description processing

        Args:
            test_word (str): str to find
            check_str (str): where to look
        """
        if test_word.lower() in check_str.lower():
            log_message = (
                f"{time.ctime()} test_word warning: {test_word} in {check_str}"
            )
            logging.warning(log_message)

    async def __collect_full_items(self, market_product_ids: list[int]) -> None:
        """load items info and items attributes from ozon, then combine it

        Args:
            market_product_ids (list): list of products ids on ozon
        """
        items_attrs = await self.__api.request_product_attributes(
            marketplace_ids=market_product_ids
        )
        items_info = await self.__api.request_products_info(
            marketplace_ids=market_product_ids
        )

        items_info = {x["id"]: x for x in items_info}
        items_attrs = {x["id"]: x for x in items_attrs}

        full_items = [dict(items_info[x], **items_attrs[x]) for x in items_info]

        self.full_items = full_items

    def change_custom_field_by_key_from_items(self, by_key: str):
        """Was made for one time operations, like setup barcode.

        Args:
            by_key (str): namedtuple/object attribute key
        """
        for index, item in enumerate(self.full_items):
            if item["id"] == self.items[index].marketplace_id:
                item[by_key] = getattr(self.items[index], by_key)

    def re_edit_name(
        self,
        re_pattern: str,
        str_change: str,
        test_word: str = None,
    ) -> None:
        """edit full_items names, also in attributes

        Args:
            re_pattern (str): regex pattern
            str_change (str): what to put
            test_word (str, optional): if name contais test_word it will go to logs. Defaults to None.
        """
        for i in self.full_items:
            i["name"] = self.__re_sub_i(i["name"], re_pattern, str_change)
            if test_word:
                self.__log_test_word(
                    test_word, i["name"] + " offer_id: " + i["offer_id"]
                )

            try:
                if attr := [x for x in i["attributes"] if x["attribute_id"] == 4180]:
                    attr = attr[0]
                    attr["values"][0]["value"] = self.__re_sub_i(
                        attr["values"][0]["value"], re_pattern, str_change
                    )
                    if test_word:
                        self.__log_test_word(
                            test_word,
                            attr["values"][0]["value"] + " offer_id: " + i["offer_id"],
                        )
            except IndexError:
                log_message = f"{time.ctime()} poduct name attribute not found, offer_id: {i['offer_id']}"
                logging.error(log_message)

    def re_edit_desc(
        self,
        re_pattern: str,
        str_change: str,
        test_word: str = None,
    ) -> None:
        """edit full_items description in attributes

        Args:
            re_pattern (str): regex pattern
            str_change (str): what to put
            test_word (str, optional): if description contais test_word it will go to logs. Defaults to None.
        """
        for i in self.full_items:
            try:
                if attr := [x for x in i["attributes"] if x["attribute_id"] == 4191]:
                    attr = attr[0]
                    attr["values"][0]["value"] = self.__re_sub_i(
                        attr["values"][0]["value"], re_pattern, str_change
                    )

                    if test_word:
                        self.__log_test_word(
                            test_word,
                            attr["values"][0]["value"] + " offer_id: " + i["offer_id"],
                        )
            except IndexError:
                log_message = f"{time.ctime()} poduct descrition attribute not found, offer_id: {i['offer_id']}"
                logging.error(log_message)

    def add_attr(self, attr: dict) -> None:
        """add attribute to full_items

        Args:
            attr (dict): attribute
        """
        for i in self.full_items:
            i["attributes"].append(attr)

    def __process_products_before_export(self):
        """ozon requires some data in specific format, so we do it here"""
        attrs = (m for x in self.full_items for m in x["attributes"])
        for i in attrs:
            if "attribute_id" in i:
                i["id"] = i.pop("attribute_id")

        # removing unnecessary fields
        products = [
            {x: m[x] for x in m if x in NECESSARY_FIELDS_FOR_OZON_EXPORT}
            for m in self.full_items
        ]
        # making product["images"] into list of str
        for i in products:
            try:
                i["images"] = [x["file_name"] for x in i["images"]]
            except:
                pass

        self.full_items = products

    async def __commit_db(self, values_list: list) -> None:
        """send to db followong changes: add to product task_id operation

        Args:
            values_list (list): list of tuples [(marketplace_id, offer_id, task_id), (marketplace_id, offer_id, task_id)...]
        """
        updated_at = datetime.now()
        data = [
            {
                "marketplace_id": x[0],
                "offer_id": x[1],
                "updated_at": updated_at,
                "task_id": x[2],
            }
            for x in values_list
        ]
        await mx_products_ozon_async.bulk_update(data)

    async def __commit_ozon(self, products: list) -> str:
        """sending update to ozon

        Args:
            items (list): list of products

        Returns:
            str: task_id from ozon
        """
        task_id = await self.__api.request_import_ozon(products)

        log_message = f"{time.ctime()} sended to ozon, task_id: {task_id}"
        logging.info(log_message)

        return task_id

    async def commit_changes(self):
        """update ozon products and commit changes to db"""
        self.__process_products_before_export()
        step = 100
        chunks = (
            self.full_items[x : x + step] for x in range(0, len(self.full_items), step)
        )
        for chunk in chunks:
            try:
                task_id = await self.__commit_ozon(chunk)
                db_values = [(x["id"], x["offer_id"], task_id) for x in chunk]
                await self.__commit_db(db_values)
            except Exception:
                log_message = f"{time.ctime()} export_error."
                logging.error(log_message)
