//SM Last Updated & reviewed on - 1st oct 2026 - Add Inventory function
// its adds the inventory and update the quantity if the item is already present in monkeybarrow database

//import details
//flutter/material.dart → gives access to Flutter’s UI widgets (Scaffold, TextFormField, Buttons, etc.).
//http → used to make REST API calls to your backend.
//dart:convert → provides jsonEncode and jsonDecode for converting data to/from JSON.
//shared_preferences → stores small pieces of data locally (like login session info).
//config.dart → likely contains your API base URL.
//session_manager.dart → handles user session (e.g., employee ID retrieval).

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'config.dart';
import 'session_manager.dart'; // make sure you import this
import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io'; // Needed for File
import 'package:image_picker/image_picker.dart';

// AddInventoryPage is the main UI for adding or updating books in the inventory.
// This defines a stateful widget — meaning it can change dynamically (e.g., enabling/disabling fields).
//The State class _AddInventoryPageState holds all logic and UI state.

class AddInventoryLibraryPage extends StatefulWidget {
  const AddInventoryLibraryPage({super.key});

  @override
  State<AddInventoryLibraryPage> createState() =>
      _AddInventoryLibraryPageState();
}

class _AddInventoryLibraryPageState extends State<AddInventoryLibraryPage> {
  //_selectedType tracks which inventory type is selected (Book, Toy, etc.).
  String _selectedType = "Book";

  // Form Key for validation
  //_formKey is used to validate the form fields.
  final _formKey = GlobalKey<FormState>();

  //Each TextEditingController manages the text input for a field (like ISBN, title, author).
  //You can read or clear their values anytime.
  final _mbisbn13Controller = TextEditingController();
  final _titleController = TextEditingController();
  final _authorController = TextEditingController();
  final _categoryController = TextEditingController();
  final _weightController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _quantityController = TextEditingController();
  final _mrpController = TextEditingController();
  final _imagefpController = TextEditingController();
  final _lastupdatedbyController = TextEditingController();
  //final _imageotherurlController = TextEditingController();

  //Defines the dropdown list for age categories.
  final List<String> _ageCategoryOptions = [
    "0 to 3 Years",
    "3 to 6 Years",
    "6 to 9 Years",
    "9 + Years",
  ];

  //_selectedAgeCategory stores the user’s selection.
  String? _selectedAgeCategory;

  // Focus nodes - Used to control keyboard focus (e.g., automatically focus on barcode field when page loads).
  final FocusNode _barcodeFocusNode = FocusNode();
  final FocusNode _quantityFocusNode = FocusNode();

  // UI state flags - These are boolean controls how UI behaves
  //_fieldsEnabled → whether text fields are editable.
  bool _fieldsEnabled = false;

  //_manualEntryMode → true when user enters details manually.
  bool _manualEntryMode = false;
  bool _isBarcodeFocused = false;

  //_updateQuantityMode → true when updating quantity of existing item.
  bool _updateQuantityMode = false;

  //_quantityEnabled → enables quantity field.
  bool _quantityEnabled = false;

  // Guard flag against duplicate/concurrent requests - _isLoading → shows loading spinner during API calls.
  bool _isLoading = false;

  final ImagePicker _picker = ImagePicker();
  List<XFile?> _images = List<XFile?>.filled(3, null);

