"""Draw a digit and recognize it with a small scikit-learn classifier."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import numpy as np
from scipy.ndimage import affine_transform, center_of_mass, map_coordinates, shift
from sklearn.calibration import CalibratedClassifierCV
from sklearn.datasets import load_digits
from sklearn.svm import SVC

CANVAS_SIZE = 280
IMAGE_SIZE = 8
BRUSH_WIDTH = 20

_DRAWING_EXAMPLES = np.array(
    [
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 7, 9, 9, 2, 0, 0],
            [0, 5, 4, 2, 7, 6, 0, 0],
            [0, 0, 0, 4, 11, 5, 0, 0],
            [0, 0, 1, 3, 10, 6, 0, 0],
            [0, 0, 6, 1, 2, 12, 1, 0],
            [0, 0, 9, 6, 6, 8, 0, 0],
            [0, 0, 1, 6, 6, 1, 0, 0],
        ],
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 4, 11, 13, 3, 0, 0],
            [0, 0, 6, 13, 13, 5, 1, 0],
            [0, 0, 3, 6, 7, 9, 5, 1],
            [0, 0, 0, 1, 1, 9, 7, 1],
            [0, 6, 2, 1, 4, 11, 5, 1],
            [0, 7, 8, 9, 9, 6, 1, 0],
            [0, 2, 4, 5, 4, 1, 0, 0],
        ],
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 7, 6, 5, 3, 0],
            [0, 0, 7, 6, 2, 0, 1, 0],
            [0, 0, 11, 9, 4, 1, 0, 0],
            [0, 0, 12, 7, 6, 3, 1, 0],
            [0, 0, 11, 4, 3, 5, 2, 0],
            [0, 0, 4, 8, 9, 4, 1, 0],
            [0, 0, 0, 4, 5, 1, 0, 0],
        ],
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 8, 7, 6, 9, 6, 1],
            [0, 8, 7, 3, 1, 5, 5, 2],
            [0, 8, 6, 7, 8, 6, 3, 1],
            [0, 8, 11, 9, 8, 9, 6, 1],
            [0, 5, 11, 7, 2, 7, 8, 2],
            [0, 1, 5, 8, 8, 9, 6, 1],
            [0, 0, 0, 3, 6, 6, 2, 0],
        ],
        [
            [0, 1, 2, 3, 4, 5, 4, 2],
            [0, 2, 5, 6, 7, 10, 8, 2],
            [0, 1, 3, 4, 7, 9, 5, 1],
            [0, 0, 2, 6, 8, 4, 1, 0],
            [0, 4, 7, 7, 4, 1, 0, 0],
            [0, 7, 6, 3, 0, 0, 0, 0],
            [0, 4, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 10, 11, 11, 11, 9, 0],
            [0, 0, 13, 3, 2, 1, 0, 0],
            [0, 0, 13, 12, 12, 7, 0, 0],
            [0, 0, 1, 0, 0, 12, 1, 0],
            [0, 5, 1, 0, 0, 12, 1, 0],
            [0, 11, 3, 2, 4, 10, 1, 0],
            [0, 0, 9, 11, 6, 0, 0, 0],
        ],
    ],
    dtype=np.float64,
)
_DRAWING_LABELS = np.array([3, 3, 6, 6, 7, 5])

_DRAWING_VARIATIONS = (
    (-10, 1.0, 1.0, 0.0, 0.0),
    (-5, 1.0, 1.0, 0.0, 0.0),
    (5, 1.0, 1.0, 0.0, 0.0),
    (10, 1.0, 1.0, 0.0, 0.0),
    (0, 0.9, 1.0, 0.0, 0.0),
    (0, 1.1, 1.0, 0.0, 0.0),
    (0, 1.0, 0.9, 0.0, 0.0),
    (0, 1.0, 1.1, 0.0, 0.0),
    (0, 1.0, 1.0, 0.0, -0.35),
    (0, 1.0, 1.0, 0.0, 0.35),
    (0, 1.0, 1.0, -0.35, 0.0),
    (0, 1.0, 1.0, 0.35, 0.0),
)


def augment_drawing_examples() -> tuple[np.ndarray, np.ndarray]:
    """Create small tilt, size, and position variants of the labeled drawings."""
    images: list[np.ndarray] = []
    labels: list[int] = []
    center = np.array([3.5, 3.5])
    for image, label in zip(_DRAWING_EXAMPLES, _DRAWING_LABELS):
        for angle, scale_x, scale_y, offset_y, offset_x in _DRAWING_VARIATIONS:
            radians = np.deg2rad(angle)
            matrix = np.array(
                [
                    [np.cos(radians) / scale_y, -np.sin(radians) / scale_x],
                    [np.sin(radians) / scale_y, np.cos(radians) / scale_x],
                ]
            )
            transformed = affine_transform(
                image,
                matrix,
                offset=center - matrix @ center,
                order=1,
                mode="constant",
                cval=0,
            )
            transformed = shift(
                transformed,
                (offset_y, offset_x),
                order=1,
                mode="constant",
                cval=0,
            )
            images.append(transformed)
            labels.append(int(label))
    return np.asarray(images), np.asarray(labels)


def augment_nine_examples(
    images: np.ndarray,
    labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Create slightly rotated training variants to make nines less angle-sensitive."""
    nine_images = images[labels == 9]
    augmented_images = []
    for image in nine_images:
        for angle in (-10, -5, 5, 10):
            radians = np.deg2rad(angle)
            matrix = np.array(
                [
                    [np.cos(radians), -np.sin(radians)],
                    [np.sin(radians), np.cos(radians)],
                ]
            )
            center = np.array([3.5, 3.5])
            augmented_images.append(
                affine_transform(
                    image,
                    matrix,
                    offset=center - matrix @ center,
                    order=1,
                    mode="constant",
                    cval=0,
                )
            )
    return np.asarray(augmented_images), np.full(len(augmented_images), 9)


