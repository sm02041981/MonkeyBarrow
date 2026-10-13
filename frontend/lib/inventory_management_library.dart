/* SM:28th July 2026
Inventory Management Frontend Dart page, This program includes the following functionalities:
    Case 1: Add New Inventory
    Case 2: Update Inventory
    Case 3: Search Inventory
    Case 4: Search Inventory History
*/

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class InventoryManagementLibrary extends StatelessWidget {
  const InventoryManagementLibrary({super.key});

  Future<void> _logout(BuildContext context) async {
    // Clear any stored session/token here
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    // Navigate back to login page (ensure context still valid)
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Inventory Management for Library"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.red),
            tooltip: 'Logout',
            onPressed: () async => await _logout(context),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center, // center everything
          children: [
            // Circular logo container
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: Colors.blue.shade200, width: 2),
              ),
              child: ClipOval(
                child: Image.asset(
                  'assets/logo.png',
                  fit: BoxFit.cover,
                  width: 120,
                  height: 120,
                  errorBuilder: (context, error, stackTrace) {
                    return const Icon(Icons.error, size: 80);
                  },
                ),
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Inventory Management for Library',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.black87),
            ),
            const SizedBox(height: 40),

            // Buttons
            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/updateinventorylibrary'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Update Inventory to Library"),
            ),
            const SizedBox(height: 40),

            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/searchinventorylibrary'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Search Inventory from Library"),
            ),
            const SizedBox(height: 40),

            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/addinventorylibrary'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Add Inventory to Library"),
            ),
          ],
        ),
      ),
    );
  }
}
