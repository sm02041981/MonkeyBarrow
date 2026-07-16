import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart' show TargetPlatform, defaultTargetPlatform;

class Config {
  static String get apiUrl {
    if (kReleaseMode) {
      return 'https://your-production-api-url.com';
    }
    
    // Development configuration based on platform
    if (kIsWeb) {
      // Web platform
      return 'http://127.0.0.1:8000';
    } else if (defaultTargetPlatform == TargetPlatform.android) {
      // Android emulator uses 10.0.2.2 instead of 127.0.0.1
      return 'http://10.0.2.2:8000';
    } else {
      // iOS and other platforms
      return 'http://127.0.0.1:8000';
    }
  }
}
