from db import mx_products_ozon
import logging
import time
from pipelines.pipelines import default_pipeline_edit_name_and_description
from logger import set_logger
from json_work import open_json, save_json

regex_whole_sentence = "(?![!\.?])[^\.!?]*интернет-магази.*([\.!]|$)"


def set_logger(name_param: str = None):
    logging.basicConfig(
        filename=f"{time.strftime('%d-%m-%Y')} {name_param if name_param else ''}.log",
        encoding="utf-8",
        level=logging.DEBUG,
    )


def update_mixs():
    set_logger("update_mixs")

    re_parts = [
        '(((цвет((а)|(ов)|( корпуса)|()))|(рисунок)|(виды)|(\(цвет корпуса\))|())([ :,]{1,2}|^)[«"]?микс["»]?[^А-яёA-z0-9]?)',
        "( микс[^А-яёA-z0-9]{1,2}((\(штрихкод на штуке\))|(цвет((а)|(ов)|()))))",
        "(Микс означает, что.*представлены не все варианты\.)",
        "(Пометка «МИКС» означает.*(так и все разного|из ассортимента нашего сайта|так и все разные|так и все одинаковых оттенков|так и все разных)\.)",
        "цв.микс|см.МИКС",
        "(розовый|голубой|жёлтый|серый|молочный|оранжевый|светло-бирюзовый|белый)/микс",
    ]
    re_pattern = "|".join(re_parts)
    test_word = "микс"

    items = mx_products_ozon.select_regex_in_name_or_descr(re_pattern)
    default_pipeline_edit_name_and_description(items, re_pattern, test_word)


def update_word_in_sentence(word: str):
    re_pattern = f'([^A-zА-яё]|^)["]?{word}["]?[^A-zА-яё.-]?'
    items = mx_products_ozon.select_regex_in_name_or_descr(re_pattern)

    default_pipeline_edit_name_and_description(items, re_pattern, word)


def update_brands_delete_anyway():
    set_logger("brands_removing")

    data = open_json()

    for brand_name in data:
        if not data[brand_name] == "delete anyway":
            continue
        try:
            print(f"processing brand: {brand_name}")
            update_word_in_sentence(brand_name)
            data[brand_name] = "processed"
            save_json(data)

            log_message = f"{time.ctime()} brand: {brand_name} processed."
        except Exception as e:
            log_message = (
                f"{time.ctime()} brand: {brand_name} unable to process. Exception: {e}"
            )
            logging.error(log_message)


if __name__ == "__main__":
    update_brands_delete_anyway()
