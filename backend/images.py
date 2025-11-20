import logging
import time
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import \
    ImageRefMode  # pyright: ignore[reportPrivateImportUsage]
from docling_core.types.doc import \
    PictureItem  # pyright: ignore[reportPrivateImportUsage]
from docling_core.types.doc import \
    TableItem  # pyright: ignore[reportPrivateImportUsage]
from rich import print

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0

redundent_types = [
    "remote_sensing",
    "logo",
    "other",
    "screenshot",
    "signature",
    "chemistry_molecular_structure",
    "icon",
    "stamp",
    "chemistry_markush_structure",
    "bar_code",
    "qr_code",
]


def main():
    logging.basicConfig(level=logging.INFO)

    data_folder = Path(__file__).parent / "data/PDFS"
    input_doc_path = data_folder / "DOC-1.pdf"
    output_dir = Path("output")

    # Keep page/element images so they can be exported. The `images_scale` controls
    # the rendered image resolution (scale=1 ~ 72 DPI). The `generate_*` toggles
    # decide which elements are enriched with images.
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    pipeline_options.do_picture_classification = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_res.input.file.stem

    # Save page images
    for page_no, page in conv_res.document.pages.items():
        page_no = page.page_no
        page_image_filename = output_dir / f"{doc_filename}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")  # pyright: ignore[reportOptionalMemberAccess]

    # Save images of figures and tables
    table_counter = 0
    picture_counter = 0
    table_path = output_dir / "tables"
    table_path.mkdir(exist_ok=True)
    images_path = output_dir / "images"
    images_path.mkdir(exist_ok=True)
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = (
                table_path / f"{doc_filename}-table-{table_counter}.png"
            )
            element_pandas_filename = (
                table_path / f"{doc_filename}-table-{table_counter}.csv"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")  # pyright: ignore[reportOptionalMemberAccess]
            df = element.export_to_dataframe(conv_res.document)
            df.to_csv(element_pandas_filename, index=False)

        if isinstance(element, PictureItem):
            # print(element.caption_text(conv_res.document))
            major_type = element.annotations[0].predicted_classes[0].class_name  # pyright: ignore[reportAttributeAccessIssue]
            if major_type in redundent_types:
                continue
            picture_counter += 1
            element_image_filename = (
                images_path
                / f"{doc_filename}-picture-{picture_counter}-{major_type}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")  # pyright: ignore[reportOptionalMemberAccess]

    # Save markdown with embedded pictures
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    # Save markdown with externally referenced pictures
    md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    # Save HTML with externally referenced pictures
    html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
    conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

    end_time = time.time() - start_time

    _log.info(f"Document converted and figures exported in {end_time:.2f} seconds.")


if __name__ == "__main__":
    main()
