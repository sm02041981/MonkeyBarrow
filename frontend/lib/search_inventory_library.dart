//NOT CODED YET
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'config.dart';

class SearchInventoryLibraryPage extends StatefulWidget {
  const SearchInventoryLibraryPage({super.key});

  @override
  State<SearchInventoryLibraryPage> createState() =>
      _SearchInventoryLibraryPageState();
}

class _SearchInventoryLibraryPageState
    extends State<SearchInventoryLibraryPage> {
  String _selectedType = "Book";
  final _mbisbnController = TextEditingController();
  Map<String, dynamic>? _item;

  Future<void> _logout(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
  }

  Future<void> _scanAndSearch() async {
    final mbIsbn13 = _mbisbnController.text.trim();
    if (mbIsbn13.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Please enter ISBN")));
      return;
    }

    final response = await http.get(
      Uri.parse('${Config.apiUrl}/api/inventory/$mbIsbn13'),
    );

    if (!mounted) return;

    if (response.statusCode == 200) {
      setState(() {
        _item = jsonDecode(response.body);
      });
    } else {
      // ✅ Show popup dialog instead of snackbar
      showDialog(
        context: context,
        builder: (BuildContext dialogContext) {
          return AlertDialog(
            title: const Text(
              "Book Not Found",
              style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
            ),
            content: const Text(
              "Book not found in MonkeyBarrow Database.\n"
              "Please check the ISBN or add the book manually.",
            ),
            actions: [
              TextButton(
                child: const Text("OK"),
                onPressed: () {
                  Navigator.of(dialogContext).pop();
                },
              ),
            ],
          );
        },
      );
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
          // Row for Inventory Type
          Row(
            children: [
              const Expanded(
                flex: 1,
                child: Text(
                  "Inventory Type - (Book / Toy / Premium-Toy / Stationery / Gift / Other)",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Color.fromARGB(255, 2, 27, 3),
                  ),
                ),
              ),
              Expanded(
                flex: 1,
                child: DropdownButton<String>(
                  value: _selectedType,
                  isExpanded: true,
                  items:
                      [
                            'Book',
                            'Toy',
                            'Premium-Toy',
                            'Stationery',
                            'Gift',
                            'Other',
                          ]
                          .map(
                            (s) => DropdownMenuItem(value: s, child: Text(s)),
                          )
                          .toList(),
                  onChanged: (val) => setState(() => _selectedType = val!),
                ),
              ),
            ],
          ),
          TextField(
            controller: _mbisbnController,
            decoration: const InputDecoration(labelText: "Enter 13-digit ISBN"),
          ),
          ElevatedButton(
            onPressed: _scanAndSearch,
            child: const Text("Search"),
          ),
          const SizedBox(height: 20),

          // ✅ Show full BookResponse schema if found
          if (_item != null) ...[
            Text("ISBN: ${_item!['mb_isbn13'] ?? ''}"),
            Text("Title: ${_item!['title'] ?? ''}"),
            Text("Author: ${_item!['author'] ?? ''}"),
            Text("Age Group: ${_item!['age_group'] ?? ''}"),
            Text("Category: ${_item!['category'] ?? ''}"),
            Text("Weight: ${_item!['weight'] ?? ''}"),
            Text("Description: ${_item!['description'] ?? ''}"),
            Text("Quantity: ${_item!['quantity'] ?? ''}"),
            Text("MRP: ${_item!['mrp'] ?? ''}"),
            Text("Image Front: ${_item!['image_fp_url'] ?? ''}"),
            Text("Image Back: ${_item!['image_bp_url'] ?? ''}"),
          ],
        ],
      ),
    );
  }
}
