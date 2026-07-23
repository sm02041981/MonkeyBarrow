import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('Login page smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.runAsync(() async {
      await tester.pumpWidget(const MyApp());
      await tester.pumpAndSettle();
    });

    // Verify that the login page is shown.
    expect(find.text('MonkeyBarrow'), findsOneWidget);
    expect(find.text('Mobile Number:'), findsOneWidget);
  });
}
