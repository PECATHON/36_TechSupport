import re

import cv2
import easyocr
import numpy as np
from rich import print


def detect_bars(image_path):
    img = cv2.imread(image_path, 0)
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bars = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 15 and h > 25:  # filter noise
            bars.append({"x": x, "y": y, "w": w, "h": h})

    # sort left→right
    bars = sorted(bars, key=lambda b: b["x"])
    return bars


reader = easyocr.Reader(["en"])


def get_text_blocks(image_path):
    results = reader.readtext(image_path)

    blocks = []
    for bbox, text, conf in results:
        blocks.append({"text": text, "bbox": bbox, "conf": conf})

    return blocks


def extract_numeric_ticks(blocks):
    ticks = []
    for blk in blocks:
        t = blk["text"]

        if re.fullmatch(r"-?\d+(\.\d+)?", t):
            ticks.append({"value": float(t), "bbox": blk["bbox"]})
    return ticks


def extract_category_labels(blocks):
    labels = []
    for blk in blocks:
        if re.fullmatch(r"[A-Za-z]+", blk["text"]):
            labels.append(blk)
    return labels


def build_scale_from_ticks(ticks):
    pts = []
    vals = []

    for t in ticks:
        ys = [p[1] for p in t["bbox"]]
        cy = sum(ys) / 4
        pts.append(cy)
        vals.append(t["value"])

    # Fit a line: value = a * pixel + b
    a, b = np.polyfit(pts, vals, 1)

    def pixel_to_val(px):
        return a * px + b

    return pixel_to_val


def extract_bar_values(bars, pixel_to_val, baseline_y):
    values = []
    for bar in bars:
        top_y = bar["y"]
        value = pixel_to_val(top_y)
        values.append(value)
    return values


if __name__ == "__main__":
    bars = detect_bars("output/DOC-1/images/DOC-1-picture-5-bar_chart.png")
    blocks = get_text_blocks("output/DOC-1/images/DOC-1-picture-5-bar_chart.png")
    print(blocks)

    ticks = extract_numeric_ticks(blocks)
    pixel_to_val = build_scale_from_ticks(ticks)

    bar_values = extract_bar_values(bars, pixel_to_val, baseline_y=None)

    print(bar_values)
