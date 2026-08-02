from conftest import (
    add_address,
    add_cart,
    checkout,
    demo_product,
    headers,
    login,
    pay_order,
    register,
    topup,
)


def _buyer(client, name="ticket_buyer"):
    register(client, name)
    return login(client, name)


def _make_paid_order(client, token):
    product = demo_product(client)
    topup(client, token)
    add_address(client, token)
    add_cart(client, token, product["id"], 1)
    code = checkout(client, token, 1)[0]
    pay_order(client, token, code)
    return code


def _open_ticket(client, token, code, issue="barang_rusak", desc="Produk yang dikirim tidak sesuai deskripsi."):
    return client.post(
        "/api/tickets",
        json={"order_code": code, "issue_type": issue, "description": desc},
        headers=headers(token),
    )


def test_buyer_open_ticket_and_list(client):
    buyer = _buyer(client)
    code = _make_paid_order(client, buyer)
    r = _open_ticket(client, buyer, code)
    assert r.status_code == 201
    t = r.json()
    assert t["ticket_code"].startswith("TKT-")
    assert t["order_code"] == code
    assert t["status"] == "open"
    assert t["opened_by"] == "ticket_buyer"
    assert t["store_name"]

    lst = client.get("/api/tickets", headers=headers(buyer)).json()
    assert len(lst) == 1
    assert lst[0]["ticket_code"] == t["ticket_code"]

    st = login(client, "member_budi")
    seller_list = client.get("/api/tickets", headers=headers(st)).json()
    assert len(seller_list) == 1
    assert seller_list[0]["ticket_code"] == t["ticket_code"]


def test_ticket_requires_paid_order(client):
    buyer = _buyer(client)
    product = demo_product(client)
    topup(client, buyer)
    add_address(client, buyer)
    add_cart(client, buyer, product["id"], 1)
    code = checkout(client, buyer, 1)[0]
    r = _open_ticket(client, buyer, code)
    assert r.status_code == 400


def test_one_active_ticket_per_order(client):
    buyer = _buyer(client)
    code = _make_paid_order(client, buyer)
    assert _open_ticket(client, buyer, code).status_code == 201
    r = _open_ticket(client, buyer, code, issue="barang_tidak_datang", desc="Barang kedua tidak kunjung datang.")
    assert r.status_code == 400
    assert "sudah ada tiket aktif" in r.json()["detail"].lower()


def test_outsider_cannot_access(client):
    buyer = _buyer(client)
    outsider = _buyer(client, "ticket_outsider")
    code = _make_paid_order(client, buyer)
    ticket_id = _open_ticket(client, buyer, code).json()["id"]

    assert client.get(f"/api/tickets/{ticket_id}", headers=headers(outsider)).status_code == 403
    assert client.get("/api/tickets", headers=headers(outsider)).json() == []


def test_messages_and_history_tracking(client):
    buyer = _buyer(client)
    code = _make_paid_order(client, buyer)
    ticket_id = _open_ticket(client, buyer, code).json()["id"]

    st = login(client, "member_budi")
    r = client.post(
        f"/api/tickets/{ticket_id}/messages",
        json={"body": "Kami cek dulu, mohon tunggu."},
        headers=headers(st),
    )
    assert r.status_code == 201
    assert r.json()["sender_name"] == "member_budi"

    detail = client.get(f"/api/tickets/{ticket_id}", headers=headers(buyer)).json()
    assert len(detail["messages"]) == 1
    assert detail["messages"][0]["body"] == "Kami cek dulu, mohon tunggu."
    assert len(detail["history"]) == 1
    assert detail["history"][0]["status"] == "open"
    assert detail["history"][0]["actor"] == "ticket_buyer"


def test_status_flow_and_rbac(client):
    buyer = _buyer(client)
    code = _make_paid_order(client, buyer)
    ticket_id = _open_ticket(client, buyer, code).json()["id"]

    st = login(client, "member_budi")
    r = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "resolved"},
        headers=headers(st),
    )
    assert r.status_code == 403

    admin = login(client, "admin", "admin123")
    r = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "in_review", "note": "Sedang ditinjau admin"},
        headers=headers(admin),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "in_review"
    assert len(r.json()["history"]) == 2
    assert r.json()["history"][1]["actor"] == "admin"

    r = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "resolved", "note": "Pengembalian dana disetujui"},
        headers=headers(admin),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"

    r = client.post(f"/api/tickets/{ticket_id}/messages", json={"body": "Terima kasih"}, headers=headers(buyer))
    assert r.status_code == 201


def test_admin_list_and_close(client):
    buyer = _buyer(client)
    code = _make_paid_order(client, buyer)
    ticket_id = _open_ticket(client, buyer, code).json()["id"]
    admin = login(client, "admin", "admin123")

    lst = client.get("/api/admin/tickets", headers=headers(admin)).json()
    assert len(lst) == 1
    assert lst[0]["id"] == ticket_id

    r = client.post(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "closed", "note": "Tiket ditutup admin"},
        headers=headers(admin),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "closed"

    r = client.post(f"/api/tickets/{ticket_id}/status", json={"status": "open"}, headers=headers(admin))
    assert r.status_code == 400
