//Final Program validated on 18sept 2026
//When Admin logs in - he sees this page, this is admin home page
// once Admin Logs in - he sees 3 options
//1. Employee Management
//2. Inventory Management
//3. Order management
//------------------------------------------------------------------------
// Scope for enhancements - we will add more links to this page related to
//   Order summary, customer insight, sales insights
//------------------------------------------------------------------------

//import 'package:flutter/material.dart'; → Brings in Flutter’s UI toolkit.
//import 'package:shared_preferences/shared_preferences.dart'; → Allows saving
//and clearing local key‑value data (used for logout).
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

//class AdminHomePage extends StatelessWidget { → Defines a stateless
//widget called AdminHomePage.
//const AdminHomePage({super.key}); → Constructor with optional widget key.
class AdminHomePage extends StatelessWidget {
  const AdminHomePage({super.key});

  //helper logout function
  Future<void> _logout(BuildContext context) async {
    // Clear any stored session/token here
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();

    // Navigate back to login page (ensure context still valid)
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
  }

  //BUILD UI
  //@override Widget build(BuildContext context) { → Builds the widget tree.
  //return Scaffold(...); → Provides page structure with app bar and body.
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      //AppBar section → Top bar of the page.
      appBar: AppBar(
        title: const Text(
          'Admin Dashboard',
          style: TextStyle(color: Colors.black),
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.red),
            tooltip: 'Logout',
            onPressed: () => _logout(context),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo Section
            Container(
              width: 140,
              height: 140,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: Colors.blue.shade200, width: 2),
              ),
              child: ClipOval(
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    Image.asset(
                      'assets/logo.png',
                      fit: BoxFit.cover,
                      width: 150,
                      height: 150,
                      errorBuilder: (context, error, stackTrace) {
                        return const Icon(Icons.error, size: 150);
                      },
                    ),
                  ],
                ),
              ),
            ),
            const Text(
              ' ',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white, // overlay text color
                shadows: [Shadow(blurRadius: 4, color: Colors.black)],
              ),
            ),
            const SizedBox(height: 40),
            // Links
            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/employeemanagement'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text('Employee Management'),
            ),
            const SizedBox(height: 40), // bigger gap
            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/inventorymanagementlibrary'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text('Inventory Management for Library'),
            ),
            const SizedBox(height: 40),
            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/inventorymanagementshop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text('Inventory Management for Online Shop'),
            ),
            const SizedBox(height: 40), // bigger gap
            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/ordermanagementlibrary'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text('Order Management for Library'),
            ),
            const SizedBox(height: 40), // bigger gap
            ElevatedButton(
              onPressed: () =>
                  Navigator.pushNamed(context, '/ordermanagementshop'),
              style: ElevatedButton.styleFrom(minimumSize: const Size(220, 60)),
              child: const Text('Order Management for Shop'),
            ),
          ],
        ),
      ),
    );
  }
}
