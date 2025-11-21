import cv2
from rich import print
import numpy as np

def detect_line_segments(image_path):
    """Return polyline points of the line chart."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 40, 120)

    # morphological thinning helps line continuity
    kernel = np.ones((2,2),np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # find contours = strokes of line
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # choose longest contour = main line
    if not contours:
        return []

    contour = max(contours, key=cv2.contourArea)
    contour = contour.squeeze()

    # smooth
    contour = cv2.approxPolyDP(contour, epsilon=2, closed=False)
    contour = contour.squeeze()

    return contour.tolist()

import easyocr
import re

reader = easyocr.Reader(['en'], gpu=False)

def get_ocr_blocks(image_path):
    results = reader.readtext(image_path)

    blocks = []
    for (bbox, text, conf) in results:
        blocks.append({
            "text": text,
            "bbox": bbox,
            "conf": conf
        })
    return blocks


def extract_numeric_ticks(blocks):
    ticks = []
    for blk in blocks:
        t = blk["text"].strip()

        if re.fullmatch(r"-?\d+(\.\d+)?", t):
            ticks.append({
                "value": float(t),
                "bbox": blk["bbox"]
            })

    return ticks

import cv2
import numpy as np

def detect_axes(image_path):
    img = cv2.imread(image_path, 0)
    edges = cv2.Canny(img, 50,150)

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi/180,
        threshold=100,
        minLineLength=100,
        maxLineGap=10
    )

    x_axis, y_axis = None, None

    if lines is None:
        return {"x_axis": None, "y_axis": None}

    for x1,y1,x2,y2 in lines[:,0]:
        if abs(y2-y1) < 10:
            x_axis = ((x1,y1),(x2,y2))
        if abs(x2-x1) < 10:
            y_axis = ((x1,y1),(x2,y2))

    return {
        "x_axis": x_axis,
        "y_axis": y_axis
    }


def build_scale_from_ticks(axis_line, ticks, orientation):
    """
    orientation: 'x' or 'y'
    ticks: OCR detected ticks
    """
    if axis_line is None or len(ticks) < 2:
        return None

    pts = []
    vals = []

    for t in ticks:
        bx = [p[0] for p in t["bbox"]]
        by = [p[1] for p in t["bbox"]]
        cx, cy = sum(bx)/4, sum(by)/4

        if orientation == 'x':
            pts.append(cx)
        else:
            pts.append(cy)

        vals.append(t["value"])

    # sort pixel positions & fit
    pts, vals = zip(*sorted(zip(pts, vals), key=lambda x: x[0]))

    a, b = np.polyfit(pts, vals, 1)

    return lambda px: a * px + b

# from utils.line_chart import detect_line_segments
# from utils.ocr_easyocr import get_ocr_blocks, extract_numeric_ticks
# from utils.axes import detect_axes, build_scale_from_ticks

def extract_line_chart(image_path):
    # 1) get line polyline
    polyline = detect_line_segments(image_path)

    # 2) OCR
    blocks = get_ocr_blocks(image_path)
    ticks = extract_numeric_ticks(blocks)

    # Separate x and y tick labels
    # Simple heuristic:
    x_ticks = [t for t in ticks if max(p[1] for p in t["bbox"]) > 100]  
    y_ticks = [t for t in ticks if max(p[0] for p in t["bbox"]) < 100]

    # 3) Axis detection
    axes = detect_axes(image_path)

    # 4) Build calibration maps
    x_scale = build_scale_from_ticks(axes["x_axis"], x_ticks, orientation='x')
    y_scale = build_scale_from_ticks(axes["y_axis"], y_ticks, orientation='y')

    # 5) Convert all polyline points to actual data values
    data_points = []
    for (x, y) in polyline:
        X = x_scale(x) if x_scale else None
        Y = y_scale(y) if y_scale else None
        data_points.append({"x": X, "y": Y})

    return data_points

if __name__ == "__main__":
    points = extract_line_chart("output/DOC-1/images/DOC-1-picture-1-line_chart.png")
    print(points)
    num=get_ocr_blocks("output/DOC-1/images/DOC-1-picture-1-line_chart.png")
    print(num)
