from conftest import headers, login, register, seller_token


def test_list_categories(client):
    r = client.get("/api/categories")
    assert r.status_code == 200
    names = [c["slug"] for c in r.json()]
    assert "makanan" in names and "minuman" in names


def test_list_products_seeded(client):
    r = client.get("/api/products", params={"size": 100})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 5
    for item in body["items"]:
        assert item["status"] == "active"
        assert item["store"]["status"] == "active"


def test_product_search_and_filter(client):
    r = client.get("/api/products", params={"q": "kopi"})
    assert r.json()["total"] == 1
    r = client.get("/api/products", params={"category": "makanan", "size": 100})
    assert r.json()["total"] >= 2
    r = client.get("/api/products", params={"sort": "cheapest"})
    prices = [float(i["price"]) for i in r.json()["items"]]
    assert prices == sorted(prices)


def test_product_detail(client):
    products = client.get("/api/products", params={"size": 1}).json()["items"]
    slug = products[0]["slug"]
    r = client.get(f"/api/products/{slug}")
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == slug
    assert "reviews" in body


def test_product_detail_404(client):
    assert client.get("/api/products/tidak-ada").status_code == 404


def test_store_public(client):
    r = client.get("/api/stores/toko-umkm-jaya")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Toko UMKM Jaya"
    assert len(body["products"]) >= 5


def test_seller_get_store(client):
    token = seller_token(client)
    r = client.get("/api/seller/store", headers=headers(token))
    assert r.status_code == 200
    assert r.json()["status"] == "active"


def test_seller_no_store_yet(client):
    register(client, "no_store_user")
    token = login(client, "no_store_user")
    r = client.get("/api/seller/store", headers=headers(token))
    assert r.status_code == 404
    assert client.get("/api/seller/products", headers=headers(token)).status_code == 400


def test_seller_create_store_pending_then_approve(client):
    register(client, "new_seller")
    token = login(client, "new_seller")
    r = client.post(
        "/api/seller/store",
        json={"name": "Toko Test Baru", "city": "Cimahi", "province": "Jawa Barat"},
        headers=headers(token),
    )
    assert r.status_code == 201
    store = r.json()
    assert store["status"] == "pending"

    admin = login(client, "admin", "admin123")
    r = client.post(f"/api/admin/stores/{store['id']}/approve", headers=headers(admin))
    assert r.status_code == 200
    assert r.json()["status"] == "active"


def test_seller_only_one_active_store(client):
    token = seller_token(client)
    r = client.post(
        "/api/seller/store",
        json={"name": "Toko Kedua", "city": "Bandung", "province": "Jawa Barat"},
        headers=headers(token),
    )
    assert r.status_code == 400


def test_seller_update_store(client):
    token = seller_token(client)
    r = client.put(
        "/api/seller/store", json={"description": "Deskripsi baru"}, headers=headers(token)
    )
    assert r.status_code == 200
    assert r.json()["description"] == "Deskripsi baru"


def test_seller_product_crud(client):
    token = seller_token(client)
    r = client.post(
        "/api/seller/products",
        json={
            "name": "Produk Test CRUD",
            "price": 25000,
            "stock": 10,
            "unit": "pcs",
            "status": "active",
        },
        headers=headers(token),
    )
    assert r.status_code == 201
    product = r.json()
    assert product["status"] == "active"

    r = client.put(
        f"/api/seller/products/{product['id']}",
        json={"price": 30000, "stock": 5},
        headers=headers(token),
    )
    assert r.status_code == 200
    assert float(r.json()["price"]) == 30000

    assert client.get(f"/api/seller/products/{product['id']}", headers=headers(token)).status_code == 200
    assert client.delete(f"/api/seller/products/{product['id']}", headers=headers(token)).status_code == 204


def test_seller_product_invalid_status(client):
    token = seller_token(client)
    r = client.post(
        "/api/seller/products",
        json={"name": "Produk Invalid", "price": 1000, "stock": 1, "status": "banned"},
        headers=headers(token),
    )
    assert r.status_code == 400


def test_new_product_hidden_from_public(client):
    token = seller_token(client)
    client.post(
        "/api/seller/products",
        json={"name": "Produk Rahasia", "price": 1000, "stock": 5, "status": "draft"},
        headers=headers(token),
    )
    r = client.get("/api/products", params={"q": "rahasia"})
    assert r.json()["total"] == 0
