//NOT CODED YET
//This is a template code we need to refine this page
//SM 28-7-26

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'config.dart';

class SearchOrderLibraryPage extends StatefulWidget {
  const SearchOrderLibraryPage({super.key});

  @override
  State<SearchOrderLibraryPage> createState() => _SearchOrderLibraryPageState();
}

class _SearchOrderLibraryPageState extends State<SearchOrderLibraryPage> {
  String _selectedType = "Book";
  final _barcodeController = TextEditingController();
  Map<String, dynamic>? _item;

  Future<void> _logout(BuildContext context) async {
    // Clear any stored session/token here
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    // Navigate back to login page (ensure context still valid)
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
  }

  Future<void> _scanAndSearch() async {
    final barcode = _barcodeController.text;
    final response = await http.get(
      Uri.parse('${Config.apiUrl}/api/inventoryhome/$barcode'),
    );
    if (response.statusCode == 200) {
      setState(() {
        _item = jsonDecode(response.body);
      });
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Inventory not found")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Search Inventory"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.red),
            tooltip: 'Logout',
            onPressed: () async => await _logout(context),
          ),
        ],
      ),
      body: Column(
        children: [
          DropdownButton<String>(
            value: _selectedType,
            items: [
              'Book',
              'Toy',
              'Other',
            ].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
            onChanged: (val) => setState(() => _selectedType = val!),
          ),
          TextField(
            controller: _barcodeController,
            decoration: const InputDecoration(labelText: "Scan Barcode/QR"),
          ),
          ElevatedButton(onPressed: _scanAndSearch, child: const Text("Scan")),
          if (_item != null) ...[
            Text("Name: ${_item!['title'] ?? ''}"),
            Text("State: ${_item!['state'] ?? ''}"),
            Text("Category: ${_item!['category'] ?? ''}"),
          ],
        ],
      ),
    );
  }
}
