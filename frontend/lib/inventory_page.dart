import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'config.dart';

class InventoryPage extends StatefulWidget {
  const InventoryPage({super.key});

  @override
  State<InventoryPage> createState() => _InventoryPageState();
}

class _InventoryPageState extends State<InventoryPage> {
  final _barcodeController = TextEditingController();
  final _serialNumberController = TextEditingController();
  final _productNameController = TextEditingController();
  final _authorController = TextEditingController();
  final _purchaseDateController = TextEditingController();
  final _weightController = TextEditingController();
  final _ageGroupController = TextEditingController();
  final _categoryController = TextEditingController();
  final _lastAgentController = TextEditingController();
  final _updateTimeController = TextEditingController();

  String _currentState = 'Available';
  String _nextState = 'Ordered';

  final Map<String, List<String>> _validTransitions = {
    'Available': ['Ordered', 'Damage/Repair'],
    'Ordered': ['Out for Delivery', 'Damage/Repair'],
    'Out for Delivery': ['Delivered', 'Damage/Repair'],
    'Delivered': ['Returned'],
    'Returned': ['Sanitization', 'Damage/Repair'],
    'Sanitization': ['Available'],
    'Damage/Repair': ['Available'],
  };

  Future<void> _scanBarcode() async {
    // Mocking a scan by populating the field, and fetching from backend
    final barcode = '1234567890';
    setState(() {
      _barcodeController.text = barcode;
    });

    try {
      final response = await http.get(Uri.parse(Config.apiUrl + '/api/inventory/$barcode'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _currentState = data['state'] ?? 'Available';
          _serialNumberController.text = data['serial_number'] ?? '';
          _productNameController.text = data['title'] ?? '';
          _authorController.text = data['author'] ?? '';
          _purchaseDateController.text = data['date_of_purchase'] ?? '';
          _weightController.text = data['weight'] ?? '';
          _ageGroupController.text = data['age_group'] ?? '';
          _categoryController.text = data['category'] ?? '';
          _lastAgentController.text = data['last_updated_by']?.toString() ?? '';
          _updateTimeController.text = data['last_updated'] ?? '';
          _nextState = _validTransitions[_currentState]!.first;
        });
        if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Item fetched from backend')),
            );
        }
      } else {
        if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Failed to fetch item: ${response.statusCode}')),
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

  Future<void> _saveState() async {
     try {
       final response = await http.patch(
          Uri.parse(Config.apiUrl + '/api/inventory/state'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
             'barcode': _barcodeController.text,
             'new_state': _nextState,
             'agent_id': 1 // mock agent id
          }),
        );

        if (response.statusCode == 200) {
             final data = jsonDecode(response.body);
             setState(() {
                _currentState = data['new_state'];
                _nextState = _validTransitions[_currentState]!.first;
             });
             if (mounted) {
                 ScaffoldMessenger.of(context).showSnackBar(
                   const SnackBar(content: Text('State updated!')),
                 );
             }
        } else {
             if (mounted) {
                 ScaffoldMessenger.of(context).showSnackBar(
                   SnackBar(content: Text('Failed to update: ${response.body}')),
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

  Widget _buildField(String label, TextEditingController controller, {bool expanded = false}) {
    final field = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        const SizedBox(height: 6),
        TextField(
          controller: controller,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            isDense: true,
          ),
          readOnly: label.contains('State') || label.contains('status'),
        ),
        const SizedBox(height: 12),
      ],
    );
    return expanded ? Expanded(child: field) : field;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Inventory', style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => Navigator.pushNamed(context, '/history'),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
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
            const SizedBox(height: 24),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _scanBarcode,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey.shade200,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4), side: const BorderSide(color: Colors.black54)),
                ),
                child: const Text('Scan Or Name'),
              ),
            ),
            const SizedBox(height: 20),

            _buildField('Barcode', _barcodeController),
            _buildField('Unique Serial Number', _serialNumberController),
            _buildField('Name Of Product', _productNameController),
            _buildField('Author/Manufacturer', _authorController),
            _buildField('Date Of Purchase', _purchaseDateController),

            Row(
              children: [
                _buildField('Weight', _weightController, expanded: true),
                const SizedBox(width: 12),
                _buildField('Age Group', _ageGroupController, expanded: true),
              ],
            ),
            _buildField('Category', _categoryController),

            const SizedBox(height: 16),
            const Text('Next State', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _nextState,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                      isDense: true,
                    ),
                    items: _validTransitions[_currentState]!.map((String s) => DropdownMenuItem<String>(value: s, child: Text(s))).toList(),
                    onChanged: (val) {
                      if (val != null) {
                        setState(() {
                          _nextState = val;
                        });
                      }
                    },
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: _saveState,
                  style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(4),
                        side: const BorderSide(color: Colors.black),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
                  ),
                  child: const Text('Save'),
                ),
              ],
            ),

            const SizedBox(height: 24),
            _buildField('Last status changed by agent', _lastAgentController),
            _buildField('Time of Update', _updateTimeController),

            if (_currentState == 'Damage/Repair') ...[
              const SizedBox(height: 10),
              ElevatedButton(
                onPressed: () {
                   setState(() {
                      _nextState = 'Available';
                   });
                   _saveState();
                },
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                child: const Text('Mark as Repaired'),
              )
            ]
          ],
        ),
      ),
    );
  }
}
