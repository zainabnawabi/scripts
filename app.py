import csv
import hmac
import io
import json
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request
from waitress import serve


TRAITS = (
    "Curiosity",
    "Planning",
    "Social energy",
    "Understanding others",
    "Handling stress",
)

QUESTION_SCORING = (
    ("Curiosity", False),
    ("Planning", False),
    ("Social energy", False),
    ("Understanding others", False),
    ("Handling stress", False),
    ("Curiosity", True),
    ("Planning", True),
    ("Social energy", True),
    ("Understanding others", True),
    ("Handling stress", True),
    ("Curiosity", False),
    ("Planning", False),
    ("Social energy", False),
    ("Understanding others", False),
    ("Handling stress", False),
    ("Curiosity", True),
    ("Planning", True),
    ("Social energy", True),
    ("Understanding others", True),
    ("Handling stress", True),
    ("Curiosity", False),
    ("Planning", False),
    ("Social energy", False),
    ("Understanding others", False),
    ("Handling stress", False),
)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get("RESPONSES_DB", "responses.sqlite3"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD"),
        MAX_CONTENT_LENGTH=4096,
    )
    if test_config:
        app.config.update(test_config)

    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS responses (
                    id TEXT PRIMARY KEY,
                    submitted_at_utc TEXT NOT NULL,
                    answers_json TEXT NOT NULL,
                    scores_json TEXT NOT NULL
                )
                """
            )

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/responses")
    def submit_response():
        if not app.config["ADMIN_PASSWORD"]:
            return jsonify(error="Response collection is not set up yet."), 503

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="The answers were incomplete or invalid."), 400

        answers = payload.get("answers")
        if (
            not isinstance(answers, list)
            or len(answers) != len(QUESTION_SCORING)
            or any(type(answer) is not int or not 1 <= answer <= 5 for answer in answers)
        ):
            return jsonify(error="The answers were incomplete or invalid."), 400

        totals = {trait: [0, 0] for trait in TRAITS}
        for answer, (trait, reverse) in zip(answers, QUESTION_SCORING):
            score = 6 - answer if reverse else answer
            totals[trait][0] += score
            totals[trait][1] += 1
        scores = {
            trait: round(((total / count - 1) / 4) * 100)
            for trait, (total, count) in totals.items()
        }

        response_id = str(uuid.uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with closing(sqlite3.connect(database_path, timeout=10)) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO responses (id, submitted_at_utc, answers_json, scores_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        response_id,
                        submitted_at,
                        json.dumps(answers),
                        json.dumps(scores),
                    ),
                )

        return jsonify(message="Your answers have been saved."), 201

    @app.get("/admin/responses.csv")
    def download_responses():
        password = app.config["ADMIN_PASSWORD"]
        if not password:
            return jsonify(error="Response collection is not set up yet."), 503

        authorization = request.authorization
        supplied_password = authorization.password if authorization else ""
        if (
            not authorization
            or authorization.type.lower() != "basic"
            or authorization.username != "admin"
            or not hmac.compare_digest(supplied_password, password)
        ):
            return Response(
                "Admin password required.",
                status=401,
                headers={"WWW-Authenticate": 'Basic realm="Response export"'},
                content_type="text/plain; charset=utf-8",
            )

        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            ["response_id", "submitted_at_utc"]
            + [f"answer_{index:02d}" for index in range(1, len(QUESTION_SCORING) + 1)]
            + list(TRAITS)
        )
        with closing(sqlite3.connect(database_path)) as connection:
            rows = connection.execute(
                """
                SELECT id, submitted_at_utc, answers_json, scores_json
                FROM responses
                ORDER BY submitted_at_utc
                """
            )
            for response_id, submitted_at, answers_json, scores_json in rows:
                answers = json.loads(answers_json)
                scores = json.loads(scores_json)
                writer.writerow(
                    [response_id, submitted_at]
                    + answers
                    + [scores[trait] for trait in TRAITS]
                )

        return Response(
            "\ufeff" + output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="responses.csv"',
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify(error="The request was too large."), error.code

    return app


app = create_app()


if __name__ == "__main__":
    if not app.config["ADMIN_PASSWORD"]:
        raise SystemExit("Set the ADMIN_PASSWORD environment variable before starting the server.")
    serve(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8080")),
    )
