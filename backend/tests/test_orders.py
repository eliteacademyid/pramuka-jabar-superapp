from conftest import (
    headers,
    add_address,
    add_cart,
    checkout,
    complete_purchase,
    demo_product,
    login,
    pay_order,
    register,
    seller_token,
    topup,
)


def _buyer(client, name="order_buyer"):
    register(client, name)
    return login(client, name)


def test_pay_success_escrow_held(client):
    token = _buyer(client)
    product = demo_product(client)
    topup(client, token, 200000)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]

    r = pay_order(client, token, code)
    assert r.status_code == 200
    order = r.json()
    assert order["status"] == "paid"
    assert order["escrow_status"] == "held"
    assert float(order["commission_rate"]) == 5

    wallet = client.get("/api/wallet", headers=headers(token)).json()
    spent = float(order["total"])
    assert float(wallet["wallet"]["balance"]) == 200000 - spent
    assert float(wallet["wallet"]["escrow_balance"]) == spent


def test_pay_insufficient_balance(client):
    token = _buyer(client)
    product = demo_product(client)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    r = pay_order(client, token, code)
    assert r.status_code == 400


def test_double_pay_rejected(client):
    token = _buyer(client)
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    assert pay_order(client, token, code).status_code == 200
    assert pay_order(client, token, code).status_code == 400


def test_cancel_pending_order(client):
    token = _buyer(client)
    product = demo_product(client)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    r = client.post(f"/api/orders/{code}/cancel", headers=headers(token))
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"


def test_cancel_paid_order_refunds(client):
    token = _buyer(client)
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    total = float(client.get(f"/api/orders/{code}", headers=headers(token)).json()["total"])

    r = client.post(f"/api/orders/{code}/cancel", headers=headers(token))
    assert r.status_code == 200
    assert r.json()["status"] == "refunded"
    assert r.json()["escrow_status"] == "refunded"

    wallet = client.get("/api/wallet", headers=headers(token)).json()
    assert float(wallet["wallet"]["balance"]) == 500000
    assert float(wallet["wallet"]["escrow_balance"]) == 0


def test_seller_flow_completes_with_commission(client):
    token = _buyer(client)
    product = demo_product(client)
    price = float(product["price"])
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    order_id = client.get(f"/api/orders/{code}", headers=headers(token)).json()["id"]

    st = seller_token(client)
    assert client.post(f"/api/seller/orders/{order_id}/confirm", headers=headers(st)).status_code == 200
    assert client.get(f"/api/seller/orders/{order_id}", headers=headers(st)).status_code == 200
    r = client.post(
        f"/api/seller/orders/{order_id}/ship",
        json={"tracking_number": "TRK-777"},
        headers=headers(st),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "shipped"
    assert r.json()["tracking_number"] == "TRK-777"

    r = client.post(f"/api/orders/{code}/confirm-receipt", headers=headers(token))
    assert r.status_code == 200
    order = r.json()
    assert order["status"] == "completed"
    assert order["escrow_status"] == "released"

    total = float(order["total"])
    expected_net = round(total * 0.95, 2)
    wallet = client.get("/api/wallet", headers=headers(st)).json()
    assert float(wallet["wallet"]["balance"]) == expected_net

    buyer_wallet = client.get("/api/wallet", headers=headers(token)).json()
    assert float(buyer_wallet["wallet"]["escrow_balance"]) == 0


def test_order_access_control(client):
    token = _buyer(client)
    other = _buyer(client, "other_buyer")
    product = demo_product(client)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    assert client.get(f"/api/orders/{code}", headers=headers(other)).status_code == 403
    assert client.get("/api/orders", headers=headers(other)).json() == []


def test_list_orders_filter(client):
    token = _buyer(client)
    product = demo_product(client)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    orders = client.get("/api/orders", headers=headers(token)).json()
    assert [o["order_code"] for o in orders] == [code]
    assert client.get("/api/orders", params={"status": "paid"}, headers=headers(token)).json() == []


def test_confirm_receipt_before_ship_rejected(client):
    token = _buyer(client)
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    r = client.post(f"/api/orders/{code}/confirm-receipt", headers=headers(token))
    assert r.status_code == 400


def test_seller_confirm_unpaid_order_rejected(client):
    token = _buyer(client)
    product = demo_product(client)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    order_id = client.get(f"/api/orders/{code}", headers=headers(token)).json()["id"]
    st = seller_token(client)
    assert client.post(f"/api/seller/orders/{order_id}/confirm", headers=headers(st)).status_code == 400


def test_full_purchase_helper(client):
    token = _buyer(client, "full_buyer")
    product = demo_product(client)
    code = complete_purchase(client, token, product["id"])
    order = client.get(f"/api/orders/{code}", headers=headers(token)).json()
    assert order["status"] == "completed"
    assert len(order["status_history"]) >= 5
