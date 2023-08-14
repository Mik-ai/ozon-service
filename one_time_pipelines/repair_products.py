from json_work import open_json, save_json
from db.alchemy_di import custom_orm_select
from db.orm.models import MxProductsOzon
from db.orm.temp_models import Photo
from business.products import MassProductsEditor
from external_api.ozon import OzonApi


def test_rapair_lap():
    lamps_mar_id = [454540157, 454540285]
    editor = MassProductsEditor()

    lamps_prod_ozon = custom_orm_select(
        cls_from=[
            MxProductsOzon.marketplace_id,
            MxProductsOzon.product_id,
            MxProductsOzon.price,
        ],
        where_params=[MxProductsOzon.marketplace_id.in_(lamps_mar_id)],
    )
    lamps_prod_ozon_dict_by_m_id = {x.marketplace_id: x for x in lamps_prod_ozon}

    lamps_photos = custom_orm_select(
        cls_from=[Photo.ObjId, Photo.PhotoName],
        where_params=[
            Photo.ObjId.in_([x.product_id for x in lamps_prod_ozon] + [26121])
        ],
    )
    # формирование списка фоток для конкретного product_id из разрозненных данных
    photos_dict = {x.ObjId: [] for x in lamps_photos}
    for photo in lamps_photos:
        photos_dict[photo.ObjId] += [photo.PhotoName]

    editor.collect_products(lamps_prod_ozon)

    for item in editor.full_items:
        item["price"] = str(lamps_prod_ozon_dict_by_m_id[item["id"]].price)
        try:
            print(f"{item['id']} has have - ", item["primary_image"])
            prduct_id = lamps_prod_ozon_dict_by_m_id[item["id"]].product_id
            item["primary_image"], *item["images"] = photos_dict[prduct_id]

        except:
            print(f"no image for: {item['id']}")
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
