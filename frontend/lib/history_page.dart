import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'config.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  final _barcodeController = TextEditingController();
  List<dynamic> _history = [];

  Future<void> _fetchHistory() async {
    if (_barcodeController.text.isNotEmpty) {
      try {
        final response = await http.get(Uri.parse('${Config.apiUrl}/api/inventory/${_barcodeController.text}/history'));
        if (response.statusCode == 200) {
          setState(() {
            _history = jsonDecode(response.body);
          });
        } else {
           if (mounted) {
               ScaffoldMessenger.of(context).showSnackBar(
                 SnackBar(content: Text('Failed to fetch history: ${response.statusCode}')),
               );
           }
        }
      } catch (e) {
          if (mounted) {
               ScaffoldMessenger.of(context).showSnackBar(
                 SnackBar(content: Text('Connection error: $e')),
               );
          }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Item History', style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
             Center(
              child: Column(
                children: [
                   Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.blue.shade200, width: 2),
                      ),
                      child: const Center(
                        child: Text(
                          'Monkey\nBarrow',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Inventory\nBarcode',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.black87),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            const Text('Barcode:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Row(
              children: [
                 Expanded(
                    child: TextField(
                      controller: _barcodeController,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                        isDense: true,
                        hintText: 'Scan / enter transition'
                      ),
                    ),
                 ),
                 const SizedBox(width: 8),
                 ElevatedButton(
                    onPressed: _fetchHistory,
                    child: const Text("Search")
                 )
              ]
            ),
            const SizedBox(height: 24),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.black54),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                   Container(
                     padding: const EdgeInsets.all(8),
                     color: Colors.grey.shade200,
                     child: const Text('Current States:', style: TextStyle(fontWeight: FontWeight.bold)),
                   ),
                   const Padding(
                     padding: EdgeInsets.all(12.0),
                     child: Column(
                       crossAxisAlignment: CrossAxisAlignment.start,
                       children: [
                          Text('• Ordered'),
                          Text('• Out-for-Delivery'),
                          Text('• Delivered'),
                          Text('• Returned'),
                          Text('• Damage/Repair'),
                          Text('• Sanitization'),
                       ],
                     ),
                   ),
                   Container(
                     padding: const EdgeInsets.all(8),
                     color: Colors.grey.shade200,
                     child: const Text('History Flow:', style: TextStyle(fontWeight: FontWeight.bold)),
                   ),
                   Padding(
                     padding: const EdgeInsets.all(12.0),
                     child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: _history.map((e) => Padding(
                          padding: const EdgeInsets.only(bottom: 8.0),
                          child: Text('${e['state']} - ${e['updated_by']} - ${e['timestamp']}'),
                        )).toList(),
                     ),
                   )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
