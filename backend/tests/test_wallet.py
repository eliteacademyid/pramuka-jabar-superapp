from conftest import (
    headers,
    add_address,
    add_cart,
    checkout,
    demo_product,
    login,
    pay_order,
    register,
    seller_token,
    topup,
)

ADMIN = "admin"
ADMIN_PASS = "admin123"


def _buyer(client, name="wallet_buyer"):
    register(client, name)
    return login(client, name)


def test_topup_and_wallet_detail(client):
    token = _buyer(client)
    r = client.post("/api/wallet/topup", json={"amount": 100000}, headers=headers(token))
    assert r.status_code == 200
    body = r.json()
    assert float(body["wallet"]["balance"]) == 100000
    assert body["transactions"][0]["type"] == "topup"


def test_wallet_transaction_history_after_purchase(client):
    token = _buyer(client)
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    body = client.get("/api/wallet", headers=headers(token)).json()
    types = [t["type"] for t in body["transactions"]]
    assert "topup" in types and "payment" in types


def test_withdraw_request_and_admin_approve(client):
    st = seller_token(client)
    topup(client, st, 100000)
    r = client.post(
        "/api/wallet/withdrawals",
        json={
            "amount": 50000,
            "bank_name": "BCA",
            "account_number": "1234567890",
            "account_name": "Budi Anggota",
        },
        headers=headers(st),
    )
    assert r.status_code == 201
    withdrawal = r.json()
    assert withdrawal["status"] == "pending"
    wallet = client.get("/api/wallet", headers=headers(st)).json()
    assert float(wallet["wallet"]["balance"]) == 50000

    my_list = client.get("/api/wallet/seller/withdrawals", headers=headers(st)).json()
    assert len(my_list) == 1

    admin = login(client, ADMIN, ADMIN_PASS)
    r = client.post(f"/api/admin/withdrawals/{withdrawal['id']}/approve", headers=headers(admin))
    assert r.status_code == 200
    assert r.json()["status"] == "processed"


def test_withdraw_insufficient_balance(client):
    token = _buyer(client)
    r = client.post(
        "/api/wallet/withdrawals",
        json={
            "amount": 1000,
            "bank_name": "BCA",
            "account_number": "1234567890",
            "account_name": "XY",
        },
        headers=headers(token),
    )
    assert r.status_code == 400


def test_withdraw_reject_refunds(client):
    st = seller_token(client)
    topup(client, st, 100000)
    r = client.post(
        "/api/wallet/withdrawals",
        json={
            "amount": 60000,
            "bank_name": "BCA",
            "account_number": "1234567890",
            "account_name": "Budi",
        },
        headers=headers(st),
    )
    w_id = r.json()["id"]
    admin = login(client, ADMIN, ADMIN_PASS)
    r = client.post(f"/api/admin/withdrawals/{w_id}/reject", headers=headers(admin))
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"
    wallet = client.get("/api/wallet", headers=headers(st)).json()
    assert float(wallet["wallet"]["balance"]) == 100000


def test_withdraw_double_process_rejected(client):
    st = seller_token(client)
    topup(client, st, 100000)
    r = client.post(
        "/api/wallet/withdrawals",
        json={
            "amount": 1000,
            "bank_name": "BCA",
            "account_number": "1234567890",
            "account_name": "Budi",
        },
        headers=headers(st),
    )
    w_id = r.json()["id"]
    admin = login(client, ADMIN, ADMIN_PASS)
    assert client.post(f"/api/admin/withdrawals/{w_id}/approve", headers=headers(admin)).status_code == 200
    assert client.post(f"/api/admin/withdrawals/{w_id}/approve", headers=headers(admin)).status_code == 400


def test_admin_withdrawals_requires_admin(client):
    token = _buyer(client)
    assert client.get("/api/admin/withdrawals", headers=headers(token)).status_code == 403


def test_seller_balance_grows_after_sale(client):
    token = _buyer(client)
    st = seller_token(client)
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    order_id = client.get(f"/api/orders/{code}", headers=headers(token)).json()["id"]
    client.post(f"/api/seller/orders/{order_id}/confirm", headers=headers(st))
    client.post(f"/api/seller/orders/{order_id}/ship", json={"tracking_number": "T"}, headers=headers(st))
    client.post(f"/api/orders/{code}/confirm-receipt", headers=headers(token))

    total = float(client.get(f"/api/orders/{code}", headers=headers(token)).json()["total"])
    wallet = client.get("/api/wallet", headers=headers(st)).json()
    assert float(wallet["wallet"]["balance"]) == round(total * 0.95, 2)
