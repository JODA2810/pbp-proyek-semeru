import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(home: LayarGuyub()));
}

class ItemBacklog {
  final String kunci;
  final String judul;
  final String jenis;
  final int poin;
  final String status;
  final String? penanggungJawab;

  const ItemBacklog({
    required this.kunci,
    required this.judul,
    required this.jenis,
    required this.poin,
    required this.status,
    this.penanggungJawab,
  });
}

class LayarGuyub extends StatelessWidget {
  const LayarGuyub({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Layar Guyub')),
      body: const Center(child: Text('Selamat datang di Layar Guyub!')),
    );
  }
}

const daftarItem = [
  ItemBacklog('GYB-001', 'Halaman menu roti', 'story', 5, 'Done', 'Sekar'),
  ItemBacklog('GYB-002', 'Form pesanan', 'story', 5, 'Review', 'Bayu'),
  ItemBacklog(
    'GYB-003',
    'Tombol pesan tidak aktif di Safari',
    'bug',
    2,
    'In Progress',
    'Dimas',
  ),
  ItemBacklog(
    'GYB-004',
    'Ongkir dihitung per kecamatan',
    'story',
    3,
    'To Do',
    'Bayu',
  ),
  ItemBacklog('GYB-005', 'Foto produk lambat dimuat', 'bug', 2, 'To Do', null),
];

class DaftarKartu extends StatelessWidget {
  const DaftarKartu({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Daftar Kartu')),
      body: const Center(child: Text('Ini adalah halaman Daftar Kartu.')),
    );
  }
}
