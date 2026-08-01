from conftest import (
    headers,
    complete_purchase,
    demo_product,
    login,
    register,
)


def _buyer(client, name="review_buyer"):
    register(client, name)
    return login(client, name)


def _order_item_id(client, token, code):
    order = client.get(f"/api/orders/{code}", headers=headers(token)).json()
    return order["items"][0]["id"]


def test_review_completed_order(client):
    token = _buyer(client)
    product = demo_product(client)
    code = complete_purchase(client, token, product["id"])
    item_id = _order_item_id(client, token, code)

    r = client.post(
        "/api/reviews",
        json={"order_item_id": item_id, "rating": 5, "comment": "Bagus sekali!"},
        headers=headers(token),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["rating"] == 5
    assert body["status"] == "visible"
    assert body["username"] is not None


def test_review_not_completed_rejected(client):
    from conftest import add_address, add_cart, checkout, topup, pay_order

    token = _buyer(client)
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    item_id = _order_item_id(client, token, code)

    r = client.post(
        "/api/reviews", json={"order_item_id": item_id, "rating": 4}, headers=headers(token)
    )
    assert r.status_code == 400


def test_duplicate_review_rejected(client):
    token = _buyer(client)
    product = demo_product(client)
    code = complete_purchase(client, token, product["id"])
    item_id = _order_item_id(client, token, code)
    payload = {"order_item_id": item_id, "rating": 5}
    assert client.post("/api/reviews", json=payload, headers=headers(token)).status_code == 201
    assert client.post("/api/reviews", json=payload, headers=headers(token)).status_code == 400


def test_review_invalid_rating(client):
    token = _buyer(client)
    product = demo_product(client)
    code = complete_purchase(client, token, product["id"])
    item_id = _order_item_id(client, token, code)
    for rating in (0, 6):
        r = client.post(
            "/api/reviews", json={"order_item_id": item_id, "rating": rating}, headers=headers(token)
        )
        assert r.status_code == 422


def test_review_appears_in_product_detail_with_rating(client):
    token = _buyer(client)
    product = demo_product(client)
    code = complete_purchase(client, token, product["id"])
    item_id = _order_item_id(client, token, code)
    client.post(
        "/api/reviews",
        json={"order_item_id": item_id, "rating": 4, "comment": "Mantap"},
        headers=headers(token),
    )

    detail = client.get(f"/api/products/{product['slug']}").json()
    assert len(detail["reviews"]) == 1
    assert detail["reviews"][0]["comment"] == "Mantap"
    assert float(detail["rating"]) == 4.0


def test_review_for_other_buyer_rejected(client):
    token = _buyer(client, "review_owner")
    other = _buyer(client, "review_other")
    product = demo_product(client)
    code = complete_purchase(client, token, product["id"])
    item_id = _order_item_id(client, token, code)
    r = client.post(
        "/api/reviews", json={"order_item_id": item_id, "rating": 5}, headers=headers(other)
    )
    assert r.status_code == 400
