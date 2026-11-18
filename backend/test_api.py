import os

os.environ["DB_PATH"] = "test_dapurcerdas.db"

import pytest
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def bersih():
    with main.db() as c:
        c.executescript(
            "DELETE FROM penjualan; DELETE FROM resep; DELETE FROM menu; DELETE FROM bahan;"
        )


def buat_bahan(nama="Susu", jumlah=10, batas=2):
    return client.post(
        "/bahan",
        json={"nama": nama, "satuan": "liter", "jumlah": jumlah, "batas_minimum": batas},
    ).json()


def buat_menu(nama="Es Kopi Susu", harga=18000):
    return client.post("/menu", json={"nama": nama, "harga": harga}).json()


def test_tambah_bahan_201():
    r = client.post("/bahan", json={"nama": "Susu", "satuan": "liter", "jumlah": 5})
    assert r.status_code == 201
    assert r.json()["id"] > 0
    assert r.json()["dibuat_pada"]


def test_bahan_nama_kosong_422():
    r = client.post("/bahan", json={"nama": "", "satuan": "liter"})
    assert r.status_code == 422


def test_bahan_tidak_ada_404():
    assert client.get("/bahan/9999").status_code == 404
    assert client.delete("/bahan/9999").status_code == 404


def test_ubah_bahan_mengisi_diubah_pada():
    b = buat_bahan()
    r = client.put(
        f"/bahan/{b['id']}",
        json={"nama": "Susu Full", "satuan": "liter", "jumlah": 8, "batas_minimum": 2},
    )
    assert r.status_code == 200
    assert r.json()["diubah_pada"] is not None


def test_pencarian_dan_filter_menipis():
    buat_bahan("Susu", 10, 2)
    buat_bahan("Roti", 1, 5)
    assert len(client.get("/bahan?q=sus").json()) == 1
    menipis = client.get("/bahan?status=menipis").json()
    assert [b["nama"] for b in menipis] == ["Roti"]


def test_nilai_tidak_dikenal_422():
    assert client.get("/bahan?status=ngawur").status_code == 422
    assert client.get("/bahan?urut=ngawur").status_code == 422


def test_detail_menu_memuat_resep():
    b = buat_bahan()
    m = buat_menu()
    r = client.post(f"/menu/{m['id']}/resep", json={"bahan_id": b["id"], "takaran": 0.15})
    assert r.status_code == 201
    detail = client.get(f"/menu/{m['id']}").json()
    assert len(detail["resep"]) == 1
    assert detail["resep"][0]["nama_bahan"] == "Susu"


def test_resep_menu_tidak_ada_404():
    b = buat_bahan()
    r = client.post("/menu/9999/resep", json={"bahan_id": b["id"], "takaran": 1})
    assert r.status_code == 404
    assert client.get("/menu/9999/resep").status_code == 404


def test_resep_isian_salah_422():
    m = buat_menu()
    assert client.post(f"/menu/{m['id']}/resep", json={"bahan_id": 1, "takaran": 0}).status_code == 422
    assert client.post(f"/menu/{m['id']}/resep", json={"bahan_id": 9999, "takaran": 1}).status_code == 422


def test_hapus_menu_ikut_hapus_resep():
    b = buat_bahan()
    m = buat_menu()
    client.post(f"/menu/{m['id']}/resep", json={"bahan_id": b["id"], "takaran": 1})
    assert client.delete(f"/menu/{m['id']}").status_code == 200
    with main.db() as c:
        assert c.execute("SELECT COUNT(*) FROM resep").fetchone()[0] == 0
    assert client.get(f"/menu/{m['id']}/resep").status_code == 404


def test_penjualan_memotong_stok():
    b = buat_bahan(jumlah=10)
    m = buat_menu()
    client.post(f"/menu/{m['id']}/resep", json={"bahan_id": b["id"], "takaran": 0.5})
    r = client.post(f"/menu/{m['id']}/penjualan", json={"jumlah": 4})
    assert r.status_code == 201
    assert client.get(f"/bahan/{b['id']}").json()["jumlah"] == 8


def test_penjualan_stok_kurang_400_dan_stok_utuh():
    b = buat_bahan(jumlah=1)
    m = buat_menu()
    client.post(f"/menu/{m['id']}/resep", json={"bahan_id": b["id"], "takaran": 0.5})
    r = client.post(f"/menu/{m['id']}/penjualan", json={"jumlah": 5})
    assert r.status_code == 400
    assert client.get(f"/bahan/{b['id']}").json()["jumlah"] == 1


def test_penjualan_menu_tidak_ada_404_dan_jumlah_0_422():
    assert client.post("/menu/9999/penjualan", json={"jumlah": 1}).status_code == 404
    m = buat_menu()
    assert client.post(f"/menu/{m['id']}/penjualan", json={"jumlah": 0}).status_code == 422


def test_ringkasan_cocok_dengan_data():
    b = buat_bahan("Susu", 10, 2)
    buat_bahan("Roti", 1, 5)
    m = buat_menu(harga=10000)
    client.post(f"/menu/{m['id']}/resep", json={"bahan_id": b["id"], "takaran": 1})
    client.post(f"/menu/{m['id']}/penjualan", json={"jumlah": 3})
    r = client.get("/ringkasan").json()
    assert r["total_bahan"] == 2
    assert r["bahan_menipis"] == 1
    assert r["porsi_terjual_pekan_ini"] == 3
    assert r["omzet_pekan_ini"] == 30000