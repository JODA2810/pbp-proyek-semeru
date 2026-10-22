import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(
    home: LayarGuyub(),
  ));
}

class LayarGuyub extends StatelessWidget {
  const LayarGuyub({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Layar Guyub'),
      ),
      body: const Center(
        child: Text('Selamat datang di Layar Guyub!'),
      ),
    );
  }

}