"""Serve the handwritten digit drawing pad in a browser."""

from __future__ import annotations

import math
from functools import lru_cache

from flask import Flask, jsonify, request, send_from_directory

import numpy as np

from digit_recognizer import DigitRecognizer, rasterize_pixels

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


@lru_cache(maxsize=1)
def get_recognizer() -> DigitRecognizer:
    return DigitRecognizer()


def parse_pixels(value: object) -> np.ndarray | None:
    if not isinstance(value, list) or len(value) != 28:
        return None

    pixels: list[list[float]] = []
    for row in value:
        if not isinstance(row, list) or len(row) != 28:
            return None
        if any(
            isinstance(pixel, bool)
            or not isinstance(pixel, (int, float))
            or not math.isfinite(pixel)
            or pixel < 0
            or pixel > 255
            for pixel in row
        ):
            return None
        pixels.append([float(pixel) for pixel in row])
    return np.array(pixels, dtype=np.float64)


@app.get("/")
def drawing_page():
    response = send_from_directory(app.root_path, "index.html", max_age=0)
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.post("/recognize")
def recognize():
    if not request.is_json:
        return jsonify(error="Send drawing pixels as JSON."), 400
    payload = request.get_json(silent=True)
    pixels = parse_pixels(payload.get("pixels") if isinstance(payload, dict) else None)
    if pixels is None:
        return jsonify(error="Draw a digit before asking for a prediction."), 400

    image = rasterize_pixels(pixels)
    if not image.any():
        return jsonify(error="Draw a digit before asking for a prediction."), 400

    digit, confidence = get_recognizer().predict(image)
    return jsonify(digit=digit, confidence=confidence)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
