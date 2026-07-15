import 'package:flutter/foundation.dart';

class Config {
  // Use 10.0.2.2 for Android emulator, 127.0.0.1 for iOS simulator/Web.
  // In a real deployed app, this should be the actual API URL.
  static const String apiUrl = kReleaseMode
      ? 'https://your-production-api-url.com'
      : 'http://127.0.0.1:8000';
}