def rasterize_pixels(pixels: np.ndarray) -> np.ndarray:
    """Crop, scale, and center a grayscale drawing to match the training images."""
    if pixels.ndim != 2 or not np.isfinite(pixels).all():
        raise ValueError("Drawing pixels must be a finite grayscale image.")
    if np.any((pixels < 0) | (pixels > 255)):
        raise ValueError("Drawing pixel values must be between 0 and 255.")

    foreground = pixels > 8
    if not np.any(foreground):
        return np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float64)

    rows, columns = np.where(foreground)
    cropped = pixels[rows.min() : rows.max() + 1, columns.min() : columns.max() + 1]
    height, width = cropped.shape
    scale = 7.0 / max(height, width)
    resized_height = max(1, round(height * scale))
    resized_width = max(1, round(width * scale))
    y_coordinates = (np.arange(resized_height) + 0.5) * height / resized_height - 0.5
    x_coordinates = (np.arange(resized_width) + 0.5) * width / resized_width - 0.5
    sample_y, sample_x = np.meshgrid(y_coordinates, x_coordinates, indexing="ij")
    resized = map_coordinates(
        cropped,
        [sample_y, sample_x],
        order=1,
        mode="nearest",
    )

    image = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float64)
    top = (IMAGE_SIZE - resized_height) // 2
    left = (IMAGE_SIZE - resized_width) // 2
    image[top : top + resized_height, left : left + resized_width] = resized * (16 / 255)
    center_y, center_x = center_of_mass(image)
    return shift(
        image,
        (3.5 - center_y, 3.5 - center_x),
        order=1,
        mode="constant",
        cval=0,
    )


