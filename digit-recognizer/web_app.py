"""Serve the handwritten digit drawing pad in a browser."""

from __future__ import annotations

import math
import json
import threading
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

import numpy as np

from digit_recognizer import DigitRecognizer, rasterize_pixels

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024
FEEDBACK_PATH = Path(__file__).with_name("user_corrections.json")
_recognizer: DigitRecognizer | None = None
_recognizer_lock = threading.RLock()


def get_recognizer() -> DigitRecognizer:
    global _recognizer
    with _recognizer_lock:
        if _recognizer is None:
            _recognizer = DigitRecognizer(load_feedback_examples())
        return _recognizer


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


def load_feedback_examples() -> list[tuple[np.ndarray, int]]:
    if not FEEDBACK_PATH.exists():
        return []
    try:
        records = json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(records, list):
        return []

    examples = []
    for record in records[-100:]:
        if not isinstance(record, dict):
            continue
        pixels = parse_pixels(record.get("pixels"))
        label = record.get("label")
        if pixels is None or isinstance(label, bool) or not isinstance(label, int) or not 0 <= label <= 9:
            continue
        image = rasterize_pixels(pixels)
        if image.any():
            examples.append((image, label))
    return examples


def save_feedback(pixels: np.ndarray, label: int) -> None:
    try:
        records = json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            records = []
    except (OSError, json.JSONDecodeError):
        records = []
    records = records[-99:]
    records.append({"pixels": pixels.astype(int).tolist(), "label": label})
    temporary_path = FEEDBACK_PATH.with_suffix(".tmp")
    temporary_path.write_text(json.dumps(records), encoding="utf-8")
    temporary_path.replace(FEEDBACK_PATH)


def explain_mistake(
    image: np.ndarray,
    prediction: int,
    confidence: float,
    correct_digit: int,
    recognizer: DigitRecognizer,
) -> str:
    probabilities = recognizer.predict_probabilities(image)
    correct_probability = float(probabilities[int(np.flatnonzero(recognizer.model.classes_ == correct_digit)[0])])
    active = image > 0.5
    rows, columns = np.where(active)
    height = int(rows.max() - rows.min() + 1) if len(rows) else 0
    width = int(columns.max() - columns.min() + 1) if len(columns) else 0
    shape = "tall" if height > width * 1.25 else "wide" if width > height * 1.25 else "compact"
    return (
        f"Before learning, it chose {prediction} ({confidence:.0%} confidence); "
        f"it gave your correct digit {correct_digit} a {correct_probability:.0%} score. "
        f"The normalized drawing was {shape} ({width} by {height} active pixels). "
        "These scores and shape are clues, not a certain explanation: handwriting style, "
        "stroke placement, or similarity between digits may have caused the confusion."
    )


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

    recognizer = get_recognizer()
    probabilities = recognizer.predict_probabilities(image)
    candidate_indices = np.argsort(probabilities)[::-1][:3]
    alternatives = [
        {
            "digit": int(recognizer.model.classes_[index]),
            "score": float(probabilities[index]),
        }
        for index in candidate_indices
    ]
    return jsonify(
        digit=alternatives[0]["digit"],
        confidence=alternatives[0]["score"],
        alternatives=alternatives,
    )


@app.post("/feedback")
def feedback():
    if not request.is_json:
        return jsonify(error="Send the drawing and correct digit as JSON."), 400
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Send the drawing and correct digit as JSON."), 400
    pixels = parse_pixels(payload.get("pixels"))
    label = payload.get("label")
    if pixels is None:
        return jsonify(error="The drawing must be a 28 by 28 pixel grid."), 400
    if isinstance(label, bool) or not isinstance(label, int) or not 0 <= label <= 9:
        return jsonify(error="Enter the correct digit from 0 to 9."), 400
    image = rasterize_pixels(pixels)
    if not image.any():
        return jsonify(error="Draw a digit before sending a correction."), 400

    global _recognizer
    with _recognizer_lock:
        recognizer = get_recognizer()
        prediction, confidence = recognizer.predict(image)
        analysis = explain_mistake(image, prediction, confidence, label, recognizer)
        save_feedback(pixels, label)
        examples = load_feedback_examples()
        _recognizer = DigitRecognizer(examples)

    return jsonify(
        message=f"Correction saved. The model has been retrained using {len(examples)} corrected drawing(s).",
        analysis=analysis,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
