## 5. Desain Basis Data

### 5.1 ERD (Relasi Entitas)
```
users (1)──(n) stores (1)──(n) products (1)──(n) product_variants
stores (1)──(n) orders *──────────* products (order_items)
users (1)──(n) orders (buyer)
stores (1)──(n) reviews (rating produk & toko)
users (1)──(1) wallets (1)──(n) wallet_transactions
orders (1)──(1) payments · (1)──(1) shipments
users (1)──(n) addresses · (1)──(n) conversations/messages
categories (1)──(n) products · coupons (n)──(n) orders?
```

### 5.2 Skema Tabel Utama

**users**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| name | varchar | |
| email / phone | varchar unique | login |
| password | varchar (hash) | |
| role | enum | member / seller / admin / superadmin |
| scout_number / kwk_number | varchar nullable | verifikasi anggota |
| kwartir_id | int FK nullable | pangkalan/Kwartir asal |
| is_verified | boolean | verifikasi keanggotaan |
| status | enum | active / suspended |
| created_at / updated_at | datetime | |

**stores**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| owner_id | bigint FK → users | |
| name | varchar | nama toko |
| slug | varchar unique | URL `/store/{slug}` |
| description | text | |
| logo / banner | varchar | |
| category_id | int FK | sektor usaha |
| address / lat / lng | text / decimal | lokasi toko |
| status | enum | pending / active / suspended / rejected |
| commission_rate | decimal | komisi platform |
| created_at / updated_at | datetime | |

**products**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| store_id | bigint FK | |
| category_id | int FK | |
| name | varchar | |
| slug | varchar unique | |
| description | text | |
| price | decimal(14,2) | |
| stock | int | |
| sku | varchar | |
| images | json | daftar URL gambar |
| status | enum | draft / active / archived / rejected |
| views / sold | int | popularitas |
| created_at / updated_at | datetime | |

**product_variants**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| product_id | bigint FK | |
| name / value | varchar | mis. ukuran "L", warna "Merah" |
| price / stock | decimal / int | overrides |

**orders**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_code | varchar unique | tampil ke user |
| buyer_id | bigint FK → users | |
| store_id | bigint FK | satu order per toko (multi-store = multi order) |
| subtotal / shipping_fee / discount / total | decimal | |
| address_id | bigint FK | alamat kirim |
| status | enum | pending_payment / confirmed / processed / shipped / delivered / completed / cancelled / refunded |
| escrow_status | enum | held / released / refunded |
| paid_at / shipped_at / completed_at | datetime | |

**order_items**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | bigint FK | |
| product_id | bigint FK | |
| variant_id | bigint FK null | |
| qty | int | |
| unit_price / total | decimal | snapshot harga |

**payments**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | bigint FK | |
| method | enum | wallet / va / qris / ewallet / cod |
| gateway_ref | varchar | nomor referensi |
| amount | decimal | |
| status | enum | pending / success / failed / refunded |
| paid_at | datetime | |

**wallets**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| user_id | bigint FK unique | |
| balance | decimal(14,2) | saldo aktif |
| escrow_balance | decimal(14,2) | dana ditahan |

**wallet_transactions**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| wallet_id | bigint FK | |
| type | enum | topup / payment / escrow_release / withdraw / refund / commission |
| amount | decimal (±) | |
| ref_id | bigint nullable | pesanan/withdraw terkait |
| balance_after | decimal | snapshot saldo |
| created_at | datetime | |

**withdraws**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| user_id | bigint FK | |
| amount | decimal | |
| bank / account_number / account_name | varchar | |
| status | enum | pending / processed / rejected | |

**shipments**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | bigint FK | |
| courier | varchar | ekspedisi |
| service | varchar | |
| tracking_number | varchar | |
| cost | decimal | |
| status / history | varchar / json | lacak |

**reviews**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_item_id | bigint FK | terikat pesanan selesai |
| user_id / product_id / store_id | FK | |
| rating | tinyint 1–5 | |
| comment | text | |
| status | enum | visible / hidden |

**conversations / messages**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | FK orders (nullable) | terisi bila percakapan dari pesanan |
| product_id | FK products (nullable) | terisi bila percakapan pra-pesanan dari detail produk |
| buyer_id | FK users (nullable) | pembeli pemilik percakapan pra-pesanan |
| message | text | |
| read_at | datetime | |

**categories**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | int PK | |
| name / slug / parent_id | varchar / int | hierarki kategori produk |

**coupons**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| code | varchar unique | |
| type | enum | percent / fixed |
| value | decimal | |
| store_id | FK null | platform atau per toko |
| max_usage / valid_from / valid_until | int / date | |

**settings** — key/value: komisi default, fee withdraw, integrasi gateway, opsi ongkir.

### 5.3 Implementasi Aktual (Iterasi 1)

Tabel yang terimplementasi (SQLAlchemy, PostgreSQL): `users`, `addresses`,
`categories`, `stores`, `products`, `cart_items`, `orders`, `order_items`,
`order_status_history`, `wallets`, `wallet_transactions`, `withdrawals`,
`reviews`, `conversations`, `messages`, `settings`.

Penyesuaian dari desain awal pada iterasi ini:

- **Escrow tanpa tabel `payments`** — status pembayaran diwakili `orders.escrow_status`
  (`held / released / refunded`) dan saldo escrow disimpan di `wallets.escrow_balance`;
  pembayaran hanya via wallet internal (payment gateway eksternal = rencana lanjutan).
- **Ongkir berbasis tier** — `settings.ONGKIR_TIER_A/B/C` (mis. 10.000 / 15.000 / 25.000)
  ditentukan dari provinsi alamat pembeli vs toko; ekspedisi pihak ketiga = rencana lanjutan.
- **Komisi platform** — `settings.COMMISSION_RATE` (default 5%); dipotong saat escrow
  dirilis ke penjual (wallet balance penjual = 95% dari total).
- **Riwayat status** — `order_status_history` mencatat perubahan status order (audit trail).
- **Belum diimplementasikan (rencana lanjutan)**: `product_variants`, `coupons`,
  tabel `payments`/`shipments` terpisah, notifikasi push/email, verifikasi keanggotaan
  Pramuka (nomor KWK), serta ekspor laporan CSV.

---

