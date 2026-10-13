//NOT CODED YET
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'config.dart';
import 'session_manager.dart'; // make sure you import this

class UpdateInventoryLibraryPage extends StatefulWidget {
  const UpdateInventoryLibraryPage({super.key});

  @override
  State<UpdateInventoryLibraryPage> createState() =>
      _UpdateInventoryLibraryPageState();
}

class _UpdateInventoryLibraryPageState
    extends State<UpdateInventoryLibraryPage> {
  final _serialController = TextEditingController();
  final _locationController = TextEditingController();
  final _orderIdController = TextEditingController();
  final _serialFocusNode = FocusNode();

  Map<String, dynamic>? _itemData;
  String? _selectedState;
  bool _isLoading = false;

  // State Transition Rules
  final Map<String, List<String>> _validTransitions = {
    "Available": ["Ordered", "Damage/Repair"],
    "Ordered": ["Out for Delivery", "Damage/Repair"],
    "Out for Delivery": ["Delivered", "Damage/Repair"],
    "Delivered": ["Returned", "Damage/Repair"],
    "Returned": ["Sanitization", "Damage/Repair"],
    "Sanitization": ["Available"],
    "Damage/Repair": ["Available"],
  };

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _serialFocusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    _serialController.dispose();
    _locationController.dispose();
    _orderIdController.dispose();
    _serialFocusNode.dispose();
    super.dispose();
  }

  Future<void> _logout(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
  }

  void _clearAll() {
    setState(() {
      _serialController.clear();
      _locationController.clear();
      _orderIdController.clear();
      _itemData = null;
      _selectedState = null;
    });
    _serialFocusNode.requestFocus();
  }

  void _showErrorDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.red),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                color: Colors.red,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        content: Text(
          message,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _serialFocusNode.requestFocus();
            },
            child: const Text(
              "OK",
              style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _scanAndFetch() async {
    final serialNumber = _serialController.text.trim();

    // Auto-clear barcode input field immediately for next scan
    _serialController.clear();
    /*
    if (serial_number.length != 20 || int.tryParse(serial_number) == null) {
      _showErrorDialog(
        "Invalid Serial Code",
        "You entered/scanned: '$serial_number' (${serial_number.length} digits).\n\nPlease scan or enter a valid 20-digit serial number.",
      );
      return;
    }
    */
    final isNumeric = RegExp(r'^\d{20}$').hasMatch(serialNumber);

    if (!isNumeric) {
      _showErrorDialog(
        "Invalid Serial Code",
        "You entered/scanned: '$serialNumber' (${serialNumber.length} digits).\n\nPlease scan or enter a valid 20-digit serial number.",
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _itemData = null;
    });

    try {
      final response = await http.get(
        Uri.parse(
          '${Config.apiUrl}/api/update_inventory_state/item/$serialNumber',
        ),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        setState(() {
          _itemData = data;
          _selectedState =
              null; // Reset selection so user explicitly chooses if updating state
          _locationController.text = data['item_location'] ?? '';
          _orderIdController.text = (data['order_id'] ?? '').toString();
        });
      } else {
        if (!mounted) return;
        // Requirement 1: Red popup for item not found
        _showErrorDialog(
          "Not Found",
          "serial number not found, no such book item in monkebarrow database",
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error connecting to server: $e")));
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
        _serialFocusNode.requestFocus();
      }
    }
  }

  Future<void> _updateState() async {
    final employeeId = await SessionManager.getEmployeeId();

    if (employeeId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Session expired. Please log in again.')),
      );
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    if (_itemData == null || _itemData!['serial_number'] == null) return;

    setState(() => _isLoading = true);

    try {
      final activeSerial = _itemData!['serial_number'];

      final Map<String, dynamic> payload = {
        'serial_number': activeSerial,
        'employee_id': employeeId,
      };

      // Requirement 2 & 3: Only pass non-null/modified properties
      if (_selectedState != null) {
        payload['new_state'] = _selectedState;
      }
      if (_locationController.text.trim().isNotEmpty) {
        payload['new_location'] = _locationController.text.trim();
      }
      if (_orderIdController.text.trim().isNotEmpty) {
        payload['order_id'] = _orderIdController.text.trim();
      }

      final response = await http.patch(
        Uri.parse('${Config.apiUrl}/api/update_inventory_state/stateupdate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      if (!mounted) return;

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Item updated successfully")),
        );

        Future.delayed(const Duration(seconds: 5), () {
          _clearAll();
        });

        setState(() {
          if (_selectedState != null) _itemData!['state'] = _selectedState;
          _itemData!['item_location'] = _locationController.text.trim();
          _itemData!['order_id'] = _orderIdController.text.trim();
          _selectedState = null; // Clear selection after save
        });
      } else {
        final error = jsonDecode(response.body);
        _showErrorDialog(
          "Update Failed",
          error['detail'] ?? "Failed to update item",
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error updating item: $e")));
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
        _serialFocusNode.requestFocus();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Determine allowed states based on current item state
    final String currentState = _itemData?['state'] ?? '';
    final List<String> allowedNextStates =
        _validTransitions[currentState] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text("Update Item Inventory"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.red),
            tooltip: 'Logout',
            onPressed: () async => await _logout(context),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: _serialController,
              focusNode: _serialFocusNode,
              decoration: InputDecoration(
                labelText: "Scan 20-Digit Serial Number",
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.qr_code_scanner),
                suffixIcon: _serialController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _serialController.clear();
                          setState(() {});
                        },
                      )
                    : null,
              ),
              keyboardType: TextInputType.number,
              onChanged: (_) => setState(() {}),
              onSubmitted: (_) => _scanAndFetch(),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _scanAndFetch,
                    icon: const Icon(Icons.search),
                    label: const Text("Fetch Item Details"),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _isLoading ? null : _clearAll,
                    icon: const Icon(Icons.refresh, color: Colors.red),
                    label: const Text(
                      "Clear",
                      style: TextStyle(color: Colors.red),
                    ),
                  ),
                ),
              ],
            ),

            if (_isLoading) ...[
              const SizedBox(height: 24),
              const Center(child: CircularProgressIndicator()),
            ],

            if (_itemData != null && !_isLoading) ...[
              const SizedBox(height: 24),
              const Divider(thickness: 2),
              const SizedBox(height: 8),

              const Text(
                "Item Details",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),

              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    children: [
                      _detailRow("Serial Number:", _itemData!['serial_number']),
                      _detailRow("ISBN 13:", _itemData!['item_mb_isbn13']),
                      _detailRow(
                        "Current State:",
                        _itemData!['state'],
                        isBold: true,
                      ),
                      _detailRow(
                        "Current Location:",
                        _itemData!['item_location'],
                      ),
                      _detailRow(
                        "Order ID:",
                        (_itemData!['order_id'] ?? "None").toString(),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),
              const Text(
                "Update Properties",
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),

              // Requirement 2: Dynamic state transitions based on state matrix
              DropdownButtonFormField<String>(
                initialValue: _selectedState,
                decoration: InputDecoration(
                  labelText: "Select New State (Optional)",
                  hintText: allowedNextStates.isEmpty
                      ? "No valid state transitions"
                      : "Leave empty to keep current state",
                  border: const OutlineInputBorder(),
                ),
                items: allowedNextStates
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: allowedNextStates.isEmpty
                    ? null
                    : (val) => setState(() => _selectedState = val),
              ),
              const SizedBox(height: 12),

              // Location Field
              TextField(
                controller: _locationController,
                decoration: const InputDecoration(
                  labelText: "Location (Optional)",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),

              // Order ID Field
              TextField(
                controller: _orderIdController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: "Order ID (Optional)",
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),

              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _updateState,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                  icon: const Icon(Icons.save),
                  label: const Text("Save Changes"),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _detailRow(String label, String? value, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
          Text(
            value ?? "N/A",
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              color: isBold ? Colors.blue : Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}
