# FInAI Demo Script

## 60 Second Product Story

1. Open the mobile-first app.
2. Show the user's monthly income, expenses, free cash, and safe-to-try amount.
3. Keep `CIS demo` and `KSPI` selected, amount `100`.
4. Click `Пересчитать`.
5. Explain that FInAI converts the position into the user's budget currency and checks whether this is safe relative to everyday life.
6. Show the scenario list: stress, bad, soft loss, base gain, good, strong.
7. Open `Агенты` and show the deep-analysis memo, risk desk, teacher note, and thesis review.
8. Click `Paper-position`.
9. Open `Монитор` and show that the position appears in `Paper portfolio`.
10. Switch provider to `MOEX ISS`, choose `SBER`, and run analysis to show live regional exchange data.

## One Line Pitch

FInAI turns scattered personal-finance data and market data into safe, explainable investment experiments.

## Judge-Friendly Proof Points

- Real API, not only screens.
- Live NBK FX rate for KZT conversion.
- Live MOEX ISS adapter for regional market data.
- SQLite persistence for paper positions.
- Mobile-first PWA and Android companion prototype.
- No live order execution in MVP; user safety stays explicit.

## Demo Commands

```bash
./scripts/dev-api.sh
./scripts/dev-web.sh
```

Then open:

```text
http://127.0.0.1:5173
```

## Native Android Demo

For an emulator:

1. Start the API with `./scripts/dev-api.sh`.
2. Open `apps/android` in Android Studio.
3. Run the `app` configuration.
4. Keep `API URL` as `http://10.0.2.2:8000`.
5. Tap `Анализ`.

For a physical phone on the same Wi-Fi:

1. Start the API with `HOST=0.0.0.0 ./scripts/dev-api.sh`.
2. Put `http://<your-mac-lan-ip>:8000` into the Android app's `API URL`.
3. Tap `Анализ`.
4. Open `Агенты` to show review, risk desk, teacher note, and opportunity radar.
