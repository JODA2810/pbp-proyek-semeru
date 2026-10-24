# DapurCerdas

Aplikasi manajemen usaha kuliner yang menyatukan kasir digital, stok bahan baku, pencatatan bahan terbuang, dan laporan usaha dalam satu platform.

## Kelompok
Nama kelompok: Semeru

| No | Nama | NIM |
|----|------|-----|
| 1 | Ivan Sanjaya Tjoe | 223400007 |
| 2 | Jonathan Surjadjaja | 243401003 |

## Ringkasan Usulan Proyek v2

### Latar belakang (hasil wawancara)
Kami mewawancarai Yano dan rekan kerjanya, Valentino, pelaku usaha kuliner, dengan 10 pertanyaan. Temuan utamanya:

- Stok masih dicatat di buku atau spreadsheet sederhana, dan dicek fisik saat closing.
- Pencatatan sering terlewat saat ramai, rekap manual malam hari melelahkan dan rawan salah hitung, dan catatan sering tidak cocok dengan stok fisik.
- Pemakaian bahan per menu hanya diperkirakan dari ingatan. Kasir mencatat menu terjual, tetapi stok bahan tidak berkurang otomatis.
- Stok habis mendadak saat akhir pekan atau jam sibuk karena tidak ada peringatan dini. Bahan segar terbuang karena salah prediksi atau FIFO tidak dijalankan.
- Waktu restock ditentukan dari melihat sisa barang. Belum ada batas minimum stok (safety stock).
- Google Sheets sulit diisi lewat HP saat ramai dan rawan rumus rusak. Aplikasi kasir seperti Moka dan Majoo punya pengaturan stok bahan yang rumit, kurang fleksibel untuk resep, dan cukup mahal untuk usaha kecil.
- Pengguna: pemilik (dashboard dan laporan), kasir (input penjualan cepat), dan dapur/gudang (resep, barang masuk, update sisa bahan). Perangkat utamanya HP, sedangkan web/komputer dipakai sesekali untuk rekap dan laporan.

### Solusi
DapurCerdas adalah aplikasi dengan pendekatan mobile-first dan tampilan sederhana. Fitur utamanya:

- Stok bahan baku berkurang otomatis berdasarkan resep setiap kali menu terjual.
- Notifikasi saat stok mencapai batas minimum.
- Pencatatan bahan rusak atau terbuang (waste).
- Dashboard penjualan, pengeluaran, dan persediaan.
- Tampilan web/desktop untuk pengelolaan dan analisis laporan.

Dengan aplikasi ini, operasional diharapkan lebih efisien, kesalahan pencatatan berkurang, persediaan lebih akurat, dan pemilik bisa memantau usaha tanpa selalu berada di tempat.

## Kontrak Lima Unsur
1. **[Unsur 1]**: isi singkat
2. **[Unsur 2]**: isi singkat
3. **[Unsur 3]**: isi singkat
4. **[Unsur 4]**: isi singkat
5. **[Unsur 5]**: isi singkat

## Batasan
- Versi awal fokus pada aplikasi mobile. Tampilan web hanya untuk melihat laporan dan dashboard.
- Tidak ada integrasi pembayaran digital (QRIS, e-wallet). Kasir hanya mencatat penjualan.
- Tidak ada integrasi dengan aplikasi kasir lain (Moka, Majoo).
- Peringatan stok menipis tampil di dalam aplikasi lebih dulu, notifikasi push menyusul bila waktu cukup.
- Satu outlet per akun, belum mendukung multi-cabang.
- Data bahan awal diinput manual oleh pengguna.

## Backlog Awal

| No | Butir | Unsur kontrak yang dilayani |
|----|-------|-----------------------------|
| 1 | Kelola data bahan baku dan stok masuk (tambah, ubah, hapus, satuan, batas minimum) | [Unsur 1] |
| 2 | Kelola menu dan resep (takaran bahan per menu) | [Unsur 2] |
| 3 | Input penjualan cepat untuk kasir, stok bahan terpotong otomatis sesuai resep | [Unsur 2] |
| 4 | Peringatan stok menipis saat jumlah mencapai batas minimum | [Unsur 3] |
| 5 | Pencatatan bahan rusak atau terbuang (waste) | [Unsur 3] |
| 6 | Dashboard pemilik: penjualan, pengeluaran, dan persediaan | [Unsur 4] |
| 7 | Laporan stok dan penggunaan bahan per menu (dasar HPP) | [Unsur 4] |
| 8 | Peran pengguna: pemilik, kasir, dapur/gudang | [Unsur 5] |