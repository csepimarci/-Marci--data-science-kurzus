import unittest
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from digit_recognizer import _DRAWING_EXAMPLES
import web_app
from web_app import app


class WebAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()
        self.original_recognizer = web_app._recognizer

    def tearDown(self) -> None:
        web_app._recognizer = self.original_recognizer

    def test_drawing_page_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Draw a number", response.data)
        self.assertIn(b"Model input preview", response.data)
        self.assertIn("no-store", response.headers["Cache-Control"])
        response.close()

    def test_recognition_rejects_empty_drawing(self) -> None:
        response = self.client.post("/recognize", json={"pixels": [[0] * 28 for _ in range(28)]})

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_recognition_rejects_invalid_pixel_grid(self) -> None:
        response = self.client.post(
            "/recognize",
            json={"pixels": [[0] * 27 for _ in range(28)]},
        )

        self.assertEqual(response.status_code, 400)

    def test_recognize_returns_digit_and_confidence(self) -> None:
        pixels = [[0] * 28 for _ in range(28)]
        for row in pixels[3:25]:
            row[13:15] = [255, 255]
        response = self.client.post(
            "/recognize",
            json={"pixels": pixels},
        )

        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertIn(result["digit"], range(10))
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 1)
        self.assertEqual(len(result["alternatives"]), 3)
        self.assertEqual(result["alternatives"][0]["digit"], result["digit"])
        self.assertGreaterEqual(
            result["alternatives"][0]["score"],
            result["alternatives"][1]["score"],
        )

    def test_recognize_returns_seven_for_the_browser_style_example(self) -> None:
        pixels = np.pad(
            np.repeat(np.repeat(_DRAWING_EXAMPLES[-1], 3, axis=0), 3, axis=1),
            2,
        )
        response = self.client.post(
            "/recognize",
            json={"pixels": pixels.tolist()},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["digit"], 7)

    def test_feedback_rejects_a_digit_outside_zero_to_nine(self) -> None:
        pixels = [[0] * 28 for _ in range(28)]
        pixels[10][10] = 255
        response = self.client.post("/feedback", json={"pixels": pixels, "label": 10})

        self.assertEqual(response.status_code, 400)
        self.assertIn("correct digit", response.get_json()["error"])

    def test_feedback_saves_the_digit_and_retrains_with_it(self) -> None:
        pixels = [[0] * 28 for _ in range(28)]
        for row in range(4, 24):
            pixels[row][13:15] = [255, 255]
        created_examples = []

        class FakeRecognizer:
            def __init__(self, feedback_examples=None):
                created_examples.append(feedback_examples)
                self.model = SimpleNamespace(classes_=np.arange(10))

            def predict(self, _image):
                return 3, 0.6

            def predict_probabilities(self, _image):
                return np.array([0.02, 0.02, 0.05, 0.6, 0.1, 0.05, 0.04, 0.04, 0.04, 0.04])

        with tempfile.TemporaryDirectory() as directory:
            feedback_path = Path(directory) / "corrections.json"
            web_app._recognizer = FakeRecognizer()
            with patch.object(web_app, "FEEDBACK_PATH", feedback_path), patch.object(
                web_app, "DigitRecognizer", FakeRecognizer
            ):
                response = self.client.post(
                    "/feedback",
                    json={"pixels": pixels, "label": 8},
                )

            self.assertEqual(response.status_code, 200)
            result = response.get_json()
            self.assertIn("retrained", result["message"])
            self.assertIn("may have caused the confusion", result["analysis"])
            saved = json.loads(feedback_path.read_text(encoding="utf-8"))
            self.assertEqual(saved[0]["label"], 8)
            self.assertEqual(saved[0]["pixels"], pixels)
            self.assertEqual(len(created_examples[-1]), 1)
            self.assertEqual(created_examples[-1][0][1], 8)


if __name__ == "__main__":
    unittest.main()
