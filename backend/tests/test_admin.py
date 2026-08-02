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

ADMIN = "admin"
ADMIN_PASS = "admin123"


def _admin(client):
    return login(client, ADMIN, ADMIN_PASS)


def _staff(client):
    a = _admin(client)
    r = client.post(
        "/api/admin/users",
        json={"username": "staff_one", "password": "staffpass1", "nama_lengkap": "Staf Satu", "role": "staff"},
        headers=headers(a),
    )
    assert r.status_code == 201
    return login(client, "staff_one", "staffpass1")


def test_admin_users_list_requires_admin(client):
    token = login(client, "member_budi")
    assert client.get("/api/admin/users", headers=headers(token)).status_code == 403
    a = _admin(client)
    r = client.get("/api/admin/users", headers=headers(a))
    assert r.status_code == 200
    usernames = [u["username"] for u in r.json()]
    assert "admin" in usernames and "member_budi" in usernames


def test_admin_create_update_delete_user(client):
    a = _admin(client)
    r = client.post(
        "/api/admin/users",
        json={"username": "staff_new", "password": "pass1234", "nama_lengkap": "Staf Baru", "role": "staff"},
        headers=headers(a),
    )
    assert r.status_code == 201
    user_id = r.json()["id"]

    assert client.post(
        "/api/admin/users",
        json={"username": "staff_new", "password": "pass1234", "nama_lengkap": "Dup", "role": "staff"},
        headers=headers(a),
    ).status_code == 400

    r = client.put(f"/api/admin/users/{user_id}", json={"role": "admin"}, headers=headers(a))
    assert r.status_code == 200
    assert r.json()["role"] == "admin"

    r = client.put(f"/api/admin/users/{user_id}", json={"is_active": False}, headers=headers(a))
    assert r.json()["is_active"] is False

    assert client.delete(f"/api/admin/users/{user_id}", headers=headers(a)).status_code == 204


def test_admin_cannot_delete_self(client):
    a = _admin(client)
    admin_id = client.get("/api/admin/users", headers=headers(a)).json()[0]["id"]
    assert client.delete(f"/api/admin/users/{admin_id}", headers=headers(a)).status_code == 400


def test_staff_can_view_stores_products_orders(client):
    st = _staff(client)
    assert client.get("/api/admin/stores", headers=headers(st)).status_code == 200
    assert client.get("/api/admin/products", headers=headers(st)).status_code == 200
    assert client.get("/api/admin/orders", headers=headers(st)).status_code == 200
    assert client.get("/api/admin/reports", headers=headers(st)).status_code == 200
    assert client.get("/api/admin/withdrawals", headers=headers(st)).status_code == 200


def test_admin_carts_per_user(client):
    a = _admin(client)
    r = client.get("/api/admin/carts", headers=headers(a))
    assert r.status_code == 200
    entries = {e["user_id"]: e for e in r.json()}
    assert all(e["item_count"] == 0 and e["subtotal"] == "0.00" for e in entries.values())

    register(client, "cart_watcher")
    buyer = login(client, "cart_watcher")
    product = demo_product(client)
    add_cart(client, buyer, product["id"], qty=3)

    st = _staff(client)
    entries = {e["user_id"]: e for e in client.get("/api/admin/carts", headers=headers(st)).json()}
    buyer_id = next(
        u["id"] for u in client.get("/api/admin/users", headers=headers(a)).json()
        if u["username"] == "cart_watcher"
    )
    entry = entries[buyer_id]
    assert entry["item_count"] == 1
    assert entry["qty_total"] == 3
    assert float(entry["subtotal"]) == float(product["price"]) * 3
    assert entry["items"][0]["name"] == product["name"]
    assert entry["items"][0]["qty"] == 3
    assert entry["updated_at"] is not None


def test_admin_approve_reject_store_flow(client):
    a = _admin(client)
    register(client, "seller_flow")
    st = login(client, "seller_flow")
    r = client.post(
        "/api/seller/store",
        json={"name": "Toko Flow", "city": "Bandung", "province": "Jawa Barat"},
        headers=headers(st),
    )
    store_id = r.json()["id"]

    r = client.post(f"/api/admin/stores/{store_id}/reject", json={}, headers=headers(a))
    assert r.status_code == 422
    r = client.post(f"/api/admin/stores/{store_id}/reject", json={"reason": "ab"}, headers=headers(a))
    assert r.status_code == 422

    r = client.post(
        f"/api/admin/stores/{store_id}/reject", json={"reason": "Dokumen kurang lengkap"}, headers=headers(a)
    )
    assert r.status_code == 200
    assert r.json()["status"] == "rejected"
    assert r.json()["reject_reason"] == "Dokumen kurang lengkap"

    r = client.post(f"/api/admin/stores/{store_id}/activate", headers=headers(a))
    assert r.status_code == 200
    assert r.json()["status"] == "active"

    r = client.post(f"/api/admin/stores/{store_id}/suspend", headers=headers(a))
    assert r.status_code == 200
    assert r.json()["status"] == "suspended"


def test_admin_approve_non_pending_store_rejected(client):
    a = _admin(client)
    store = client.get("/api/admin/stores", headers=headers(a)).json()
    active = next(s for s in store if s["status"] == "active")
    assert client.post(f"/api/admin/stores/{active['id']}/approve", headers=headers(a)).status_code == 400


def test_admin_deactivate_product(client):
    a = _admin(client)
    products = client.get("/api/admin/products", headers=headers(a)).json()
    target = next(p for p in products if p["status"] != "archived")
    r = client.post(f"/api/admin/products/{target['id']}/deactivate", headers=headers(a))
    assert r.status_code == 200
    assert r.json()["status"] == "archived"
    public = client.get("/api/products", params={"size": 100}).json()
    assert all(p["id"] != target["id"] for p in public["items"])


def test_admin_orders_and_reports(client):
    token = login(client, "member_budi")
    register(client, "admin_flow_buyer")
    buyer = login(client, "admin_flow_buyer")
    product = demo_product(client)
    complete_purchase(client, buyer, product["id"])

    a = _admin(client)
    orders = client.get("/api/admin/orders", headers=headers(a)).json()
    assert len(orders) == 1
    assert orders[0]["status"] == "completed"

    r = client.get("/api/admin/reports", params={"days": 30}, headers=headers(a))
    assert r.status_code == 200
    report = r.json()
    assert report["period_days"] == 30
    assert report["users"] >= 3
    assert report["stores"] >= 1
    assert report["orders_by_status"].get("completed") == 1
    assert float(report["transaction_volume"]) > 0


def test_seller_dashboard(client):
    token = login(client, "member_budi")
    register(client, "dash_buyer")
    buyer = login(client, "dash_buyer")
    product = demo_product(client)
    code = complete_purchase(client, buyer, product["id"])
    total = float(client.get(f"/api/orders/{code}", headers=headers(buyer)).json()["total"])

    r = client.get("/api/seller/dashboard", headers=headers(token))
    assert r.status_code == 200
    dash = r.json()
    assert dash["active_products"] == 14
    assert dash["orders_by_status"]["completed"] == 1
    assert float(dash["total_sales"]) == total
    assert float(dash["balance"]) == round(total * 0.95, 2)


def test_member_cannot_access_admin(client):
    register(client, "plain_member")
    token = login(client, "plain_member")
    for path in ("/api/admin/stores", "/api/admin/users", "/api/admin/reports"):
        assert client.get(path, headers=headers(token)).status_code == 403
