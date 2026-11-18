"""Isi data contoh: python seed.py  (dilewati bila data sudah ada)."""
from datetime import date, timedelta

from main import db, init_db, sekarang


def isi():
    init_db()
    with db() as c:
        if c.execute("SELECT COUNT(*) FROM bahan").fetchone()[0] > 0:
            print("Data sudah ada, dilewati.")
            return
        t = sekarang()
        bahan = [
            ("Biji kopi", "kg", 5, 2),
            ("Susu UHT", "liter", 10, 4),
            ("Sirup gula aren", "liter", 3, 1),
            ("Cup 12 oz", "pcs", 200, 50),
            ("Teh celup", "pcs", 60, 20),
            ("Sosis", "pcs", 30, 20),
            ("Roti hot dog", "pcs", 5, 10),
        ]
        ids = {}
        for nama, satuan, jml, batas in bahan:
            cur = c.execute(
                "INSERT INTO bahan (nama, satuan, jumlah, batas_minimum, dibuat_pada) "
                "VALUES (?,?,?,?,?)",
                (nama, satuan, jml, batas, t),
            )
            ids[nama] = cur.lastrowid

        menu = {
            "Es Kopi Susu": (18000, {"Biji kopi": 0.02, "Susu UHT": 0.15,
                                     "Sirup gula aren": 0.02, "Cup 12 oz": 1}),
            "Kopi Hitam": (12000, {"Biji kopi": 0.02, "Cup 12 oz": 1}),
            "Es Teh Manis": (8000, {"Teh celup": 2, "Sirup gula aren": 0.03,
                                    "Cup 12 oz": 1}),
            "Hot Dog": (15000, {"Sosis": 1, "Roti hot dog": 1}),
        }
        mid = {}
        for nama, (harga, resep) in menu.items():
            cur = c.execute(
                "INSERT INTO menu (nama, harga, dibuat_pada) VALUES (?,?,?)",
                (nama, harga, t),
            )
            mid[nama] = cur.lastrowid
            for b, takaran in resep.items():
                c.execute(
                    "INSERT INTO resep (menu_id, bahan_id, takaran) VALUES (?,?,?)",
                    (cur.lastrowid, ids[b], takaran),
                )

        hari = date.today()
        penjualan = [
            ("Es Kopi Susu", 12, 0), ("Es Kopi Susu", 9, 1), ("Kopi Hitam", 6, 1),
            ("Es Teh Manis", 15, 2), ("Hot Dog", 7, 3), ("Es Kopi Susu", 14, 4),
        ]
        for nama, jml, mundur in penjualan:
            c.execute(
                "INSERT INTO penjualan (menu_id, jumlah, tanggal, dibuat_pada) "
                "VALUES (?,?,?,?)",
                (mid[nama], jml, (hari - timedelta(days=mundur)).isoformat(), t),
            )
        print("Data contoh terisi.")


if __name__ == "__main__":
    isi()