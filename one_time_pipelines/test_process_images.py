from db.orm.schema_public import MxAsPrice, MxProductsOzon
from db.alchemy_di import custom_orm_select
from business.products import MassProductsEditor
from business.ocr_module import PyTesseractOCR

from PIL import Image
import requests


def start_test():
    ocr_inst = PyTesseractOCR()
    print()
    data = custom_orm_select(
        cls_from=MxProductsOzon,
        where_params=[
            ~MxProductsOzon.is_archived,
            MxProductsOzon.state_name.in_(["Готов к продаже", "Продается"]),
        ],
        sql_limit=10,
    )

    editor = MassProductsEditor()
    editor.collect_products(data)
    for item in editor.full_items:
        image_urls = [x["file_name"] for x in item["images"]]
        for image_url in image_urls:
            ocr_inst.download_and_process_image(image_url)
            print()

    url = "https://cdn1.ozone.ru/s3/multimedia-i/6158404482.jpg"
    img = Image.open(requests.get(url, stream=True).raw)
