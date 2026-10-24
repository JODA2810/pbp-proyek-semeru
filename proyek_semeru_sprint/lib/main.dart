import 'package:flutter/material.dart';

void main() {
  runApp(const DapurCerdasApp());
}

String fmt(double v) => v % 1 == 0 ? v.toInt().toString() : v.toString();

// ---------- Model ----------
class Kategori {
  final int id;
  final String nama;
  final Color warna;
  const Kategori(this.id, this.nama, this.warna);
}

class Bahan {
  int id;
  String nama;
  String satuan;
  double jumlah;
  double batasMinimum;
  DateTime? kedaluwarsa;
  int? kategoriId;

  Bahan({
    required this.id,
    required this.nama,
    required this.satuan,
    this.jumlah = 0,
    this.batasMinimum = 0,
    this.kedaluwarsa,
    this.kategoriId,
  });

  bool get menipis => jumlah <= batasMinimum;
}

class Transaksi {
  final int bahanId;
  final String namaBahan;
  final String jenis;
  final double jumlah;
  final DateTime tanggal;
  Transaksi(
    this.bahanId,
    this.namaBahan,
    this.jenis,
    this.jumlah,
    this.tanggal,
  );
}

// ---------- Aplikasi ----------
class DapurCerdasApp extends StatelessWidget {
  const DapurCerdasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(title: 'DapurCerdas', home: HalamanStok());
  }
}

// ---------- Halaman riwayat ----------
class HalamanRiwayat extends StatelessWidget {
  final List<Transaksi> riwayat;
  const HalamanRiwayat(this.riwayat, {super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Riwayat transaksi')),
      body: riwayat.isEmpty
          ? const Center(child: Text('Belum ada transaksi'))
          : ListView(
              children: [
                for (final t in riwayat)
                  ListTile(
                    leading: Icon(
                      t.jenis == 'masuk'
                          ? Icons.arrow_downward
                          : Icons.arrow_upward,
                      color: t.jenis == 'masuk' ? Colors.green : Colors.red,
                    ),
                    title: Text(t.namaBahan),
                    subtitle: Text(t.tanggal.toString().substring(0, 10)),
                    trailing: Text(
                      '${t.jenis == 'masuk' ? '+' : '-'}${fmt(t.jumlah)}',
                    ),
                  ),
              ],
            ),
    );
  }
}

// ---------- Halaman stok ----------
class HalamanStok extends StatefulWidget {
  const HalamanStok({super.key});

  @override
  State<HalamanStok> createState() => _HalamanStokState();
}

class _HalamanStokState extends State<HalamanStok> {
  final List<Kategori> kategori = const [
    Kategori(1, 'Saus', Color(0xFFE53935)),
    Kategori(2, 'Protein', Color(0xFF8D6E63)),
    Kategori(3, 'Bumbu', Color(0xFFFB8C00)),
    Kategori(4, 'Kemasan', Color(0xFF1E88E5)),
  ];

  final List<Bahan> daftarBahan = [
    Bahan(
      id: 1,
      nama: 'Saus tomat',
      satuan: 'liter',
      jumlah: 12,
      batasMinimum: 5,
      kategoriId: 1,
    ),
    Bahan(
      id: 2,
      nama: 'Sosis',
      satuan: 'pcs',
      jumlah: 8,
      batasMinimum: 20,
      kategoriId: 2,
      kedaluwarsa: DateTime.now().add(const Duration(days: 3)),
    ),
    Bahan(
      id: 3,
      nama: 'Cup 8 oz',
      satuan: 'pcs',
      jumlah: 100,
      batasMinimum: 50,
      kategoriId: 4,
    ),
  ];

  final List<Transaksi> riwayat = [];
  int nextId = 4;
  String filter = 'semua';

  Kategori? cariKategori(int? id) {
    for (final k in kategori) {
      if (k.id == id) return k;
    }
    return null;
  }

  List<Bahan> get tampil {
    final sekarang = DateTime.now();
    switch (filter) {
      case 'menipis':
        return daftarBahan.where((b) => b.menipis).toList();
      case 'kedaluwarsa':
        return daftarBahan
            .where(
              (b) =>
                  b.kedaluwarsa != null &&
                  b.kedaluwarsa!.difference(sekarang).inHours <= 7 * 24,
            )
            .toList();
      default:
        return daftarBahan;
    }
  }

