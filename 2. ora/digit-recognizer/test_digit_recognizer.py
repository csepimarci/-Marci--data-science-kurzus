import unittest

import numpy as np

from digit_recognizer import (
    _DRAWING_EXAMPLES,
    _DRAWING_LABELS,
    DigitRecognizer,
    augment_browser_examples,
    augment_drawing_examples,
    augment_nine_examples,
    rasterize_pixels,
    rasterize_strokes,
)
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


class RasterizeStrokesTests(unittest.TestCase):
    def test_empty_strokes_produce_blank_image(self) -> None:
        image = rasterize_strokes([])

        self.assertEqual(image.shape, (8, 8))
        self.assertFalse(np.any(image))

    def test_single_point_produces_visible_centered_image(self) -> None:
        image = rasterize_strokes([[(140, 140)]])

        self.assertGreater(float(image.max()), 0)
        self.assertEqual(np.unravel_index(image.argmax(), image.shape), (3, 3))

    def test_pixel_normalization_is_independent_of_canvas_size(self) -> None:
        small = np.zeros((28, 28))
        small[5:15, 8:14] = 255
        large = np.zeros((28, 28))
        large[3:23, 5:17] = 255

        np.testing.assert_allclose(rasterize_pixels(small), rasterize_pixels(large))

    def test_empty_pixel_grid_produces_blank_image(self) -> None:
        image = rasterize_pixels(np.zeros((28, 28)))

        self.assertEqual(image.shape, (8, 8))
        self.assertFalse(np.any(image))

    def test_pixel_normalization_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            rasterize_pixels(np.full((28, 28), np.nan))


class DigitRecognizerTests(unittest.TestCase):
    def test_recognizes_the_demonstrated_three_five_six_and_seven_styles(self) -> None:
        recognizer = DigitRecognizer()

        predictions = [
            recognizer.predict(image)
            for image in _DRAWING_EXAMPLES
        ]

        self.assertEqual([digit for digit, _ in predictions], _DRAWING_LABELS.tolist())
        self.assertTrue(all(0 <= confidence <= 1 for _, confidence in predictions))

    def test_augments_examples_with_original_labels(self) -> None:
        images, labels = augment_drawing_examples()

        self.assertEqual(images.shape, (len(_DRAWING_LABELS) * 12, 8, 8))
        np.testing.assert_array_equal(
            labels,
            np.repeat(_DRAWING_LABELS, 12),
        )

    def test_recognizes_scale_and_position_variations_of_five_and_seven(self) -> None:
        recognizer = DigitRecognizer()
        augmented_images, augmented_labels = augment_drawing_examples()
        relevant_indices = np.flatnonzero(np.isin(augmented_labels, [5, 7]))

        predictions = [
            recognizer.predict(augmented_images[index])[0]
            for index in relevant_indices
        ]

        np.testing.assert_array_equal(
            predictions,
            augmented_labels[relevant_indices],
        )

    def test_augments_nines_with_rotations(self) -> None:
        digits = load_digits()
        images, labels = augment_nine_examples(digits.images, digits.target)

        self.assertEqual(images.shape, (np.count_nonzero(digits.target == 9) * 4, 8, 8))
        np.testing.assert_array_equal(labels, np.full(len(labels), 9))
        self.assertTrue(np.all((images >= 0) & (images <= 16)))

    def test_prepares_browser_style_training_examples(self) -> None:
        digits = load_digits()
        source_images = digits.images[:3]
        source_labels = digits.target[:3]

        images, labels = augment_browser_examples(source_images, source_labels)

        self.assertEqual(images.shape, (3, 8, 8))
        np.testing.assert_array_equal(labels, source_labels)
        self.assertTrue(np.all(np.isfinite(images)))

    def test_recognizes_rotated_held_out_nines(self) -> None:
        digits = load_digits()
        _, test_images, _, test_labels = train_test_split(
            digits.images,
            digits.target,
            test_size=0.2,
            random_state=42,
            stratify=digits.target,
        )
        held_out_nines, _ = augment_nine_examples(
            test_images[test_labels == 9][:10],
            np.full(10, 9),
        )
        recognizer = DigitRecognizer()

        predictions = [recognizer.predict(image)[0] for image in held_out_nines]

        self.assertEqual(predictions, [9] * len(held_out_nines))

    def test_recognizes_rotated_nines_after_browser_preprocessing(self) -> None:
        digits = load_digits()
        _, test_images, _, test_labels = train_test_split(
            digits.images,
            digits.target,
            test_size=0.2,
            random_state=42,
            stratify=digits.target,
        )
        held_out_nines, labels = augment_nine_examples(
            test_images[test_labels == 9][:10],
            np.full(10, 9),
        )
        browser_images, browser_labels = augment_browser_examples(
            held_out_nines,
            labels,
        )
        recognizer = DigitRecognizer()

        predictions = [recognizer.predict(image)[0] for image in browser_images]

        np.testing.assert_array_equal(predictions, browser_labels)


if __name__ == "__main__":
    unittest.main()
