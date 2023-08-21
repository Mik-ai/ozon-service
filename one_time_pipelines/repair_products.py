from json_work import open_json, save_json
from db.alchemy_di import (
    custom_orm_select,
)
from db.orm.models import MxProductsOzon, MkProductsOzonFrank
from db.orm.temp_models import Photo
from business.products import MassProductsEditor
from external_api.ozon import OzonApi
from config import batch_lengh_generator
from sqlalchemy import update
from logger import Logger

from difflib import SequenceMatcher

# str1 = "Футболка для девочки, цвет лиловый/попугай, рост 128 см "
# str2 = "Футболка для девочки, цвет лиловый/попугай, рост 135 см "
# SequenceMatcher(None, str1, str2).ratio()


def append_items_json(items: dict):
    file_name = "fuckup_items_info.json"
    data = open_json(file_name)
    data = dict(data, **items)
    save_json(data, file_name)


def start_rapair_really_fuckup():
    logger = Logger("repair_really_fuckdup")
    editor = MassProductsEditor()
    data = open_json("really_fuckedup_products.json")
    really_fuckedup_products = data["items"]
    marketplace_ids = [m for x in really_fuckedup_products for m in x]

    data_from_db = custom_orm_select(
        [MxProductsOzon.marketplace_id, MxProductsOzon.offer_id],
        where_params=[
            MxProductsOzon.marketplace_id.in_(marketplace_ids),
            MxProductsOzon.product_id != None,
        ],
    )
    photo_from_db = custom_orm_select(
        cls_from=[Photo.ObjId, MxProductsOzon.marketplace_id, Photo.PhotoName],
        join_on=[MxProductsOzon, Photo.ObjId == MxProductsOzon.product_id],
        where_params=[MxProductsOzon.marketplace_id.in_(marketplace_ids)],
    )

    photo_dict = {x.marketplace_id: [] for x in photo_from_db}
    for i in photo_from_db:
        photo_dict[i.marketplace_id] += [i.PhotoName]

    for chunk in batch_lengh_generator(1000, data_from_db):
        print(f"processing chunk first item is: {chunk[0]}")
        editor.collect_products(chunk)

        for item in editor.full_items:
            try:
                print(f"{item['id']} has have - ", item["primary_image"])
                item["primary_image"], *item["images"] = photo_dict[item["id"]]
                item["images"] = item["images"][:14]

            except:
                print(f"no image for: {item['id']}")
        print("debug")
        editor.commit_changes()

    print("done!")


def create_really_fuckup():
    api = OzonApi()
    data = open_json("fuckup_products.json")
    data = batch_lengh_generator(500, data["items"])

    really_fuckedup_products = []

    for fuckup_pairs in data:
        marketplace_ids = [m for x in fuckup_pairs for m in x]
        products_info = api.request_products_info(marketplace_ids=marketplace_ids)
        products_info_dict = {x["id"]: x for x in products_info}

        really_fuckedup_products += [
            (x[0], x[1])
            for x in fuckup_pairs
            if SequenceMatcher(
                None,
                products_info_dict[x[0]]["name"],
                products_info_dict[x[1]]["name"],
            ).ratio()
            < 0.3
        ]

    save_json(
        data={"items": really_fuckedup_products},
        file_name="really_fuckedup_products.json",
    )

    print("debug")
    print("debug")
    print("debug")


def process_fuckup_products():
    result = open_json("info_500k_data.json")
    result = [result[x] for x in result]

    len([image for x in result for image in x["images"] if image != ""])

    images_dicts = {
        image: x["id"] for x in result for image in x["images"] if image != ""
    }
    prim_image_dicts = {
        x["primary_image"]: x["id"] for x in result if x["primary_image"] != ""
    }

    fuckup_items = []

    for prim_image in prim_image_dicts:
        try:
            fuckup_items.append(
                (prim_image_dicts[prim_image], images_dicts[prim_image])
            )
        except:
            pass

    # empty_prim_image = [x["id"] for x in result if x["primary_image"] == ""]
    # fuckup_items = [x for x in fuckup_items if x[0] not in empty_prim_image]

    save_json({"items": fuckup_items}, "fuckup_products.json")

    check_products = [x for x in fuckup_items][:10]

    products_from_db = custom_orm_select(
        cls_from=[MxProductsOzon.marketplace_id, MxProductsOzon.offer_id],
        where_params=[
            MxProductsOzon.marketplace_id.in_([m for x in check_products for m in x])
        ],
    )
    products_dict = {x.marketplace_id: x.offer_id for x in products_from_db}

    [(products_dict[x[0]], products_dict[x[1]]) for x in check_products]

    print("done!")
    print("done!")
    print("done!")


