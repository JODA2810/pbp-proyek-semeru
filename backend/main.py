"""Backend DapurCerdas - Kelompok Semeru.

Jalankan : uvicorn main:app --reload
Dokumentasi: http://127.0.0.1:8000/docs
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="DapurCerdas API", version="1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


# ---------- Database ----------
def db_path():
    return os.environ.get("DB_PATH", "dapurcerdas.db")


def sekarang():
    return datetime.now().isoformat(timespec="seconds")


@contextmanager
def db():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS bahan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                satuan TEXT NOT NULL,
                jumlah REAL NOT NULL DEFAULT 0,
                batas_minimum REAL NOT NULL DEFAULT 0,
                dibuat_pada TEXT NOT NULL,
                diubah_pada TEXT
            );
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                harga INTEGER NOT NULL DEFAULT 0,
                dibuat_pada TEXT NOT NULL,
                diubah_pada TEXT
            );
            CREATE TABLE IF NOT EXISTS resep (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_id INTEGER NOT NULL REFERENCES menu(id) ON DELETE CASCADE,
                bahan_id INTEGER NOT NULL REFERENCES bahan(id) ON DELETE CASCADE,
                takaran REAL NOT NULL CHECK (takaran > 0),
                UNIQUE (menu_id, bahan_id)
            );
            CREATE TABLE IF NOT EXISTS penjualan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                menu_id INTEGER NOT NULL REFERENCES menu(id) ON DELETE CASCADE,
                jumlah INTEGER NOT NULL CHECK (jumlah > 0),
                tanggal TEXT NOT NULL,
                dibuat_pada TEXT NOT NULL
            );
            """
        )


init_db()


# ---------- Skema ----------
class StatusStok(str, Enum):
    semua = "semua"
    menipis = "menipis"
    aman = "aman"


class UrutBahan(str, Enum):
    nama = "nama"
    stok = "stok"
    terbaru = "terbaru"


class BahanIn(BaseModel):
    nama: str = Field(min_length=1, max_length=100)
    satuan: str = Field(min_length=1, max_length=20)
    jumlah: float = Field(default=0, ge=0)
    batas_minimum: float = Field(default=0, ge=0)


class MenuIn(BaseModel):
    nama: str = Field(min_length=1, max_length=100)
    harga: int = Field(ge=0)


class ResepIn(BaseModel):
    bahan_id: int
    takaran: float = Field(gt=0)


class PenjualanIn(BaseModel):
    jumlah: int = Field(ge=1)
    tanggal: date = Field(default_factory=date.today)


# ---------- Pembantu ----------
def ambil_bahan(c, bahan_id):
    r = c.execute("SELECT * FROM bahan WHERE id=?", (bahan_id,)).fetchone()
    if not r:
        raise HTTPException(404, "Bahan tidak ditemukan")
    d = dict(r)
    d["menipis"] = d["jumlah"] <= d["batas_minimum"]
    return d


def ambil_menu(c, menu_id):
    r = c.execute("SELECT * FROM menu WHERE id=?", (menu_id,)).fetchone()
    if not r:
        raise HTTPException(404, "Menu tidak ditemukan")
    return dict(r)


def daftar_resep(c, menu_id):
    rows = c.execute(
        """SELECT r.id, r.bahan_id, b.nama AS nama_bahan, b.satuan, r.takaran
           FROM resep r JOIN bahan b ON b.id = r.bahan_id
           WHERE r.menu_id=? ORDER BY r.id""",
        (menu_id,),
    )
    return [dict(r) for r in rows]


# ---------- Bahan ----------
@app.get("/bahan")
def daftar_bahan(
    q: Optional[str] = None,
    status: StatusStok = StatusStok.semua,
    urut: UrutBahan = UrutBahan.nama,
):
    sql = "SELECT * FROM bahan WHERE 1=1"
    args = []
    if q:
        sql += " AND nama LIKE ?"
        args.append(f"%{q}%")
    if status == StatusStok.menipis:
        sql += " AND jumlah <= batas_minimum"
    elif status == StatusStok.aman:
        sql += " AND jumlah > batas_minimum"
    sql += " ORDER BY " + {
        "nama": "nama",
        "stok": "jumlah ASC",
        "terbaru": "dibuat_pada DESC, id DESC",
    }[urut.value]
    with db() as c:
        hasil = []
        for r in c.execute(sql, args):
            d = dict(r)
            d["menipis"] = d["jumlah"] <= d["batas_minimum"]
            hasil.append(d)
        return hasil


