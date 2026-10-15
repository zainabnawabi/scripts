# Personal reflection quiz

## Run locally

Install the packages and set a private password for downloading responses:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:ADMIN_PASSWORD = "use-a-long-private-password"
& .\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:8080`. The first page explains that answers and scores are saved automatically when a visitor finishes. Make sure your research consent process is completed before participants use the quiz.

## Download responses

Open `http://127.0.0.1:8080/admin/responses.csv` in a browser and sign in with username `admin` and the `ADMIN_PASSWORD` you set. The CSV opens in Excel. It contains a random response ID, the submission time, the 25 answers, and the five calculated scores. The app does not ask for a name or email.

Responses are stored in a local SQLite database named `responses.sqlite3`. Keep this file private and back it up if needed. Do not commit or publicly expose it.

## Hosting online

Deploy this app on a Python host that provides HTTPS. Set `ADMIN_PASSWORD` in the host's private environment settings, set `HOST` to `0.0.0.0`, and set `PORT` to the port provided by the host. Set `RESPONSES_DB` to a path on persistent private storage; otherwise the host may erase responses when it restarts or redeploys. Use HTTPS for saving responses and downloading the CSV.
