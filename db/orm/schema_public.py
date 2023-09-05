from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP, NUMERIC
from typing import Optional


class Base(DeclarativeBase):
    pass


class MxProductsOzon(Base):
    __tablename__ = "mx_products_ozon"

    marketplace_id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, index=True
    )
    offer_id: Mapped[str] = mapped_column(TEXT, nullable=False, index=True)
    product_id: Mapped[Optional[int]] = mapped_column(index=True)
    created_at = mapped_column(TIMESTAMP, nullable=False)
    ozon_created_at = mapped_column(TIMESTAMP)
    group_name: Mapped[Optional[str]]
    state: Mapped[str] = mapped_column(TEXT)
    state_name: Mapped[str] = mapped_column(TEXT, index=True)
    validation_state: Mapped[str] = mapped_column(TEXT)
    state_description: Mapped[str] = mapped_column(TEXT)
    item_errors: Mapped[Optional[bool]]
    box_height: Mapped[Optional[int]]
    box_length: Mapped[Optional[int]]
    box_width: Mapped[Optional[int]]
    measures_unit: Mapped[str] = mapped_column(TEXT)
    box_weight: Mapped[Optional[int]]
    weight_unit: Mapped[str] = mapped_column(TEXT)
    category_id: Mapped[Optional[int]] = mapped_column(index=True)
    updated_at = mapped_column(TIMESTAMP, nullable=False, index=True)
    decimal_measures: Mapped[bool] = mapped_column(default=False)
    price = mapped_column(NUMERIC)
    is_archived: Mapped[bool] = mapped_column(nullable=False, default=False, index=True)
    product_name: Mapped[Optional[str]] = mapped_column(TEXT)
    product_description: Mapped[Optional[str]] = mapped_column(TEXT)
    task_id: Mapped[Optional[int]]
    fbo_stock: Mapped[Optional[int]]
    fbs_stock: Mapped[Optional[int]]
    barcode: Mapped[Optional[str]] = mapped_column(TEXT)


class MxCategoryTreeMp(Base):
    __tablename__ = "mx_category_tree_mp"

    marketplace_id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, index=True
    )
    leaf_category: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, index=True
    )
    level: Mapped[int] = mapped_column(primary_key=True, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, index=True
    )

    created_at = mapped_column(TIMESTAMP, nullable=False)
    updated_at = mapped_column(TIMESTAMP, nullable=False)


class MxProductsOzonBrandFix(Base):
    __tablename__ = "mx_products_ozon_brand_fix"
    marketplace_id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    offer_id: Mapped[Optional[str]] = mapped_column(nullable=False)
    brand_found: Mapped[str] = mapped_column(nullable=False)
    found_in_name: Mapped[Optional[bool]] = mapped_column(default=False)
    found_in_descr: Mapped[Optional[bool]] = mapped_column(default=False)
    do_delete: Mapped[Optional[bool]] = mapped_column(default=False)
    created_at = mapped_column(TIMESTAMP, nullable=False)
    updated_at = mapped_column(TIMESTAMP, nullable=False)
    human_processed: Mapped[bool] = mapped_column(nullable=False, default=False)
    fixed: Mapped[bool] = mapped_column(nullable=False, default=False)


class MxAsPrice(Base):
    __tablename__ = "mx_as_Price"

    offer_id: Mapped[int] = mapped_column(name="OfferID")
    product_id: Mapped[int] = mapped_column(
        name="ProductID", nullable=False, primary_key=True
    )
    amount: Mapped[float] = mapped_column(name="Amount")
    price: Mapped[float] = mapped_column(name="Price")
    supply_price: Mapped[float] = mapped_column(name="SupplyPrice")
    color_id: Mapped[float] = mapped_column(name="ColorID")
    size_id: Mapped[float] = mapped_column(name="SizeID")
    art_no = mapped_column(TEXT, name="ArtNo")
    main_column: Mapped[bool] = mapped_column(name="Main")
    length: Mapped[float] = mapped_column(name="Length", index=True)
    width: Mapped[float] = mapped_column(name="Width", index=True)
    height: Mapped[float] = mapped_column(name="Height", index=True)
    weight: Mapped[float] = mapped_column(name="Weight", index=True)
    barcode = mapped_column(TEXT, name="BarCode")


class MxAssosiassionsProductsRsSl(Base):
    __tablename__ = "mx_assosiassions_products_rs_sl"

    id: Mapped[int] = mapped_column(primary_key=True)
    rs_product_id: Mapped[int] = mapped_column(nullable=False)
    sl_product_id: Mapped[int] = mapped_column(nullable=False)
    created_at = mapped_column(TIMESTAMP, nullable=False)
    updated_at = mapped_column(TIMESTAMP, nullable=False)


class MxAsProduct(Base):
    __tablename__ = "mx_as_Product"

    product_id: Mapped[int] = mapped_column("ProductID", primary_key=True)
    offer_id: Mapped[str] = mapped_column("ArtNo")


