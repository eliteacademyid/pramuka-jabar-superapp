from conftest import (
    headers,
    add_address,
    add_cart,
    checkout,
    demo_product,
    login,
    register,
    seller_token,
    topup,
)


def _buyer(client, name="cart_buyer"):
    register(client, name)
    return login(client, name)


def test_cart_empty(client):
    token = _buyer(client)
    r = client.get("/api/cart", headers=headers(token))
    assert r.status_code == 200
    assert r.json()["groups"] == []


def test_add_update_delete_cart(client):
    token = _buyer(client)
    product = demo_product(client)
    cart = add_cart(client, token, product["id"], 2)
    assert cart["groups"][0]["items"][0]["qty"] == 2
    assert float(cart["total"]) == float(product["price"]) * 2

    item_id = cart["groups"][0]["items"][0]["id"]
    r = client.put(f"/api/cart/items/{item_id}", json={"qty": 3}, headers=headers(token))
    assert r.json()["groups"][0]["items"][0]["qty"] == 3

    r = client.delete(f"/api/cart/items/{item_id}", headers=headers(token))
    assert r.json()["groups"] == []


def test_cart_qty_exceeds_stock(client):
    token = _buyer(client)
    product = demo_product(client)
    r = client.post(
        "/api/cart/items",
        json={"product_id": product["id"], "qty": product["stock"] + 1},
        headers=headers(token),
    )
    assert r.status_code == 400


def test_cart_unavailable_product(client):
    token = _buyer(client)
    st = seller_token(client)
    r = client.post(
        "/api/seller/products",
        json={"name": "Produk Draft", "price": 10000, "stock": 5, "status": "draft"},
        headers=headers(st),
    )
    assert r.status_code == 201
    draft = r.json()
    r = client.post("/api/cart/items", json={"product_id": draft["id"], "qty": 1}, headers=headers(token))
    assert r.status_code == 400


def test_checkout_requires_address(client):
    token = _buyer(client)
    product = demo_product(client)
    add_cart(client, token, product["id"])
    r = client.post("/api/cart/checkout", json={"address_id": 999}, headers=headers(token))
    assert r.status_code == 400


def test_checkout_empty_cart(client):
    token = _buyer(client)
    add_address(client, token)
    r = client.post("/api/cart/checkout", json={"address_id": 1}, headers=headers(token))
    assert r.status_code == 400


def test_checkout_creates_order_with_ongkir(client):
    token = _buyer(client)
    product = demo_product(client)
    add_cart(client, token, product["id"], 1)
    add_address(client, token)
    codes = checkout(client, token, 1)
    assert len(codes) == 1
    order = client.get(f"/api/orders/{codes[0]}", headers=headers(token)).json()
    expected = float(product["price"]) + 10000
    assert float(order["total"]) == expected
    assert order["status"] == "pending_payment"
    assert order["escrow_status"] == "none"


def test_checkout_different_province_ongkir_tier_c(client):
    token = _buyer(client)
    product = demo_product(client)
    add_cart(client, token, product["id"], 1)
    add_address(client, token, city="Jakarta", province="DKI Jakarta")
    codes = checkout(client, token, 1)
    order = client.get(f"/api/orders/{codes[0]}", headers=headers(token)).json()
    assert float(order["shipping_fee"]) == 25000


def test_checkout_clears_cart_and_deducts_stock(client):
    token = _buyer(client)
    product = demo_product(client)
    stock_before = product["stock"]
    add_cart(client, token, product["id"], 2)
    add_address(client, token)
    checkout(client, token, 1)
    assert client.get("/api/cart", headers=headers(token)).json()["groups"] == []
    fresh = client.get(f"/api/products/{product['slug']}").json()
    assert fresh["stock"] == stock_before - 2
