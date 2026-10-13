//NOT CODED YET
//This is a template code we need to refine this page
//SM 28-7-26

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'config.dart';

class UpdateOrderLibraryPage extends StatefulWidget {
  const UpdateOrderLibraryPage({super.key});

  @override
  State<UpdateOrderLibraryPage> createState() => _UpdateOrderLibraryPageState();
}

class _UpdateOrderLibraryPageState extends State<UpdateOrderLibraryPage> {
  String _selectedType = "Book";
  final _barcodeController = TextEditingController();
  String? _currentState;
  String? _nextState;

  Future<void> _logout(BuildContext context) async {
    // Clear any stored session/token here
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    // Navigate back to login page (ensure context still valid)
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
  }

  Future<void> _scanAndFetch() async {
    final barcode = _barcodeController.text;
    final response = await http.get(
      Uri.parse('${Config.apiUrl}/api/inventoryhome/$barcode'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        _currentState = data['state'];
        _nextState = "Ordered";
      });
    } else {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text("Inventory not found")));
    }
  }

  Future<void> _updateState() async {
    final response = await http.patch(
      Uri.parse('${Config.apiUrl}/api/inventoryhome/state'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'barcode': _barcodeController.text,
        'new_state': _nextState,
        'agent_id': 1,
      }),
    );
    if (response.statusCode == 200) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("State updated successfully")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Update Inventory"),
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
          ElevatedButton(onPressed: _scanAndFetch, child: const Text("Scan")),
          if (_currentState != null) ...[
            DropdownButton<String>(
              value: _nextState,
              items: [
                "Ordered",
                "Delivered",
                "Returned",
              ].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
              onChanged: (val) => setState(() => _nextState = val),
            ),
            ElevatedButton(
              onPressed: _updateState,
              child: const Text("Save State"),
            ),
          ],
        ],
      ),
    );
  }
}