  Future<void> formTambah() async {
    final nama = TextEditingController();
    final satuan = TextEditingController();
    final jumlah = TextEditingController(text: '0');
    final batas = TextEditingController(text: '0');
    int? kat;

    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Tambah bahan'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nama,
                decoration: const InputDecoration(labelText: 'Nama'),
              ),
              TextField(
                controller: satuan,
                decoration: const InputDecoration(
                  labelText: 'Satuan (kg/liter/pcs)',
                ),
              ),
              TextField(
                controller: jumlah,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Jumlah awal'),
              ),
              TextField(
                controller: batas,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Batas minimum'),
              ),
              DropdownButtonFormField<int>(
                hint: const Text('Kategori'),
                items: [
                  for (final k in kategori)
                    DropdownMenuItem(value: k.id, child: Text(k.nama)),
                ],
                onChanged: (v) => kat = v,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () {
              final j = double.tryParse(jumlah.text) ?? -1;
              final m = double.tryParse(batas.text) ?? -1;
              if (nama.text.trim().isEmpty ||
                  satuan.text.trim().isEmpty ||
                  j < 0 ||
                  m < 0) {
                return;
              }
              setState(() {
                daftarBahan.add(
                  Bahan(
                    id: nextId++,
                    nama: nama.text.trim(),
                    satuan: satuan.text.trim(),
                    jumlah: j,
                    batasMinimum: m,
                    kategoriId: kat,
                  ),
                );
              });
              Navigator.pop(ctx);
            },
            child: const Text('Simpan'),
          ),
        ],
      ),
    );
  }

  void catat(Bahan b, String jenis, double jml) {
    if (jml <= 0) return;
    if (jenis == 'keluar' && jml > b.jumlah) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Stok tidak cukup (tersedia ${fmt(b.jumlah)}, diminta ${fmt(jml)})',
          ),
        ),
      );
      return;
    }
    setState(() {
      b.jumlah += jenis == 'masuk' ? jml : -jml;
      riwayat.insert(0, Transaksi(b.id, b.nama, jenis, jml, DateTime.now()));
    });
  }

  void formTransaksi(Bahan b) {
    final jml = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(b.nama),
        content: TextField(
          controller: jml,
          keyboardType: TextInputType.number,
          decoration: InputDecoration(labelText: 'Jumlah (${b.satuan})'),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              catat(b, 'keluar', double.tryParse(jml.text) ?? 0);
            },
            child: const Text('Keluar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              catat(b, 'masuk', double.tryParse(jml.text) ?? 0);
            },
            child: const Text('Masuk'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final data = tampil;
    return Scaffold(
      appBar: AppBar(
        title: const Text('DapurCerdas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => HalamanRiwayat(riwayat)),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: formTambah,
        child: const Icon(Icons.add),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                for (final f in ['semua', 'menipis', 'kedaluwarsa'])
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(f),
                      selected: filter == f,
                      onSelected: (_) => setState(() => filter = f),
                    ),
                  ),
              ],
            ),
          ),
          Expanded(
            child: data.isEmpty
                ? const Center(child: Text('Tidak ada bahan'))
                : ListView.builder(
                    itemCount: data.length,
                    itemBuilder: (context, i) {
                      final b = data[i];
                      final k = cariKategori(b.kategoriId);
                      return Dismissible(
                        key: ValueKey(b.id),
                        background: Container(color: Colors.red),
                        onDismissed: (_) => setState(() {
                          daftarBahan.remove(b);
                          riwayat.removeWhere((t) => t.bahanId == b.id);
                        }),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: k?.warna ?? Colors.grey,
                            child: Text(b.nama[0]),
                          ),
                          title: Text(b.nama),
                          subtitle: Text(k?.nama ?? 'Tanpa kategori'),
                          trailing: Text(
                            '${fmt(b.jumlah)} ${b.satuan}',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: b.menipis ? Colors.red : null,
                            ),
                          ),
                          onTap: () => formTransaksi(b),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
