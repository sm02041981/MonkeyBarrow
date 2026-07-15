import 'package:flutter/material.dart';
import 'login_page.dart';
import 'inventory_page.dart';
import 'admin_page.dart';
import 'history_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MonkeyBarrow',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const LoginPage(),
        '/inventory': (context) => const InventoryPage(),
        '/admin': (context) => const AdminPage(),
        '/history': (context) => const HistoryPage(),
      },
    );
  }
}
