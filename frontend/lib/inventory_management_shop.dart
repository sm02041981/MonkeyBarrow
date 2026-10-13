//NOT CODED YET
/* SM:28th July 2026
Inventory Management Frontend Dart page, This program includes the following functionalities:
    Case 1: Add New Inventory to Online Shop
    Case 2: Update Inventory to Online Shop
    Case 3: Search Inventory in Online Shop
    Case 4: Search Inventory History in Online Shop
*/

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class InventoryManagementShop extends StatelessWidget {
  const InventoryManagementShop({super.key});

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
        title: const Text("Inventory Management for Shop"),
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
              'Inventory Management for Shop',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.black87),
            ),
            const SizedBox(height: 40),

            // Buttons
            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/updateinventoryshop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Update Inventory to Shop"),
            ),
            const SizedBox(height: 40),

            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/searchinventoryshop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Search Inventory from Shop"),
            ),
            const SizedBox(height: 40),

            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/addinventoryshop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Add Inventory to Shop"),
            ),
          ],
        ),
      ),
    );
  }
}