@app.get("/bahan/{bahan_id}")
def detail_bahan(bahan_id: int):
    with db() as c:
        return ambil_bahan(c, bahan_id)


@app.post("/bahan", status_code=201)
def tambah_bahan(data: BahanIn):
    with db() as c:
        cur = c.execute(
            """INSERT INTO bahan (nama, satuan, jumlah, batas_minimum, dibuat_pada)
               VALUES (?,?,?,?,?)""",
            (data.nama, data.satuan, data.jumlah, data.batas_minimum, sekarang()),
        )
        return ambil_bahan(c, cur.lastrowid)


@app.put("/bahan/{bahan_id}")
def ubah_bahan(bahan_id: int, data: BahanIn):
    with db() as c:
        ambil_bahan(c, bahan_id)
        c.execute(
            """UPDATE bahan SET nama=?, satuan=?, jumlah=?, batas_minimum=?,
               diubah_pada=? WHERE id=?""",
            (data.nama, data.satuan, data.jumlah, data.batas_minimum, sekarang(), bahan_id),
        )
        return ambil_bahan(c, bahan_id)


@app.delete("/bahan/{bahan_id}")
def hapus_bahan(bahan_id: int):
    with db() as c:
        ambil_bahan(c, bahan_id)
        c.execute("DELETE FROM bahan WHERE id=?", (bahan_id,))
        return {"pesan": "Bahan dihapus", "id": bahan_id}


# ---------- Menu ----------
@app.get("/menu")
def daftar_menu(q: Optional[str] = None):
    sql = "SELECT * FROM menu"
    args = []
    if q:
        sql += " WHERE nama LIKE ?"
        args.append(f"%{q}%")
    sql += " ORDER BY nama"
    with db() as c:
        return [dict(r) for r in c.execute(sql, args)]


@app.get("/menu/{menu_id}")
def detail_menu(menu_id: int):
    with db() as c:
        m = ambil_menu(c, menu_id)
        m["resep"] = daftar_resep(c, menu_id)
        return m


@app.post("/menu", status_code=201)
def tambah_menu(data: MenuIn):
    with db() as c:
        cur = c.execute(
            "INSERT INTO menu (nama, harga, dibuat_pada) VALUES (?,?,?)",
            (data.nama, data.harga, sekarang()),
        )
        return ambil_menu(c, cur.lastrowid)


@app.put("/menu/{menu_id}")
def ubah_menu(menu_id: int, data: MenuIn):
    with db() as c:
        ambil_menu(c, menu_id)
        c.execute(
            "UPDATE menu SET nama=?, harga=?, diubah_pada=? WHERE id=?",
            (data.nama, data.harga, sekarang(), menu_id),
        )
        return ambil_menu(c, menu_id)


@app.delete("/menu/{menu_id}")
def hapus_menu(menu_id: int):
    """Menu terhapus, resep dan penjualannya ikut terhapus."""
    with db() as c:
        ambil_menu(c, menu_id)
        c.execute("DELETE FROM menu WHERE id=?", (menu_id,))
        return {"pesan": "Menu dihapus", "id": menu_id}


# ---------- Resep (anak dari menu) ----------
@app.get("/menu/{menu_id}/resep")
def lihat_resep(menu_id: int):
    with db() as c:
        ambil_menu(c, menu_id)
        return daftar_resep(c, menu_id)


