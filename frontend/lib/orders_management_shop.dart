//NOT CODED YET
//This is a template code we need to refine this page
//SM 28-7-26
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class OrderManagementShop extends StatelessWidget {
  const OrderManagementShop({super.key});

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
        title: const Text("Order Management Shop Home"),
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
              'Order Management',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Colors.black87),
            ),
            const SizedBox(height: 40),

            // Buttons
            ElevatedButton(
              onPressed: () => Navigator.pushNamed(context, '/updateordershop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Update Shop Order"),
            ),
            const SizedBox(height: 40),

            ElevatedButton(
              onPressed: () => Navigator.pushNamed(context, '/searchordershop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Search Shop Order"),
            ),
            const SizedBox(height: 40),

            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/pendingordershop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text("Show Pending Shop Order List"),
            ),
          ],
        ),
      ),
    );
  }
}
