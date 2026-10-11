# Handwritten Digit Recognizer

A mouse- and touch-friendly app that recognizes a handwritten digit from 0 to 9.
The browser app displays the prediction and estimated confidence under the
drawing pad.

## Run in GitHub Codespaces

From this folder, install dependencies and start the browser app:

```bash
python -m pip install -r requirements.txt
python web_app.py
```

Open the **Ports** tab in Codespaces and open port **5000** in your browser.

## Run on a desktop

```bash
python digit_recognizer.py
```

## Tests

```bash
python -m unittest -v test_digit_recognizer test_web_app
```

The app trains a support-vector classifier from scikit-learn's built-in
handwritten-digits dataset; it does not download a model. It includes extra
examples for the demonstrated 3, 5, 6, and 7 styles, browser-preprocessed
training images, small tilted/resized/shifted variations, and rotated 9s to
improve robustness to handwriting differences.