@app.post("/menu/{menu_id}/resep", status_code=201)
def tambah_resep(menu_id: int, data: ResepIn):
    with db() as c:
        ambil_menu(c, menu_id)
        ada = c.execute("SELECT 1 FROM bahan WHERE id=?", (data.bahan_id,)).fetchone()
        if not ada:
            raise HTTPException(422, "bahan_id tidak ditemukan")
        try:
            cur = c.execute(
                "INSERT INTO resep (menu_id, bahan_id, takaran) VALUES (?,?,?)",
                (menu_id, data.bahan_id, data.takaran),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Bahan itu sudah ada di resep menu ini")
        return next(r for r in daftar_resep(c, menu_id) if r["id"] == cur.lastrowid)


@app.delete("/menu/{menu_id}/resep/{resep_id}")
def hapus_resep(menu_id: int, resep_id: int):
    with db() as c:
        ambil_menu(c, menu_id)
        cur = c.execute(
            "DELETE FROM resep WHERE id=? AND menu_id=?", (resep_id, menu_id)
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Resep tidak ditemukan")
        return {"pesan": "Resep dihapus", "id": resep_id}


# ---------- Penjualan (anak dari menu) ----------
@app.get("/menu/{menu_id}/penjualan")
def lihat_penjualan(menu_id: int):
    with db() as c:
        ambil_menu(c, menu_id)
        rows = c.execute(
            "SELECT * FROM penjualan WHERE menu_id=? ORDER BY tanggal DESC, id DESC",
            (menu_id,),
        )
        return [dict(r) for r in rows]


@app.post("/menu/{menu_id}/penjualan", status_code=201)
def catat_penjualan(menu_id: int, data: PenjualanIn):
    """Catat penjualan; stok bahan terpotong otomatis sesuai resep."""
    with db() as c:
        ambil_menu(c, menu_id)
        resep = c.execute(
            "SELECT bahan_id, takaran FROM resep WHERE menu_id=?", (menu_id,)
        ).fetchall()
        if not resep:
            raise HTTPException(422, "Menu belum punya resep")
        # periksa dulu semua bahan sebelum ada yang dipotong
        for r in resep:
            b = ambil_bahan(c, r["bahan_id"])
            butuh = r["takaran"] * data.jumlah
            if b["jumlah"] < butuh:
                raise HTTPException(
                    400,
                    f"Stok {b['nama']} tidak cukup "
                    f"(tersedia {b['jumlah']}, butuh {butuh})",
                )
        for r in resep:
            c.execute(
                "UPDATE bahan SET jumlah = jumlah - ?, diubah_pada=? WHERE id=?",
                (r["takaran"] * data.jumlah, sekarang(), r["bahan_id"]),
            )
        cur = c.execute(
            """INSERT INTO penjualan (menu_id, jumlah, tanggal, dibuat_pada)
               VALUES (?,?,?,?)""",
            (menu_id, data.jumlah, data.tanggal.isoformat(), sekarang()),
        )
        return dict(
            c.execute("SELECT * FROM penjualan WHERE id=?", (cur.lastrowid,)).fetchone()
        )


# ---------- Ringkasan (layar desktop) ----------
@app.get("/ringkasan")
def ringkasan():
    batas = (date.today() - timedelta(days=6)).isoformat()
    with db() as c:
        total_bahan = c.execute("SELECT COUNT(*) FROM bahan").fetchone()[0]
        menipis = c.execute(
            "SELECT COUNT(*) FROM bahan WHERE jumlah <= batas_minimum"
        ).fetchone()[0]
        total_menu = c.execute("SELECT COUNT(*) FROM menu").fetchone()[0]
        trx, porsi = c.execute(
            """SELECT COUNT(*), COALESCE(SUM(jumlah), 0)
               FROM penjualan WHERE tanggal >= ?""",
            (batas,),
        ).fetchone()
        omzet = c.execute(
            """SELECT COALESCE(SUM(p.jumlah * m.harga), 0)
               FROM penjualan p JOIN menu m ON m.id = p.menu_id
               WHERE p.tanggal >= ?""",
            (batas,),
        ).fetchone()[0]
        return {
            "total_bahan": total_bahan,
            "bahan_menipis": menipis,
            "bahan_aman": total_bahan - menipis,
            "total_menu": total_menu,
            "penjualan_pekan_ini": trx,
            "porsi_terjual_pekan_ini": porsi,
            "omzet_pekan_ini": omzet,
        }