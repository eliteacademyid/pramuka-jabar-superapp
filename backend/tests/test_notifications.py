from conftest import (
    add_address,
    add_cart,
    checkout,
    demo_product,
    headers,
    login,
    pay_order,
    register,
    seller_token,
    topup,
)


def _buyer(client, name="notif_buyer"):
    register(client, name)
    return login(client, name)


def _make_order(client, token):
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    return code


def _notifs(client, token):
    r = client.get("/api/notifications", headers=headers(token))
    assert r.status_code == 200
    return r.json()


def test_notify_seller_on_checkout_and_pay(client):
    buyer = _buyer(client)
    code = _make_order(client, buyer)
    st = seller_token(client)

    notifs = _notifs(client, st)
    assert any(n["ntype"] == "order" and "Pesanan baru" in n["title"] and code in n["body"] for n in notifs)
    assert notifs[0]["link"] == "/account/seller/orders"

    pay_order(client, buyer, code)
    notifs = _notifs(client, st)
    assert notifs[0]["title"] == "Pesanan dibayar"
    assert code in notifs[0]["body"]


def test_notify_buyer_on_processed_and_shipped(client):
    buyer = _buyer(client)
    code = _make_order(client, buyer)
    pay_order(client, buyer, code)
    st = seller_token(client)
    order_id = client.get("/api/seller/orders", headers=headers(st)).json()[0]["id"]

    client.post(f"/api/seller/orders/{order_id}/confirm", headers=headers(st))
    notifs = _notifs(client, buyer)
    assert notifs[0]["title"] == "Pesanan diproses"
    assert notifs[0]["link"] == f"/account/orders/{code}"

    client.post(f"/api/seller/orders/{order_id}/ship", json={"tracking_number": "JNE-123"}, headers=headers(st))
    notifs = _notifs(client, buyer)
    assert notifs[0]["title"] == "Pesanan dikirim"
    assert "JNE-123" in notifs[0]["body"]


def test_notify_chat_recipient(client):
    buyer = _buyer(client)
    product = demo_product(client)
    conv_id = client.post("/api/conversations", json={"product_id": product["id"]}, headers=headers(buyer)).json()["id"]

    client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"body": "Halo, stok masih ada?"},
        headers=headers(buyer),
    )
    st = seller_token(client)
    notifs = _notifs(client, st)
    assert notifs[0]["ntype"] == "chat"
    assert notifs[0]["title"] == "Pesan baru dari notif_buyer"
    assert notifs[0]["link"] == f"/account/chat/{conv_id}"

    buyer_notifs = _notifs(client, buyer)
    assert all(n["ntype"] != "chat" for n in buyer_notifs)


def test_unread_count_and_read_flows(client):
    buyer = _buyer(client)
    product = demo_product(client)
    conv_id = client.post("/api/conversations", json={"product_id": product["id"]}, headers=headers(buyer)).json()["id"]
    st = seller_token(client)
    client.post(f"/api/conversations/{conv_id}/messages", json={"body": "Halo"}, headers=headers(st))

    assert client.get("/api/notifications/unread-count", headers=headers(buyer)).json()["count"] == 1
    notifs = _notifs(client, buyer)
    nid = notifs[0]["id"]

    r = client.post(f"/api/notifications/{nid}/read", headers=headers(buyer))
    assert r.status_code == 200
    assert client.get("/api/notifications/unread-count", headers=headers(buyer)).json()["count"] == 0

    client.post(f"/api/conversations/{conv_id}/messages", json={"body": "Halo lagi"}, headers=headers(st))
    r = client.post("/api/notifications/read-all", headers=headers(buyer))
    assert r.status_code == 200
    assert client.get("/api/notifications/unread-count", headers=headers(buyer)).json()["count"] == 0


def test_notifications_isolated_per_user(client):
    buyer = _buyer(client)
    outsider = _buyer(client, "notif_outsider")
    product = demo_product(client)
    client.post("/api/conversations", json={"product_id": product["id"]}, headers=headers(buyer))
    assert client.get("/api/notifications/unread-count", headers=headers(outsider)).json()["count"] == 0