class MxSlItem(Base):
    __tablename__ = "mx_sl_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[int] = mapped_column("sid")
    product_id: Mapped[int] = mapped_column("product_id")


class MkProductsOzonFrank(Base):
    __tablename__ = "mk_products_ozon_frank"

    marketplace_id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    task_id: Mapped[int] = mapped_column(nullable=False)
    created_at = mapped_column(TIMESTAMP, nullable=False)
    updated_at = mapped_column(TIMESTAMP, nullable=False)
    price = mapped_column(NUMERIC, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)


class MxAsProduct(Base):
    product_id: Mapped[int] = mapped_column(name="ProductId", nullable=False)
    art_no: Mapped[str] = mapped_column(name="ArtNo", index=True)
    name: Mapped[str] = mapped_column(name="Name")
    description: Mapped[str] = mapped_column(name="Description")
    date_added = mapped_column(TIMESTAMP, name="DateAdded", index=True)
    brand_id: Mapped[float] = mapped_column(name="BrandID", index=True)
    min_amount: Mapped[float] = mapped_column(name="MinAmount")
    max_amoun: Mapped[str] = mapped_column(name="MaxAmount")
    multiplicity: Mapped[float] = mapped_column(name="Multiplicity")
    main_category: Mapped[int] = mapped_column(name="main_category", index=True)


class ProductPropertyValue(Base):
    product_id: Mapped[int] = mapped_column(name="ProductID", index=True)
    property_value_id: Mapped[int] = mapped_column(name="PropertyValueID", index=True)


class PropertyValue(Base):
    propertyValue_id: Mapped[int] = mapped_column(name="PropertyValueID", index=True)
    property_id: Mapped[int] = mapped_column(name="PropertyID", index=True)
    value: Mapped[str] = mapped_column(name="Value", index=True)
    sort_order: Mapped[float] = mapped_column(name="SortOrder")
    use_in_filter: Mapped[bool] = mapped_column(name="UseInFilter")
    use_in_details: Mapped[bool] = mapped_column(name="UseInDetails")
    range_value: Mapped[float] = mapped_column(name="RangeValue")
    use_in_brief: Mapped[bool] = mapped_column(name="UseInBrief")


class Property(Base):
    PropertyID: Mapped[int] = mapped_column(
        name="PropertyID", primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(name="Name")
    use_in_filter: Mapped[bool] = mapped_column(name="UseInFilter")
    sort_order: Mapped[int] = mapped_column(name="SortOrder")
    expanded: Mapped[bool] = mapped_column(name="Expanded")
    use_in_details: Mapped[bool] = mapped_column(name="UseInDetails")
    description: Mapped[str] = mapped_column(name="Description")
    unit: Mapped[str] = mapped_column(name="Unit")
    type: Mapped[int] = mapped_column(name="Type")
    group_id: Mapped[float] = mapped_column(name="GroupId")
    use_in_brief: Mapped[bool] = mapped_column(name="UseInBrief")
    name_displayed: Mapped[str] = mapped_column(name="NameDisplayed")


class Price(Base):
    offer_id: Mapped[int] = mapped_column(name="OfferID")
    product_id: Mapped[int] = mapped_column(name="ProductID")
    amount: Mapped[float] = mapped_column(name="Amount")
    price: Mapped[float] = mapped_column(name="Price")
    supply_price: Mapped[float] = mapped_column(name="SupplyPrice")
    color_id: Mapped[float] = mapped_column(name="ColorID")
    size_id: Mapped[float] = mapped_column(name="SizeID")
    art_no: Mapped[str] = mapped_column(name="ArtNo")
    main: Mapped[bool] = mapped_column(name="Main")
    length: Mapped[float] = mapped_column(name="Length")
    width: Mapped[float] = mapped_column(name="Width")
    height: Mapped[float] = mapped_column(name="Height")
    weight: Mapped[float] = mapped_column(name="Weight")
    bar_code: Mapped[str] = mapped_column(name="BarCode")


class Photo(Base):
    photo_id: Mapped[int] = mapped_column(name="PhotoId")
    obj_id: Mapped[int] = mapped_column(name="ObjId", index=True)
    type: Mapped[str] = mapped_column(name="Type")
    photo_name: Mapped[str] = mapped_column(name="PhotoName")
    modified_date = mapped_column(TIMESTAMP, name="ModifiedDate")
    description: Mapped[str] = mapped_column(name="Description")
    photo_sort_order: Mapped[float] = mapped_column(name="PhotoSortOrder")
    main: Mapped[bool] = mapped_column(name="Main", index=True)
    origin_name: Mapped[str] = mapped_column(name="OriginName")
    color_id: Mapped[str] = mapped_column(name="ColorID")
    photo_name_size1: Mapped[str] = mapped_column(name="PhotoNameSize1")
    photo_name_size2: Mapped[str] = mapped_column(name="PhotoNameSize2")
