import csv
import logging
import math
import time
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import (  # pyright: ignore[reportPrivateImportUsage]
    PictureItem, TableItem)

from .bar import (build_scale_from_ticks, detect_bars, extract_bar_values,
                  extract_numeric_ticks, get_text_blocks)
from .get_desc import get_responses
from .line import extract_line_chart, get_ocr_blocks
from .pie import extract_pie_chart

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0

redundent_types = [
    "remote_sensing",
    "logo",
    "other",
    "map",
    "screenshot",
    "signature",
    "chemistry_molecular_structure",
    "icon",
    "stamp",
    "chemistry_markush_structure",
    "bar_code",
    "qr_code",
]


def main(input_doc_path: Path):
    logging.basicConfig(level=logging.INFO)

    if not input_doc_path.is_file():
        return []

    output_dir = Path("output") / input_doc_path.name.split(".")[0]

    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    pipeline_options.do_picture_classification = True
    pipeline_options.do_picture_description = False

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_res.input.file.stem

    images_path = output_dir / "images"
    images_path.mkdir(exist_ok=True)

    tables_path = output_dir / "tables"
    tables_path.mkdir(exist_ok=True)

    picture_counter = 0
    table_counter = 0

    for element, _level in conv_res.document.iterate_items():
        # ========== TABLES ==========
        if isinstance(element, TableItem):
            table_counter += 1
            img_file = tables_path / f"{doc_filename}-table-{table_counter}.png"
            csv_file = tables_path / f"{doc_filename}-table-{table_counter}.csv"

            element.get_image(conv_res.document).save(img_file, "PNG")  # pyright: ignore[reportOptionalMemberAccess]
            df = element.export_to_dataframe(conv_res.document)
            df.to_csv(csv_file, index=False)
            continue

        # ========== PICTURES ==========
        if isinstance(element, PictureItem):
            major_type = element.annotations[0].predicted_classes[0].class_name  # pyright: ignore[reportAttributeAccessIssue]

            if major_type in redundent_types:
                continue

            picture_counter += 1

            img_file = (
                images_path
                / f"{doc_filename}-picture-{picture_counter}-{major_type}.png"
            )

            element.get_image(conv_res.document).save(img_file, "PNG")  # pyright: ignore[reportOptionalMemberAccess]
            csv_file = (
                images_path
                / f"{doc_filename}-picture-{picture_counter}-{major_type}.csv"
            )
            img_file = str(img_file)
            try:
                if "bar_chart" in major_type:
                    bars = detect_bars(img_file)
                    ocr_data = get_text_blocks(img_file)

                    ticks = extract_numeric_ticks(ocr_data)
                    pixel_to_val = build_scale_from_ticks(ticks)

                    bar_heights = extract_bar_values(
                        bars, pixel_to_val, baseline_y=None
                    )

                    texts = [item["text"] for item in ocr_data]
                    heights = [float(h) for h in bar_heights] + [math.nan] * (
                        len(texts) - len(bar_heights)
                    )

                    with open(csv_file, mode="w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(texts)  # first row: texts
                        writer.writerow(heights)  # second row: bar heights

                elif "line_chart" in major_type:
                    coords = extract_line_chart(img_file)
                    ocr_data = get_ocr_blocks(img_file)

                    x_row = [
                        float(c["x"]) if c["x"] is not None else math.nan
                        for c in coords[: len(ocr_data)]
                    ]
                    y_row = [
                        float(c["y"]) if c["y"] is not None else math.nan
                        for c in coords[: len(ocr_data)]
                    ]
                    text_row = [item["text"] for item in ocr_data]

                    with open(csv_file, mode="w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(x_row)
                        writer.writerow(y_row)
                        writer.writerow(text_row)
                elif "pie_chart" in major_type:
                    data = extract_pie_chart(img_file)
                    with open(csv_file, mode="w", newline="") as f:
                        writer = csv.writer(f)
                        # Header
                        writer.writerow(["name", "percentage"])

                        for item in data:
                            writer.writerow([item["label"], float(item["percentage"])])
                if not csv_file.exists():
                    csv_file.touch()
            except Exception as e:
                _log.error(e)
                csv_file.touch()

    csvs, images = get_responses(output_dir)

    elapsed = time.time() - start_time
    _log.info(f"Document converted and figures exported in {elapsed:.2f} seconds.")
    return csvs, images
