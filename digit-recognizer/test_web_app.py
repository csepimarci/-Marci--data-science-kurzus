import unittest

import numpy as np

from digit_recognizer import _DRAWING_EXAMPLES
from web_app import app


class WebAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def test_drawing_page_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Draw a number", response.data)
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


if __name__ == "__main__":
    unittest.main()
