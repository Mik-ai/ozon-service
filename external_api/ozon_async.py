import logging
from json_work import save_json
from yarl import URL

from config import OZON_BASE_URL, retry_async

make_request_body_jsons = False


class OzonApi:
    base_url: str
    headers: dict

    def __init__(self, session, url: str = OZON_BASE_URL) -> None:
        self.base_url = url
        self.session = session

    async def __process_post_responce(self, response, method):
        """processing post responce

        Args:
            response: post response
            method: part of url responsible for what ozon seller api method is used

        Raises:
            Exception: if response not 200

        Returns:
            list or dict (depend on what method is used): response_json["result"]
        """
        if response.status != 200:
            exception_str = (
                f"{self.base_url}{method}-{response.status_code}: {response_json}"
            )
            logging.warning(msg=exception_str)
            raise Exception(exception_str)

        response_json = await response.json()

        if "result" in response_json:
            return response_json["result"]
        else:
            return response_json

    @retry_async(5)
    async def __api_post_request(self, method: str, request_body: dict) -> dict:
        """main post request, every other method should use this

        Args:
            method (str): part of url responsible for what ozon seller api method will be used
            request_body (dict): json data of request

        """
        async with self.session.post(
            URL(self.base_url + method, encoded=True),
            json=request_body,
        ) as response:
            return await self.__process_post_responce(response, method)

    async def request_products_info(
        self, offer_ids: list[str] = [], marketplace_ids: list[int] = []
    ) -> list[dict]:
        """Method for getting an array of products by their identifiers.

        Args:
            offer_ids (list[str]): Product identifier in the seller's system.
            marketplace_ids (list[int], optional): Product identifier. Defaults to [].

        Returns:
            list[dict]: list of products
        """
        method = "/v2/product/info/list"
        request_body = {
            "offer_id": offer_ids,
            "product_id": marketplace_ids,
        }
        result = await self.__api_post_request(method, request_body)
        return result["items"]

    async def request_category_attributes(self, category_ids: list[int]) -> list[dict]:
        """Method for getting attributes for categories.

        Args:
            category_ids (list[str], optional): list of categories. Minimum is 1, maximum is 20.

        Returns:
            list[dict]: list of {"category_id": id,"attributes": [...]}
        """
        method = "/v3/category/attribute"
        request_body = {
            "attribute_type": "ALL",
            "category_id": category_ids,
        }
        result = await self.__api_post_request(method, request_body)
        return result

    async def request_one_category_attributes(self, category_id: int) -> list[dict]:
        """Method for getting attributes for category.

        Args:
            category_id (int): category

        Returns:
            list[dict]: list of {"category_id": id,"attributes": [...]}
        """
        method = "/v3/category/attribute"
        request_body = {
            "attribute_type": "ALL",
            "category_id": [category_id],
        }
        result = await self.__api_post_request(method, request_body)
        return result

    async def request_product_attributes(
        self,
        offer_ids: list[str] = [],
        marketplace_ids: list[int] = [],
        limit: int = 1000,
    ) -> list[dict]:
        """Returns a product characteristics description by product identifier.
           You can search for the product by offer_id or product_id.

        Args:
            offer_ids (list[str]): Product identifier in the seller's system.
            marketplace_ids (list[int], optional): Product identifier. Defaults to [].
            limit (int, optional): Number of values per page. Minimum is 1, maximum is 1000. Defaults to 1000.

        Returns:
            list[dict]: Array of product characteristics.
        """
        method = "/v3/products/info/attributes"
        request_body = {
            "filter": {"offer_id": offer_ids, "product_id": marketplace_ids},
            "limit": limit,
        }
        result = await self.__api_post_request(method, request_body)
        return result

    async def request_import_ozon(self, products: list) -> int:
        """This method allows you to create products and update their details

        Args:
            products_dict (dict): Array of product

        Returns:
            int: task id
        """
        method = "/v2/product/import"
        request_body = {"items": products}

        result = await self.__api_post_request(method, request_body)
        task_id = result["task_id"]
        self.log_request_body(request_body, f"{task_id} request_bodies.json")
        return task_id

    def log_request_body(self, request_body: dict, file_name: str):
        if make_request_body_jsons:
            save_json(request_body, file_name)

    async def request_product_list(
        self,
        offer_ids: list[str] = [],
        marketplace_ids: list[int] = [],
        limit: int = 100,
        custom_filter: dict = None,
    ) -> list[dict]:
        """request product list

        Args:
            offer_ids (list[str]): Product identifier in the seller's system. Defaults to [].
            marketplace_ids (list[int], optional): Product identifier. Defaults to [].
            limit (int, optional): Number of values per page. Minimum is 1, maximum is 1000. Defaults to 100.
            custom_filter (dict, optional): Additional dict of filters. Defaults None.

        Returns:
            list[dict]: product list with base informations
        """
        method = "/v2/product/list"
        request_body = {
            "filter": {
                "offer_id": offer_ids,
                "product_id": marketplace_ids,
            },
            "limit": limit,
        }

        if custom_filter:
            print("customfilter: ", custom_filter)
            request_body["filter"].update(custom_filter)
            print("request body: ", request_body)

        result = await self.__api_post_request(method, request_body)
        return result["items"]

    async def request_update_limits(self) -> dict:
        """Method for getting information about limits

        Returns:
            dict: dict with daily limits
        """
        method = "/v4/product/info/limit"
        request_body = {}
        result = await self.__api_post_request(method, request_body)
        return result
