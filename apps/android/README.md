# FInAI Android

Native Android prototype for the FInAI companion app.

Current surfaces:

- Main mobile app screen with Idea, Agents, and Monitor tabs.
- Home-screen widget with safe-to-try amount and market note.
- Demo fallback state aligned with the web/API scenario.
- Live `POST /api/mobile/session` client for the FastAPI backend.
- Editable API URL field for emulator or physical phone testing.
- Internet permission and cleartext local HTTP are configured for hackathon development.

Development:

1. Open `apps/android` in Android Studio.
2. Let Gradle sync the project.
3. Run the `app` configuration on a phone or emulator.

This machine does not currently expose Android Studio, Android SDK, or a Gradle wrapper in the project, so the APK build step starts after Android Studio syncs or after a Gradle wrapper is generated.

The app opens with demo data and updates from the backend when the `Анализ` button is pressed.

Local API targets:

- Android emulator: `http://10.0.2.2:8000`
- Physical phone on the same Wi-Fi: `http://<your-mac-lan-ip>:8000`

For a physical phone, start the API so it listens on your Mac's network interface:

```bash
HOST=0.0.0.0 ./scripts/dev-api.sh
```

Then put your Mac's Wi-Fi IP into the app's `API URL` field.

Do not connect live broker order placement from Android until authentication, encrypted secret storage, and explicit confirmation screens are implemented.
