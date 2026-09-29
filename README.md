# FitBuddy — AI fitness plan generator

FitBuddy is a small, complete FastAPI application. It creates a personalized weekly workout plan and practical nutrition tips, supports feedback-based plan updates, and provides a local admin view of saved profiles. Plans use Gemini when an API key is configured; the app works without one using its built-in demo plan.

## Project files

```text
fitbuddy/
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── schemas.py
├── static/
│   └── styles.css
├── templates/
│   ├── all_users.html
│   ├── index.html
│   └── result.html
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Run in VS Code (Windows)

1. Open the `fitbuddy` folder in VS Code (`File → Open Folder`). Open the integrated terminal (`Terminal → New Terminal`).
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. You can also use Command Prompt and run `.venv\Scripts\activate.bat`.

3. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`. To use Gemini, set `GEMINI_API_KEY` to your Google AI Studio API key. Keep `.env` private and never commit it. If you leave the key blank, the app uses the built-in demo generator.
5. Start the development server:

   ```powershell
   uvicorn app.main:app --reload
   ```

6. Open **http://127.0.0.1:8000** in your browser. Stop the server with `Ctrl+C`.

## Use and check the application

- Fill out the profile form and select **Create my plan**. The generated plan page shows the workout schedule, nutrition tips, and a safety note.
- Enter a preference in the feedback box (for example, “make the sessions shorter” or “I have no equipment”) and select **Update my plan**.
- Open **http://127.0.0.1:8000/view-all-users** to see the profiles saved in the local SQLite database.
- Open **http://127.0.0.1:8000/health** to check that the server is responding. It reports whether Gemini or demo mode is active.
- FastAPI's interactive API documentation is at **http://127.0.0.1:8000/docs**.

Optional: set `ADMIN_TOKEN` in `.env`; then the admin page requires a matching query token, for example `/view-all-users?token=your-value`. Leave it blank for local development.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key; blank enables demo mode | blank |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `DATABASE_PATH` | SQLite file location | `fitbuddy.db` |
| `SECRET_KEY` | App secret reserved for future session features | development placeholder |
| `ADMIN_TOKEN` | Optional token protecting the local admin page | blank |

The plan is wellness guidance, not medical advice. FitBuddy does not diagnose conditions or prescribe diets. Avoid entering sensitive personal or medical information. For production deployment, use HTTPS, a strong secret, a protected admin account, and appropriate privacy and security controls.
