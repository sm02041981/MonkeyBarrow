import 'package:flutter/material.dart';

import 'login_page.dart';

import 'admin_home_page.dart';
import 'employee_home_page.dart';

import 'employee_management.dart';
import 'orders_management_library.dart';
import 'orders_management_shop.dart';

import 'inventory_management_library.dart';
import 'inventory_management_shop.dart';

import 'add_inventory_library.dart';
import 'add_inventory_shop.dart';

import 'inventory_history_library_page.dart';
import 'inventory_history_shop_page.dart';

import 'update_inventory_library_page.dart';
import 'update_inventory_shop_page.dart';

import 'search_inventory_library.dart';
import 'search_inventory_shop.dart';

import 'search_order_library.dart';
import 'show_pending_order_library.dart';
import 'update_order_library.dart';

import 'search_order_shop.dart';
import 'show_pending_order_shop.dart';
import 'update_order_shop.dart';

void main() {
  // runapp is function we are calling to run application on flutter
  //we are calling runApp in main function
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
        //Section#1
        //details for login page
        '/': (context) => const LoginPage(),

        //Section#2
        //details for admin home page
        '/admin': (context) => const AdminHomePage(),

        //details for employee home page
        '/employeehome': (context) => const EmployeeHomePage(),

        //Section#3
        //details for all functionalities those can be routed from
        //admin & employee home pages
        //admin can see all management links
        //employee can see only inventory and order
        '/employeemanagement': (context) => const EmployeeManagement(),
        '/inventorymanagementlibrary': (context) =>
            const InventoryManagementLibrary(),
        '/inventorymanagementshop': (context) =>
            const InventoryManagementShop(),

        '/ordermanagementlibrary': (context) => const OrderManagementLibrary(),
        '/ordermanagementshop': (context) => const OrderManagementShop(),

        //Section#4
        //employeemanagement has no other link attached for now

        //Section#5
        //Inventorymanagement with child links
        '/searchinventorylibrary': (context) =>
            const SearchInventoryLibraryPage(),
        '/searchinventoryshop': (context) => const SearchInventoryShopPage(),

        '/updateinventorylibrary': (context) =>
            const UpdateInventoryLibraryPage(),
        '/updateinventoryshop': (context) => const UpdateInventoryShopPage(),

        '/addinventorylibrary': (context) => const AddInventoryLibraryPage(),
        '/addinventoryshop': (context) => const AddInventoryShopPage(),

        '/historylibrary': (context) => const InventoryHistoryLibraryPage(),
        '/historyshop': (context) => const InventoryHistoryShopPage(),

        //Section#6
        //LIBRARY Ordermanagement with child links
        '/updateorderlibrary': (context) => const UpdateOrderLibraryPage(),
        '/searchorderlibrary': (context) => const SearchOrderLibraryPage(),
        '/showpendingorderlibrary': (context) =>
            const ShowPendingOrderLibraryPage(),

        //Section#6
        //SHOP Ordermanagement with child links
        '/updateordershop': (context) => const UpdateOrderShopPage(),
        '/searchordershop': (context) => const SearchOrderShopPage(),
        '/showpendingordershop': (context) => const ShowPendingOrderShopPage(),
      },
    );
  }
}
