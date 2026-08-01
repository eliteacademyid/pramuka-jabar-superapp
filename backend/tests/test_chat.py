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


def _buyer(client, name="chat_buyer"):
    register(client, name)
    return login(client, name)


def _make_order(client, token):
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    return code


def test_conversation_auto_created_on_checkout(client):
    token = _buyer(client)
    code = _make_order(client, token)
    r = client.get("/api/conversations", headers=headers(token))
    assert r.status_code == 200
    convs = r.json()
    assert len(convs) == 1
    assert convs[0]["order_code"] == code
    participants = convs[0]["participants"]
    assert "chat_buyer" in participants
    assert "member_budi" in participants
    assert "admin" in participants


def test_send_and_list_messages(client):
    buyer = _buyer(client)
    _make_order(client, buyer)
    conv_id = client.get("/api/conversations", headers=headers(buyer)).json()[0]["id"]

    r = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"body": "Halo, masih ada stok?"},
        headers=headers(buyer),
    )
    assert r.status_code == 201
    assert r.json()["sender_name"] == "chat_buyer"

    st = seller_token(client)
    msgs = client.get(f"/api/conversations/{conv_id}/messages", headers=headers(st)).json()
    assert len(msgs) == 1
    assert msgs[0]["body"] == "Halo, masih ada stok?"
    assert msgs[0]["read_at"] is not None


def test_message_body_validation(client):
    buyer = _buyer(client)
    _make_order(client, buyer)
    conv_id = client.get("/api/conversations", headers=headers(buyer)).json()[0]["id"]
    r = client.post(f"/api/conversations/{conv_id}/messages", json={"body": ""}, headers=headers(buyer))
    assert r.status_code == 422


def test_participants_only_access(client):
    buyer = _buyer(client, "chat_owner")
    outsider = _buyer(client, "chat_outsider")
    _make_order(client, buyer)
    conv_id = client.get("/api/conversations", headers=headers(buyer)).json()[0]["id"]

    assert client.get(f"/api/conversations/{conv_id}/messages", headers=headers(outsider)).status_code == 403
    r = client.post(
        f"/api/conversations/{conv_id}/messages",
        json={"body": "Halo?"},
        headers=headers(outsider),
    )
    assert r.status_code == 403
    assert client.get("/api/conversations", headers=headers(outsider)).json() == []


def test_admin_sees_all_conversations(client):
    buyer = _buyer(client)
    _make_order(client, buyer)
    admin = login(client, "admin", "admin123")
    convs = client.get("/api/conversations", headers=headers(admin)).json()
    assert len(convs) == 1
    assert client.get(f"/api/conversations/{convs[0]['id']}/messages", headers=headers(admin)).status_code == 200
