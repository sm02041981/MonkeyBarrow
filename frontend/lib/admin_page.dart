/*
SM-22July2026 - Coding and refining the AdminPage widget for the MonkeyBarrow app.
Admin screen for adding employees to the system. It includes fields for mobile number, employee ID, and employment status. 
The data is sent to the backend via an HTTP POST request.
*/

//-------------
//1. IMPORTS
//-------------
/*
Brings in Flutter’s Material Design UI library (widgets like Scaffold, AppBar, TextField, ElevatedButton).#
Background: Flutter compiles these widgets into native code for iOS/Android.
*/
import 'package:flutter/material.dart';

/*
Imports the HTTP client package for making network requests.
as http means you’ll call functions like http.post(...).
Background: This package uses Dart’s dart:io under the hood to open sockets and send HTTP requests.
*/
import 'package:http/http.dart' as http;

/*
Provides functions like jsonEncode and jsonDecode.
Background: Converts Dart objects (Map, List) into JSON strings for sending to backend APIs.
*/
import 'dart:convert';

/*
Imports your own file config.dart.
Likely contains constants such as Config.apiUrl (the base URL of your backend server).
*/
import 'config.dart';

//-------------
//2. Widget Class
//-------------

/*
Defines a screen (page) called AdminPage.
StatefulWidget means it has mutable state (like form inputs).
super.key passes a unique identifier for widget rebuilding.
 */
class AdminPage extends StatefulWidget {
  const AdminPage({super.key});

//Connects this widget to its state class _AdminPageState.
  @override
  State<AdminPage> createState() => _AdminPageState();
}

//-------------
//3. State  Class
//-------------

/*
TextEditingController → manages text input fields (reads/writes values).
_status → holds dropdown value (default: "Active").
Background: Flutter keeps these in memory while the widget is alive.
 */
class _AdminPageState extends State<AdminPage> {
  final _mobileController = TextEditingController();
  final _employeeIdController = TextEditingController();
  String _status = 'Active';


//-------------
//4. Backend Logic
//-------------

/*
Declares an async function (returns Future<void).
Used when you want to call backend APIs.
*/
  Future<void> _saveEmployee() async {

/*
Makes a POST request to your backend (/api/admin/employee).
headers → tells backend you’re sending JSON.
body → encodes form data into JSON.
Background: Dart opens a TCP connection, sends HTTP request, waits for response.
*/

      try {
         final response = await http.post(
          Uri.parse('${Config.apiUrl}/api/admin/employee'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
             'mobile_number': _mobileController.text,
             'employee_id': _employeeIdController.text,
             'status': _status
          }),
        );

/*
If backend returns 200 OK, show success message.
mounted ensures widget is still in the widget tree (avoids errors if user navigated away).
Background: Flutter builds a SnackBar widget and overlays it on screen.
*/
        if (response.statusCode == 200) {
            if (mounted) {
               ScaffoldMessenger.of(context).showSnackBar(
                 const SnackBar(content: Text('Employee Saved!')),
               );
            }
        } 
        //If backend returns error (e.g., 400, 500), show failure message with backend’s response body.
        else {
            if (mounted) {
               ScaffoldMessenger.of(context).showSnackBar(
                 SnackBar(content: Text('Failed: ${response.body}')),
               );
            }
        }
        //If network fails (no internet, server down), catch exception and show error.
      } catch (e) {
          if (mounted) {
               ScaffoldMessenger.of(context).showSnackBar(
                 SnackBar(content: Text('Connection error: $e')),
               );
          }
      }
  }
//-------------
//4. UI Build
//-------------
/*
build method constructs the UI tree.
Scaffold → provides page structure (app bar, body, etc.).
 */
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      //Displays top bar with title.
      //AppBar → Material Design top bar with title and action buttons.
      //IconButton → navigates to inventory page when pressed.
      //Background: Flutter maintains a navigation stack (like browser history).
      appBar: AppBar(
        title: const Text('Admin Dashboard', style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
        actions: [
          IconButton(
            icon: const Icon(Icons.inventory),
            onPressed: () => Navigator.pushNamed(context, '/inventory'),
          )
        ],
      ),
      //SingleChildScrollView → allows scrolling if content is long and overflow.      
      //column → arranges widgets vertically (like a list).  
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
             Center(
              child: Column(
                children: [
                  //Circular container with text inside (like a logo).
                  //Background: Flutter draws shapes using Skia graphics engine.
                   Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.blue.shade200, width: 2),
                      ),
                      child: const Center(
                        child: Text(
                          'Monkey\nBarrow',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Employee\nManagement',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 16, color: Colors.black87),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 40),
            const Text('Mobile Number:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _mobileController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
            ),
            const SizedBox(height: 20),
            const Text('Employee ID:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _employeeIdController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
            ),
            const SizedBox(height: 20),
            const Text('Employment Status:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue: _status,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
              items: ['Active', 'Suspended', 'Not in Firm']
                  .map((String s) => DropdownMenuItem<String>(value: s, child: Text(s)))
                  .toList(),
              onChanged: (val) {
                 if (val != null) {
                    setState(() {
                       _status = val;
                    });
                 }
              },
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _saveEmployee,
                style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(4),
                        side: const BorderSide(color: Colors.black),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('Save Employee', style: TextStyle(fontSize: 16)),
              ),
            )
          ],
        ),
      ),
    );
  }
}
