import cv2
from rich import print
import numpy as np
import easyocr

def angle_from_center(cx, cy, lx, ly):
    return np.degrees(np.arctan2(ly - cy, lx - cx)) % 360


def extract_pie_chart(pie_path):
    img = cv2.imread(pie_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # --- Detect circle ---
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 200)
    x, y, r = circles[0][0]

    # --- Slice borders ---
    edges = cv2.Canny(gray, 80, 150)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 120)

    angles = sorted([theta * 180 / np.pi for rho, theta in lines[:,0]])
    slices = [(angles[i+1] - angles[i]) % 360 for i in range(len(angles)-1)]
    slices.append((360 - angles[-1] + angles[0]) % 360)

    # --- OCR ---
    reader = easyocr.Reader(['en'])
    ocr_res = reader.readtext(img)

    # --- Extract labels + % ---
    raw_labels = []
    raw_pcts = []
    for box, text, conf in ocr_res:
        if "%" in text:
            raw_pcts.append(text)
        else:
            raw_labels.append(text)

    mapping = []
    for label, angle in zip(raw_labels, slices):
        pct = None
        for p in raw_pcts:
            if label.lower() in p.lower():
                pct = int(p.replace("%",""))
                break

        mapping.append({
            "label": label,
            "angle": angle,
            "percentage": pct or round(angle/360*100,1)
        })

    return mapping

if __name__ == "__main__":
    num=extract_pie_chart("output/DOC-1/images/DOC-1-picture-10-pie_chart.png")
    print(num)