def augment_browser_examples(
    images: np.ndarray,
    labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Prepare training images using the same crop and scaling as browser drawings."""
    canvas_pixels = np.pad(
        np.repeat(np.repeat(images, 3, axis=1), 3, axis=2),
        ((0, 0), (2, 2), (2, 2)),
    ) * (255 / 16)
    prepared_images = np.asarray([rasterize_pixels(image) for image in canvas_pixels])
    return prepared_images, labels.copy()


def rasterize_strokes(
    strokes: list[list[tuple[float, float]]],
) -> np.ndarray:
    """Render mouse strokes at pad resolution before preparing a digit image."""
    points = [point for stroke in strokes for point in stroke]
    pixels = np.zeros((IMAGE_SIZE * 4, IMAGE_SIZE * 4), dtype=np.float64)
    if not points:
        return np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float64)

    pixel_scale = (IMAGE_SIZE * 4) / CANVAS_SIZE
    radius = (BRUSH_WIDTH / 2) * pixel_scale
    pixel_y, pixel_x = np.mgrid[0 : IMAGE_SIZE * 4, 0 : IMAGE_SIZE * 4]
    pixel_x = pixel_x + 0.5
    pixel_y = pixel_y + 0.5
    for stroke in strokes:
        mapped_stroke = [(x * pixel_scale, y * pixel_scale) for x, y in stroke]
        segments = list(zip(mapped_stroke, mapped_stroke[1:])) or [
            (mapped_stroke[0], mapped_stroke[0])
        ]
        for (x1, y1), (x2, y2) in segments:
            dx = x2 - x1
            dy = y2 - y1
            length_squared = dx * dx + dy * dy
            if length_squared:
                projection = np.clip(
                    ((pixel_x - x1) * dx + (pixel_y - y1) * dy) / length_squared,
                    0,
                    1,
                )
            else:
                projection = 0
            distance = np.hypot(
                pixel_x - (x1 + projection * dx),
                pixel_y - (y1 + projection * dy),
            )
            coverage = np.clip(radius + 0.5 - distance, 0, 1)
            pixels = np.maximum(pixels, coverage * 255)

    return rasterize_pixels(pixels)


class DigitRecognizer:
    def __init__(self) -> None:
        digits = load_digits()
        augmented_images, augmented_labels = augment_drawing_examples()
        augmented_nines, augmented_nine_labels = augment_nine_examples(
            digits.images,
            digits.target,
        )
        browser_images, browser_labels = augment_browser_examples(
            digits.images,
            digits.target,
        )
        browser_nine_variations, browser_nine_labels = augment_browser_examples(
            augmented_nines,
            augmented_nine_labels,
        )
        training_images = np.vstack(
            (
                digits.data,
                _DRAWING_EXAMPLES.reshape(len(_DRAWING_LABELS), -1),
                augmented_images.reshape(len(augmented_labels), -1),
                augmented_nines.reshape(len(augmented_nine_labels), -1),
                browser_images.reshape(len(browser_labels), -1),
                browser_nine_variations.reshape(len(browser_nine_labels), -1),
            )
        )
        training_labels = np.concatenate(
            (
                digits.target,
                _DRAWING_LABELS,
                augmented_labels,
                augmented_nine_labels,
                browser_labels,
                browser_nine_labels,
            )
        )
        self.model = CalibratedClassifierCV(
            SVC(C=10, gamma="scale", random_state=42),
            cv=5,
            ensemble=False,
        )
        self.model.fit(training_images, training_labels)

    def predict(self, image: np.ndarray) -> tuple[int, float]:
        probabilities = self.model.predict_proba(image.reshape(1, -1))[0]
        best_index = int(np.argmax(probabilities))
        return int(self.model.classes_[best_index]), float(probabilities[best_index])


class DigitPad:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Handwritten Digit Recognizer")
        self.root.resizable(False, False)
        self.recognizer = DigitRecognizer()
        self.strokes: list[list[tuple[float, float]]] = []
        self.current_stroke: list[tuple[float, float]] | None = None

        frame = ttk.Frame(root, padding=20)
        frame.grid()

        ttk.Label(
            frame,
            text="Draw a digit from 0 to 9",
            font=("TkDefaultFont", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 8))
        ttk.Label(
            frame,
            text="Use the mouse on the black drawing pad, then select Recognize.",
        ).grid(row=1, column=0, columnspan=2, pady=(0, 14))

        self.canvas = tk.Canvas(
            frame,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            background="black",
            highlightthickness=1,
            highlightbackground="#888888",
            cursor="crosshair",
        )
        self.canvas.grid(row=2, column=0, columnspan=2)
        self.canvas.bind("<Button-1>", self._start_stroke)
        self.canvas.bind("<B1-Motion>", self._continue_stroke)

        ttk.Button(frame, text="Recognize", command=self._recognize).grid(
            row=3, column=0, sticky="ew", pady=(14, 0), padx=(0, 5)
        )
        ttk.Button(frame, text="Clear", command=self._clear).grid(
            row=3, column=1, sticky="ew", pady=(14, 0), padx=(5, 0)
        )
        self.result = ttk.Label(frame, text="Your prediction will appear here.")
        self.result.grid(row=4, column=0, columnspan=2, pady=(14, 0))

    def _start_stroke(self, event: tk.Event) -> None:
        point = (float(event.x), float(event.y))
        self.current_stroke = [point]
        self.strokes.append(self.current_stroke)
        radius = BRUSH_WIDTH / 2
        self.canvas.create_oval(
            event.x - radius,
            event.y - radius,
            event.x + radius,
            event.y + radius,
            fill="white",
            outline="white",
        )

    def _continue_stroke(self, event: tk.Event) -> None:
        if self.current_stroke is None:
            return
        previous = self.current_stroke[-1]
        current = (float(event.x), float(event.y))
        self.current_stroke.append(current)
        self.canvas.create_line(
            *previous,
            *current,
            fill="white",
            width=BRUSH_WIDTH,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
        )

    def _recognize(self) -> None:
        image = rasterize_strokes(self.strokes)
        if not np.any(image):
            self.result.configure(text="Draw a digit on the pad first.")
            return
        digit, confidence = self.recognizer.predict(image)
        self.result.configure(
            text=f"Prediction: {digit}  ·  Confidence: {confidence:.0%}"
        )

    def _clear(self) -> None:
        self.canvas.delete("all")
        self.strokes.clear()
        self.current_stroke = None
        self.result.configure(text="Your prediction will appear here.")


def main() -> None:
    root = tk.Tk()
    DigitPad(root)
    root.mainloop()


if __name__ == "__main__":
    main()
