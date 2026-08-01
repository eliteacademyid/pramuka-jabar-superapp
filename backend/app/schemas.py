from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import ACCOUNT_TYPES, ROLES


# ---------- Auth & User ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    nama_lengkap: str = Field(min_length=1, max_length=100)
    email: Optional[str] = None
    account_type: str = "umum"
    scout_number: Optional[str] = None
    kwartir: Optional[str] = None
    golongan: Optional[str] = None

    @field_validator("account_type")
    @classmethod
    def _check_account_type(cls, v: str) -> str:
        if v not in ACCOUNT_TYPES:
            raise ValueError("account_type harus 'anggota' atau 'umum'")
        return v


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    nama_lengkap: str
    role: str = "staff"

    @field_validator("role")
    @classmethod
    def _check_role(cls, v: str) -> str:
        if v not in ROLES:
            raise ValueError("Role tidak valid")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    nama_lengkap: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class ProfileUpdate(BaseModel):
    nama_lengkap: Optional[str] = None
    email: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nama_lengkap: str
    email: Optional[str] = None
    account_type: str
    scout_number: Optional[str] = None
    kwartir: Optional[str] = None
    golongan: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class WalletOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    balance: Decimal
    escrow_balance: Decimal


class StoreSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    status: str


class MeOut(BaseModel):
    user: UserOut
    wallet: Optional[WalletOut] = None
    store: Optional[StoreSummary] = None


class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Address ----------

class AddressCreate(BaseModel):
    label: str = "rumah"
    address_line: str = Field(min_length=3)
    city: str = Field(min_length=2)
    province: str = Field(min_length=2)
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    is_primary: bool = False


class AddressUpdate(BaseModel):
    label: Optional[str] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    is_primary: Optional[bool] = None


class AddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    address_line: str
    city: str
    province: str
    postal_code: Optional[str]
    phone: Optional[str]
    is_primary: bool


# ---------- Category ----------

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


# ---------- Store ----------

class StoreCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None
    city: str = Field(min_length=2)
    province: str = Field(min_length=2)
    phone: Optional[str] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    city: Optional[str] = None
    province: Optional[str] = None
    phone: Optional[str] = None


class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    slug: str
    description: Optional[str]
    category_id: Optional[int]
    city: str
    province: str
    phone: Optional[str]
    status: str
    reject_reason: Optional[str]
    created_at: datetime


class StorePublicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str]
    city: str
    province: str
    phone: Optional[str]
    rating: Optional[Decimal] = None
    products: Optional[List["ProductOut"]] = None


# ---------- Product ----------

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    unit: Optional[str] = None
    images: Optional[List[str]] = None
    status: str = "draft"


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    unit: Optional[str] = None
    images: Optional[List[str]] = None
    status: Optional[str] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_id: int
    category_id: Optional[int]
    name: str
    slug: str
    description: Optional[str]
    price: Decimal
    stock: int
    unit: Optional[str]
    images: Optional[List[str]]
    status: str
    sold: int
    rating: Optional[Decimal] = None
    created_at: datetime


class ProductPublicOut(ProductOut):
    store: Optional[StoreSummary] = None
    reviews: Optional[List["ReviewOut"]] = None
    out_of_stock: bool = False


class ProductPage(BaseModel):
    items: List[ProductPublicOut]
    total: int
    page: int
    size: int


# ---------- Cart ----------

class CartAdd(BaseModel):
    product_id: int
    qty: int = Field(default=1, ge=1)


class CartUpdate(BaseModel):
    qty: int = Field(ge=1)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    name: str
    slug: str
    price: Decimal
    qty: int
    subtotal: Decimal
    stock: int
    image: Optional[str] = None
    out_of_stock: bool


class CartStoreGroup(BaseModel):
    store_id: int
    store_name: str
    store_slug: str
    items: List[CartItemOut]
    subtotal: Decimal


class CartOut(BaseModel):
    groups: List[CartStoreGroup]
    total: Decimal


# ---------- Order ----------

class CheckoutRequest(BaseModel):
    address_id: int


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    qty: int
    total: Decimal


class OrderStatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    note: Optional[str]
    created_at: datetime


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_code: str
    buyer_id: int
    store_id: int
    store_name: Optional[str] = None
    address_snapshot: Optional[dict]
    subtotal: Decimal
    shipping_fee: Decimal
    discount: Decimal
    total: Decimal
    status: str
    escrow_status: str
    commission_rate: Optional[Decimal]
    tracking_number: Optional[str]
    created_at: datetime
    items: List[OrderItemOut] = []
    status_history: List[OrderStatusHistoryOut] = []


class CheckoutResult(BaseModel):
    orders: List[str]


# ---------- Wallet ----------

class TopupRequest(BaseModel):
    amount: Decimal = Field(gt=0)


class WalletTxOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    amount: Decimal
    ref_type: Optional[str]
    ref_id: Optional[int]
    balance_after: Decimal
    note: Optional[str]
    created_at: datetime


class WalletDetailOut(BaseModel):
    wallet: WalletOut
    transactions: List[WalletTxOut]


class WithdrawRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    bank_name: str = Field(min_length=2)
    account_number: str = Field(min_length=5)
    account_name: str = Field(min_length=2)


class WithdrawalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    bank_name: str
    account_number: str
    account_name: str
    status: str
    note: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]


# ---------- Review ----------

class ReviewCreate(BaseModel):
    order_item_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_item_id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str]
    status: str
    created_at: datetime
    username: Optional[str] = None


# ---------- Chat ----------

class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_id: int
    sender_name: Optional[str] = None
    body: str
    read_at: Optional[datetime]
    created_at: datetime


class ConversationOut(BaseModel):
    id: int
    order_code: str
    order_status: str
    created_at: datetime
    participants: List[str] = []


# ---------- Admin ----------

class StoreModerate(BaseModel):
    reason: Optional[str] = None


class AdminReport(BaseModel):
    users: int
    stores: int
    products: int
    orders_by_status: dict
    transaction_volume: Decimal
    period_days: int


class AdminCartItemOut(BaseModel):
    product_id: int
    name: str
    price: Decimal
    qty: int
    subtotal: Decimal


class AdminCartEntryOut(BaseModel):
    user_id: int
    username: str
    nama_lengkap: str
    is_active: bool
    item_count: int
    qty_total: int
    subtotal: Decimal
    updated_at: Optional[datetime]
    items: List[AdminCartItemOut]


class SellerDashboardOut(BaseModel):
    active_products: int
    orders_by_status: dict
    total_sales: Decimal
    balance: Decimal
    escrow_balance: Decimal


# forward refs
StorePublicOut.model_rebuild()
ProductPublicOut.model_rebuild()
ProductOut.model_rebuild()
