import base64
import csv
import io
import tempfile
import unittest
from pathlib import Path

from app import QUESTION_SCORING, create_app


class ResponseAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = Path(self.temp_dir.name) / "test.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(database),
                "ADMIN_PASSWORD": "test-password",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_response_is_saved_without_an_in_game_consent_field(self):
        response = self.client.post(
            "/api/responses",
            json={"answers": [3] * len(QUESTION_SCORING)},
        )
        self.assertEqual(response.status_code, 201)
        credentials = base64.b64encode(b"admin:test-password").decode("ascii")
        export = self.client.get(
            "/admin/responses.csv",
            headers={"Authorization": f"Basic {credentials}"},
        )
        rows = list(csv.reader(io.StringIO(export.get_data(as_text=True).lstrip("\ufeff"))))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][2:27], ["3"] * len(QUESTION_SCORING))

    def test_response_is_saved_and_csv_can_be_downloaded(self):
        answers = [3] * len(QUESTION_SCORING)
        response = self.client.post(
            "/api/responses",
            json={"answers": answers},
        )
        self.assertEqual(response.status_code, 201)

        unauthorized = self.client.get("/admin/responses.csv")
        self.assertEqual(unauthorized.status_code, 401)

        credentials = base64.b64encode(b"admin:test-password").decode("ascii")
        export = self.client.get(
            "/admin/responses.csv",
            headers={"Authorization": f"Basic {credentials}"},
        )
        self.assertEqual(export.status_code, 200)
        self.assertIn("text/csv", export.content_type)
        rows = list(csv.reader(io.StringIO(export.get_data(as_text=True).lstrip("\ufeff"))))
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(rows[0]), 2 + len(answers) + 5)
        self.assertEqual(rows[1][2:27], [str(answer) for answer in answers])
        self.assertEqual(rows[1][27:], ["50"] * 5)

    def test_export_contains_server_calculated_scores(self):
        self.client.post(
            "/api/responses",
            json={"answers": [1] * len(QUESTION_SCORING)},
        )
        credentials = base64.b64encode(b"admin:test-password").decode("ascii")
        export = self.client.get(
            "/admin/responses.csv",
            headers={"Authorization": f"Basic {credentials}"},
        )
        rows = list(csv.reader(io.StringIO(export.get_data(as_text=True).lstrip("\ufeff"))))
        self.assertEqual(rows[1][27:], ["40"] * 5)

    def test_response_rejects_wrong_length_and_boolean_answers(self):
        for answers in ([3] * 24, [True] + [3] * 24):
            with self.subTest(answers=answers[:2]):
                response = self.client.post(
                    "/api/responses",
                    json={"answers": answers},
                )
                self.assertEqual(response.status_code, 400)

    def test_collection_is_disabled_without_admin_password(self):
        app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(Path(self.temp_dir.name) / "disabled.sqlite3"),
                "ADMIN_PASSWORD": None,
            }
        )
        response = app.test_client().post(
            "/api/responses",
            json={"answers": [3] * len(QUESTION_SCORING)},
        )
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