  //initState() runs once when the widget is created.
  //Adds a listener to detect when barcode field gains/loses focus.
  //Automatically focuses the barcode field after the first frame.
  @override
  void initState() {
    super.initState();
    _barcodeFocusNode.addListener(_onFocusChange);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _barcodeFocusNode.requestFocus();
    });
  }

  //Updates _isBarcodeFocused whenever focus changes.
  void _onFocusChange() {
    setState(() => _isBarcodeFocused = _barcodeFocusNode.hasFocus);
  }

  //// Cleans up controllers and focus nodes to prevent memory leaks
  @override
  void dispose() {
    _barcodeFocusNode.removeListener(_onFocusChange);
    _mbisbn13Controller.dispose();
    _titleController.dispose();
    _authorController.dispose();
    _categoryController.dispose();
    _weightController.dispose();
    _descriptionController.dispose();
    _quantityController.dispose();
    _mrpController.dispose();
    _imagefpController.dispose();
    _lastupdatedbyController.dispose();
    //_imageotherurlController.dispose();
    _barcodeFocusNode.dispose();
    _quantityFocusNode.dispose();
    super.dispose();
  }

  //Resets the form to its initial state.
  void _resetFormState() {
    setState(() {
      _fieldsEnabled = false;
      _manualEntryMode = false;
      _updateQuantityMode = false;
      _quantityEnabled = false;
      _selectedAgeCategory = null;
      _mbisbn13Controller.clear();
      _titleController.clear();
      _authorController.clear();
      _categoryController.clear();
      _weightController.clear();
      _descriptionController.clear();
      _quantityController.clear();
      _mrpController.clear();
      _imagefpController.clear();
      _lastupdatedbyController.clear();
      //_imageotherurlController.clear();

      // Reset images
      _images = List<XFile?>.filled(3, null);
    });
    _formKey.currentState?.reset();
    _barcodeFocusNode.requestFocus();
  }

  //Clears saved session and redirects to login screen.
  //Call to logout function
  Future<void> _logout(BuildContext context) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
  }

  //Prevents duplicate requests and shows loading state.
  Future<bool> _fetchBookDetails(String mbIsbn13) async {
    if (_isLoading) return false;
    setState(() => _isLoading = true);

    //Makes a GET request to your backend to check if the book exists.
    try {
      final dbResponse = await http.get(
        Uri.parse('${Config.apiUrl}/api/inventory/$mbIsbn13'),
      );

      //if response is not success then if block will execute and throw exception
      if (dbResponse.statusCode != 200) {
        throw Exception(
          "Backend server returned from dart file ${dbResponse.statusCode}",
        );
      }

      //Parses the JSON response and extracts status/data.
      //print("DB API response code from dart file: ${dbResponse.statusCode}");
      //print("DB Books API raw body from dart file: ${dbResponse.body}");
      final resBody = jsonDecode(dbResponse.body);
      final String decision = resBody['status'] ?? 'NOT_FOUND';
      final Map<String, dynamic> data = resBody['data'] ?? {};

      if (!mounted) return true;

      //Each case updates the UI accordingly using setState() and shows dialogs/snackbars.
      switch (decision) {
        // CASE 1: Book already exists in MonkeyBarrow DB
        case "EXISTS_IN_DB":
          setState(() {
            _mbisbn13Controller.text = (data['mb_isbn13'] ?? '').toString();
            _titleController.text = data['title'] ?? '';
            _authorController.text = data['author'] ?? '';
            _categoryController.text = data['category'] ?? '';
            _weightController.text = (data['weight'] ?? '').toString();
            _descriptionController.text = data['description'] ?? '';
            _imagefpController.text = data['image_fp_url'] ?? '';
            _lastupdatedbyController.text = data['last_updated_by'] ?? '';
            _quantityController.text = (data['quantity'] ?? '').toString();
            _mrpController.text = (data['mrp'] ?? '').toString();

            final ageVal = data['age_group'] ?? '';
            _selectedAgeCategory = _ageCategoryOptions.contains(ageVal)
                ? ageVal
                : null;
            _fieldsEnabled = false;
          });
          showDialog(
            context: context,
            builder: (BuildContext dialogContext) {
              return AlertDialog(
                title: const Text(
                  "Book Already Exists",
                  style: TextStyle(
                    color: Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                content: const Text(
                  "Book already exists in MonkeyBarrow Database.\nWould you like to update quantity?",
                ),
                actions: [
                  TextButton(
                    child: const Text("NO"),
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      _resetFormState();
                    },
                  ),
                  TextButton(
                    child: const Text("YES"),
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      setState(() {
                        _quantityController.clear();
                        _quantityEnabled = true;
                        _updateQuantityMode = true;
                      });
                      FocusScope.of(context).requestFocus(_quantityFocusNode);
                    },
                  ),
                ],
              );
            },
          );
          break;

        // CASE 2: Fetched from Google Books API
        case "FETCHED_FROM_GOOGLE":
          print(
            "Inside Dart File : Case2  - Book not found in DB, checking Google Books API...",
          );
          print("Querying Google Books for ISBN inside dart file: $mbIsbn13");

          setState(() {
            _fieldsEnabled = true; // enable fields first
            _updateQuantityMode = false;
            _quantityEnabled = true;
            final volumeInfo = resBody['data'] ?? {};
            //print("DB API response code from dart file: ${volumeInfo}");

            _mbisbn13Controller.text = (volumeInfo['mb_isbn13'] ?? '')
                .toString();
            _titleController.text = volumeInfo['title'] ?? '';
            _authorController.text = volumeInfo['author'] ?? '';
            _categoryController.text = volumeInfo['category'] ?? '';
            _weightController.text = (volumeInfo['weight'] ?? '').toString();
            _descriptionController.text = volumeInfo['description'] ?? '';
            _imagefpController.text = volumeInfo['image_fp_url'] ?? '';
          });
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                "Details fetched from Google Books. Please fill required fields (Age, Quantity, MRP).",
              ),
              backgroundColor: Colors.blue,
            ),
          );
          break;

        // CASE 3: Not found on Google API
        case "NOT_FOUND":
        default:
          showDialog(
            context: context,
            builder: (BuildContext dialogContext) {
              return AlertDialog(
                title: const Text(
                  "Book Not Found",
                  style: TextStyle(
                    color: Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                content: const Text(
                  "Book details not found in database or Google Books.\nPlease enter details manually.",
                ),
                actions: [
                  TextButton(
                    child: const Text("OK"),
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      setState(() {
                        _mbisbn13Controller.text = mbIsbn13;
                        _fieldsEnabled = true;
                        _manualEntryMode = true;
                        _updateQuantityMode = false;
                        _quantityEnabled = true;
                      });
                    },
                  ),
                ],
              );
            },
          );
          break;
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error fetching details: $e')));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
    return true;
  }

  // _addBook() helper function which makes api call to do following tasks
  // 1. Insert a book into database, create serial book entries into database
  // 2. Print the serial bar code to be pasted on the book
  // 3. upload the image to google cloud and share the public url for shopify
  // 4. upload the book to shopify website
  Future<void> _addBook() async {
    // fetching & preserving the employeeid details across the session
    final employeeId = await SessionManager.getEmployeeId();
    if (employeeId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Session expired. Please log in again.')),
      );
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    // Prevent execution if barcode scanning or another request is
    //  currently loading
    if (_isLoading) return;
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);

    //generating a payload which is to be sent to api via request json

    try {
      var uri = Uri.parse('${Config.apiUrl}/api/inventory/addbook');
      var request = http.MultipartRequest('POST', uri);

      final bookData = jsonEncode({
        'mb_isbn13': _mbisbn13Controller.text.trim(),
        'title': _titleController.text.trim(),
        'author': _authorController.text.trim(),
        'age_group': _selectedAgeCategory ?? '',
        'category': _categoryController.text.trim(),
        'weight': _weightController.text.trim(),
        'description': _descriptionController.text.trim(),
        'quantity': int.tryParse(_quantityController.text.trim()) ?? 0,
        'mrp': double.tryParse(_mrpController.text.trim()) ?? 0.0,
        'image_fp_url': _imagefpController.text.trim(),
        'last_updated_by': employeeId,
      });
      // request is a variable which passes multipart request and we are
      // capturing fields payload below
      request.fields['book_data_str'] = bookData;

      // request is a variable which passes multipart request and we are
      // multiple files to request variable which will be appended to request
      for (final img in _images) {
        if (img != null) {
          final bytes = await img.readAsBytes();
          request.files.add(
            http.MultipartFile.fromBytes('files', bytes, filename: img.name),
          );
        }
      }

      // Send request
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (!mounted) return;
      if (response.statusCode == 200) {
        print('Book inserted successfully: ${response.body}');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Book added successfully")),
        );
        _resetFormState();
      } else {
        print(
          'Failed to insert book: ${response.statusCode} - ${response.body}',
        );
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Book Insertion Failed: ${response.body}")),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error adding book: $e')));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // _updateQuantity helper function which makes api call to do following tasks
  // 1. In Json it pass: isbn, additional quantity, last updated by & rack code
  // 2. As the book is already present in book table,
  // 2.a it create serial book entries into database
  // 3. Print the serial bar code to be pasted on the book
  // 4. update the new available book quantity to shopify website

  Future<void> _updateQuantity() async {
    // fetching & preserving the employeeid details across the session
    final employeeId = await SessionManager.getEmployeeId();
    if (employeeId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Session expired. Please log in again.')),
      );
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    if (_isLoading) return;

    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    //generating a payload which is to be sent to api via request json
    // In Json it pass: isbn, additional quantity, last updated by & rack code

    try {
      final payload = {
        'mb_isbn13': _mbisbn13Controller.text.trim(),
        'quantity': _quantityController.text.trim(),
        'last_updated_by': employeeId,
        'rack_code': "",
      };

      //here we are just receiving the response of our post api call
      //Sends the data to your backend to add a new book.
      final response = await http.post(
        Uri.parse('${Config.apiUrl}/api/inventory/updatequantity'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      // FIXED: Was 'if (mounted) return;' now corrected to '!mounted'
      if (!mounted) return;

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Quantity updated successfully")),
        );
        // Reset form state after update success
        _resetFormState();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Quantity Updated Failed: ${response.body}")),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error updating quantity: $e')));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // _addItem() helper function which makes api call to do following tasks
  // 1. Insert a non-book items into database,
  // 1.A. Create serial non-book items entries into database
  // 2. Print the serial bar code to be pasted on the non-book items
  // 3. upload the image to google cloud and share the public url for shopify
  // 4. upload the book to shopify website

  Future<void> _addItem() async {
    // fetching & preserving the employeeid details across the session
    final employeeId = await SessionManager.getEmployeeId();
    if (employeeId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Session expired. Please log in again.')),
      );
      Navigator.pushReplacementNamed(context, '/login');
      return;
    }

    //Prevent execution if barcode scanning or another request is
    //  currently loading
    if (_isLoading) return;
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);

    //generating a payload which is to be sent to api via request json
    try {
      var uri = Uri.parse('${Config.apiUrl}/api/inventory/additem');
      var request = http.MultipartRequest('POST', uri);

      final payload = jsonEncode({
        'mbcode': _mbisbn13Controller.text.trim(),
        'title': _titleController.text.trim(),
        'brand': _authorController.text.trim(),
        'age_group': _selectedAgeCategory ?? '',
        'category': _categoryController.text.trim(),
        'weight': _weightController.text.trim(),
        'description': _descriptionController.text.trim(),
        'quantity': _quantityController.text.trim(),
        'mrp': double.tryParse(_mrpController.text.trim()) ?? 0.0,
        'last_updated_by': employeeId,
        'inventory_type': _selectedType,
      });
      // request is a variable which passes multipart request and we are
      // capturing fields payload below
      request.fields['item_data_str'] = payload;

      // request is a variable which passes multipart request and we are
      // multiple files to request variable which will be appended to request
      for (final img in _images) {
        if (img != null) {
          final bytes = await img.readAsBytes();
          request.files.add(
            http.MultipartFile.fromBytes('files', bytes, filename: img.name),
          );
        }
      }

      // Send request - Sends the data to your backend to add a new item.

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      // here we are just receiving the response of our post api call
      // FIXED: Was 'if (mounted) return;' now corrected to '!mounted'
      if (!mounted) return;
      if (response.statusCode == 200) {
        print('Item inserted successfully: ${response.body}');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Item added successfully")),
        );
        // Reset form state after update success
        _resetFormState();
      } else {
        print('Failed item insert: ${response.statusCode} - ${response.body}');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Item insertion failed: ${response.body}")),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error adding item: $e')));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  //BUILD UI
  //Uses Scaffold for page layout.
  //Form wraps all input fields for validation.
  //Conditional rendering shows either Book form or Generic form.
  //Buttons at the bottom trigger appropriate actions.

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Add Inventory"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.red),
            tooltip: 'Logout',
            onPressed: () async => await _logout(context),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              // Row for Inventory Type
              Row(
                children: [
                  const Expanded(
                    flex: 1,
                    child: Text(
                      "Inventory Type - (Book / Toy / Premium-Toy)",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color.fromARGB(255, 2, 27, 3),
                      ),
                    ),
                  ),
                  Expanded(
                    flex: 1,
                    child: DropdownButton<String>(
                      value: _selectedType,
                      isExpanded: true,
                      items: ['Book', 'Toy', 'PremiumToy']
                          .map(
                            (s) => DropdownMenuItem(value: s, child: Text(s)),
                          )
                          .toList(),
                      //onChanged: (val) => setState(() => _selectedType = val!),
                      onChanged: (val) {
                        setState(() {
                          _selectedType = val!;
                          _resetFormState(); // clear all controllers and reset flags
                        });
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Conditional rendering
              if (_selectedType == "Book")
                ..._buildBookForm()
              else
                ..._buildGenericForm(),

              //3Images code for Image upload
              // rendering image slots just before add / clear buttons
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: List.generate(3, (index) {
                  final img = _images[index];
                  return GestureDetector(
                    onTap: () => _pickImage(index),
                    child: Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.blueAccent),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: img != null
                          ? kIsWeb
                                ? Image.network(img.path, fit: BoxFit.cover)
                                : Image.file(File(img.path), fit: BoxFit.cover)
                          : const Icon(
                              Icons.camera_alt,
                              size: 40,
                              color: Colors.grey,
                            ),
                    ),
                  );
                }),
              ),

              // rendering  add / clear buttons
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _isLoading
                          ? null
                          : (_selectedType == "Book"
                                ? (_updateQuantityMode
                                      ? _updateQuantity
                                      : _addBook)
                                : _addItem),
                      child: _isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : Text(
                              _selectedType == "Book"
                                  ? (_updateQuantityMode
                                        ? "Update Quantity"
                                        : "Add Book")
                                  : "Add Item",
                            ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _isLoading ? null : _resetFormState,
                      child: const Text("Clear"),
                    ),
                  ),
                ],
              ), //Row end
            ],
          ),
        ),
      ),
    );
  }

  // Existing Book form (reuse your current fields)
  List<Widget> _buildBookForm() {
    return [
      TextFormField(
        controller: _mbisbn13Controller,
        focusNode: _barcodeFocusNode,
        decoration: const InputDecoration(labelText: "ISBN13 / Barcode"),
        keyboardType: TextInputType.number,
        textInputAction: TextInputAction.search,
        onFieldSubmitted: (val) async {
          if (val.trim().isNotEmpty) {
            await _fetchBookDetails(val.trim());
          }
        },
      ),
      const SizedBox(height: 12),
      TextFormField(
        controller: _titleController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(labelText: "Title"),
      ),
      TextFormField(
        controller: _authorController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(labelText: "Author"),
      ),
      TextFormField(
        controller: _categoryController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(labelText: "Category"),
      ),
      TextFormField(
        controller: _weightController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(labelText: "Weight"),
      ),
      TextFormField(
        controller: _descriptionController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(labelText: "Description"),
        maxLines: 3,
      ),
      TextFormField(
        controller: _imagefpController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(labelText: "Image Front URL"),
      ),
      TextFormField(
        controller: _lastupdatedbyController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(labelText: "Last Updated By"),
      ),

      const SizedBox(height: 12),
      // Age Category Dropdown (Mandatory)
      DropdownButtonFormField<String>(
        initialValue: _selectedAgeCategory,
        decoration: const InputDecoration(
          labelText: "Age Category *",
          labelStyle: TextStyle(color: Colors.red),
          floatingLabelStyle: TextStyle(color: Colors.red),
        ),
        items: _ageCategoryOptions.map((String category) {
          return DropdownMenuItem<String>(
            value: category,
            child: Text(category),
          );
        }).toList(),
        onChanged: _fieldsEnabled
            ? (String? newValue) {
                setState(() {
                  _selectedAgeCategory = newValue;
                });
              }
            : null,
        validator: (value) {
          if (_fieldsEnabled && (value == null || value.isEmpty)) {
            return 'Please select an Age Category';
          }
          return null;
        },
      ),
      // Quantity Field (Mandatory)
      TextFormField(
        controller: _quantityController,
        focusNode: _quantityFocusNode,
        enabled: _quantityEnabled || _fieldsEnabled,
        decoration: const InputDecoration(
          labelText: "Quantity *",
          labelStyle: TextStyle(color: Colors.red),
          floatingLabelStyle: TextStyle(color: Colors.red),
        ),
        validator: (value) {
          if ((_quantityEnabled || _fieldsEnabled) &&
              (value == null || value.trim().isEmpty)) {
            return 'Quantity is required';
          }
          return null;
        },
      ),

      // MRP Field (Mandatory)
      TextFormField(
        controller: _mrpController,
        enabled: _fieldsEnabled,
        decoration: const InputDecoration(
          labelText: "MRP *",
          labelStyle: TextStyle(color: Colors.red),
          floatingLabelStyle: TextStyle(color: Colors.red),
        ),
        validator: (value) {
          if (_fieldsEnabled && (value == null || value.trim().isEmpty)) {
            return 'MRP is required';
          }
          return null;
        },
      ),
    ];
  }

  // New Generic form for non-book inventory
  List<Widget> _buildGenericForm() {
    return [
      TextFormField(
        controller: _mbisbn13Controller,
        decoration: const InputDecoration(labelText: "EAN / Code"),
      ),
      TextFormField(
        controller: _titleController,
        decoration: const InputDecoration(labelText: "Title"),
      ),
      TextFormField(
        controller: _authorController,
        decoration: const InputDecoration(labelText: "Brand"),
      ),
      TextFormField(
        controller: _categoryController,
        decoration: const InputDecoration(labelText: "Category"),
      ),
      TextFormField(
        controller: _weightController,
        decoration: const InputDecoration(labelText: "Weight"),
      ),
      TextFormField(
        controller: _descriptionController,
        decoration: const InputDecoration(labelText: "Description"),
      ),
      TextFormField(
        controller: _lastupdatedbyController,
        decoration: const InputDecoration(labelText: "Last Updated By"),
      ),

      DropdownButtonFormField<String>(
        initialValue: _selectedAgeCategory,
        decoration: const InputDecoration(
          labelText: "Age Category *",
          labelStyle: TextStyle(color: Colors.red),
          floatingLabelStyle: TextStyle(color: Colors.red),
        ),
        items: _ageCategoryOptions
            .map((c) => DropdownMenuItem(value: c, child: Text(c)))
            .toList(),
        onChanged: (val) => setState(() => _selectedAgeCategory = val),
        validator: (val) => val == null ? "Age Category is required" : null,
      ),
      TextFormField(
        controller: _quantityController,
        decoration: const InputDecoration(
          labelText: "Quantity *",
          labelStyle: TextStyle(color: Colors.red),
          floatingLabelStyle: TextStyle(color: Colors.red),
        ),
        validator: (val) =>
            val == null || val.trim().isEmpty ? "Quantity required" : null,
      ),
      TextFormField(
        controller: _mrpController,
        decoration: const InputDecoration(
          labelText: "MRP *",
          labelStyle: TextStyle(color: Colors.red),
          floatingLabelStyle: TextStyle(color: Colors.red),
        ),
        validator: (val) =>
            val == null || val.trim().isEmpty ? "MRP required" : null,
      ),
    ];
  }

  Future<void> _pickImage(int index) async {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext ctx) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: const Text('Camera'),
                onTap: () async {
                  final XFile? image = await _picker.pickImage(
                    source: ImageSource.camera,
                    maxWidth: 800,
                    maxHeight: 800,
                  );
                  if (image != null) {
                    setState(() {
                      _images[index] = image;
                    });
                  }
                  Navigator.pop(ctx);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library),
                title: const Text('Gallery'),
                onTap: () async {
                  final XFile? image = await _picker.pickImage(
                    source: ImageSource.gallery,
                    maxWidth: 800,
                    maxHeight: 800,
                  );
                  if (image != null) {
                    setState(() {
                      _images[index] = image;
                    });
                  }
                  Navigator.pop(ctx);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  //final ImagePicker _picker = ImagePicker();
  //List<XFile?> _images = List<XFile?>.filled(3, null);

  /*Future<void> _pickImage(int index) async {
    if (kIsWeb || Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
      // Desktop/Web → use camera plugin
      final cameras = await availableCameras();
      final CameraDescription camera = cameras.first;

      final CameraController controller = CameraController(
        camera,
        ResolutionPreset.medium,
      );

      await controller.initialize();
      final XFile image = await controller.takePicture();

      setState(() {
        _images[index] = image;
      });

      await controller.dispose();
    } else {
      // Mobile → use image_picker
      final XFile? image = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 800,
        maxHeight: 800,
      );

      if (image != null) {
        setState(() {
          _images[index] = image;
        });
      }
    }
  }*/
}