def start_process_mk_franks():
    api = OzonApi()
    editor = MassProductsEditor()

    mk_data = custom_orm_select(
        cls_from=[
            MkProductsOzonFrank.marketplace_id,
            MkProductsOzonFrank.is_deleted,
            MkProductsOzonFrank.price,
        ],
        where_params=[MkProductsOzonFrank.is_deleted == False],
    )
    batches_1k_marketplace_ids = batch_lengh_generator(1000, mk_data)

    result = []

    for batch in batches_1k_marketplace_ids:
        print(f"start downloading items info, first item is {batch[0].marketplace_id}")
        marketplace_ids = [x.marketplace_id for x in batch]
        products_info = api.request_products_info(marketplace_ids=marketplace_ids)
        result += products_info
    # save_json(file_name="info_500k_data", data={x["id"]:x for x in result})

    print("done!")
    print("done!")
    print("done!")


def test_rapair_lamp():
    my_loggs = Logger("repair_product")

    data = open_json("repair.json")
    data = data["items"]
    product_ids = [x["product_id"] for x in data]

    test_data = custom_orm_select(
        cls_from=MkProductsOzonFrank,
        where_params=[MkProductsOzonFrank.marketplace_id.in_(product_ids)],
    )

    # lamps_mar_id = [454540157, 454540285]
    editor = MassProductsEditor()

    lamps_prod_ozon = custom_orm_select(
        cls_from=[
            MxProductsOzon.marketplace_id,
            MxProductsOzon.product_id,
            MxProductsOzon.price,
        ],
        where_params=[MxProductsOzon.marketplace_id.in_(product_ids)],
    )
    prod_ozon_dict_by_m_id = {x.marketplace_id: x for x in lamps_prod_ozon}

    lamps_photos = custom_orm_select(
        cls_from=[Photo.ObjId, MxProductsOzon.marketplace_id, Photo.PhotoName],
        join_on=[MxProductsOzon, Photo.ObjId == MxProductsOzon.product_id],
        where_params=[Photo.ObjId.in_([x.product_id for x in lamps_prod_ozon])],
    )

    # формирование списка фоток для конкретного product_id из разрозненных данных
    photos_dict = {x.marketplace_id: [] for x in lamps_photos}
    for photo in lamps_photos:
        photos_dict[photo.marketplace_id] += [photo.PhotoName]

    editor.collect_products(lamps_prod_ozon)

    for item in editor.full_items:
        if item["price"] == str(prod_ozon_dict_by_m_id[item["id"]].price):
            continue
        item["price"] = str(prod_ozon_dict_by_m_id[item["id"]].price)
        try:
            print(f"{item['id']} has have - ", item["primary_image"])
            # prduct_id = prod_ozon_dict_by_m_id[item["id"]].product_id
            item["primary_image"], *item["images"] = photos_dict[item["id"]]
            item["images"] = item["images"][:14]

        except:
            print(f"no image for: {item['id']}")
    print("debug")
    print("debug")

    editor.commit_changes()
    print("debug")
    print("debug")
    print("debug")


def start_repair():
    data = open_json("repair.json")
    ozon_product_ids = [x["product_id"] for x in data["items"]]

    api = OzonApi()
    data_info = api.request_products_info(marketplace_ids=ozon_product_ids)
    data_attrs = api.request_product_attributes(marketplace_ids=ozon_product_ids)

    primary_images_dict = {x["id"]: x["primary_image"] for x in data_info}

    repairing_pairs = []

    images_attrs = {x["id"]: x["images"] for x in data_attrs}

    for marketplace_id in primary_images_dict:
        for image in images_attrs:
            if (
                primary_images_dict[marketplace_id]
                in " ".join([x["file_name"] for x in images_attrs[image]])
                and marketplace_id != image
            ):
                repairing_pairs.append((marketplace_id, image))

    print("debug")
    print("debug")
    print("debug")
