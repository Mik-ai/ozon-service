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
    main_field: Mapped[bool] = mapped_column(name="Main")
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
