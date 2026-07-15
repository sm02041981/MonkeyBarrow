import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('Login page smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());

    // Verify that the login page is shown.
    expect(find.text('Monkey\nBarrow'), findsOneWidget);
    expect(find.text('Mobile Number:'), findsOneWidget);
    expect(find.text('Generate OTP'), findsOneWidget);
  });
}
