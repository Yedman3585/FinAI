# FInAI Android

Native Android application for the FinAI personal finance and market intelligence product.

Current surfaces:

- Home dashboard with Personal / MOLOX Pro modes.
- Notes feed for market events, saved items, impact tags, and Molly explanations.
- Market workspace with watchlist, scenarios, editable thesis, and live MOLOX analysis.
- Learn path generated from the user's recent money and market activity.
- Profile, money limits, priority alerts, API connection, and paper-portfolio status.
- Movable Molly assistant available over every screen.
- Home-screen widget with safe-to-try amount and market note.
- Demo fallback state aligned with the web/API scenario.
- Live `POST /api/mobile/session` client for the FastAPI backend.
- Editable API URL in Profile for emulator or physical phone testing.
- Internet permission and cleartext local HTTP are configured for hackathon development.

Development:

1. Open `apps/android` in Android Studio.
2. Select JDK 17 under Settings > Build, Execution, Deployment > Build Tools > Gradle.
3. Let Gradle sync the project.
4. Run the `app` configuration on a phone or emulator.

On the current Mac, JDK 17 is installed at:

```text
/Users/yedige.mussabayev/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
```

The project includes a Gradle 8.9 wrapper and has been compiled into a debug APK:

```bash
cd apps/android
./gradlew assembleDebug
```

APK output:

```text
apps/android/app/build/outputs/apk/debug/app-debug.apk
```

The app opens with a complete demo state and updates market, scenarios, agents, radar, portfolio, and the action state when `Run MOLOX analysis` is pressed.

Local API targets:

- Android emulator: `http://10.0.2.2:8000`
- Physical phone on the same Wi-Fi: `http://<your-mac-lan-ip>:8000`

For a physical phone, start the API so it listens on your Mac's network interface:

```bash
HOST=0.0.0.0 ./scripts/dev-api.sh
```

Then put your Mac's Wi-Fi IP into the app's `API URL` field.

Do not connect live broker order placement from Android until authentication, encrypted secret storage, and explicit confirmation screens are implemented.
