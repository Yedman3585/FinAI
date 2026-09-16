# VS Code Setup

Open the project root:

```bash
code /Users/yedige.mussabayev/Documents/FInAI
```

Recommended workspaces:

- `apps/api` for backend work
- `apps/web` for web UI
- `apps/android` for Android app and widget
- `docs` for product and architecture notes

## First Local Run

API:

```bash
./scripts/dev-api.sh
```

Web:

```bash
./scripts/dev-web.sh
```

If your shell does not have Node.js, use the bundled runtime through the VS Code task `Web: run with bundled Node`.

Android:

Open `apps/android` in Android Studio, sync Gradle, and run on the phone.
