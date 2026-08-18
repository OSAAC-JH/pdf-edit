"""
scripts/compress.py
pikepdf를 활용하여 PDF 용량을 압축 및 최적화합니다.
--target-mb 지정 시, 구조적 압축(pikepdf)만으로 목표에 못 미치면
PyMuPDF로 내장 이미지를 단계적으로 재압축/다운스케일하여 목표에 최대한 근접시킵니다
(목표 용량은 최선 노력(best-effort) 기준이며, 텍스트 위주 PDF 등에서는 도달하지 못할 수 있습니다).
사용 예시:
  - 기본 압축: python scripts/compress.py input.pdf --output compressed.pdf
  - 목표 용량 지정: python scripts/compress.py input.pdf --output compressed.pdf --target-mb 3
"""

import argparse
import os
import sys
import shutil
import tempfile
import pikepdf
import pymupdf
from common import validate_input_file, ensure_output_dir, print_success

# 단계적으로 낮춰가며 시도할 JPEG 품질 값
QUALITY_LADDER = [80, 65, 50, 35, 20]


def structural_compress(input_path: str, output_path: str):
    with pikepdf.open(input_path) as pdf:
        pdf.save(
            output_path,
            compress_streams=True,
            recompress_flate=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
        )


def recompress_images(input_path: str, output_path: str, quality: int, shrink_factor: int = 0):
    """내장 이미지를 지정 품질의 JPEG로 재인코딩하고, 필요 시 해상도도 축소합니다."""
    doc = pymupdf.open(input_path)
    seen_xrefs = set()

    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            pix = pymupdf.Pixmap(doc, xref)
            if pix.colorspace is None or pix.colorspace.n not in (1, 3):
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            if pix.alpha:
                pix = pymupdf.Pixmap(pix, 0)
            if shrink_factor > 0:
                pix.shrink(shrink_factor)

            jpg_bytes = pix.tobytes("jpg", jpg_quality=quality)
            page.replace_image(xref, stream=jpg_bytes)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 용량 압축 및 최적화")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument("--output", type=str, required=True, help="출력 PDF 파일 경로")
    parser.add_argument(
        "--target-mb",
        type=float,
        default=None,
        help="목표 용량(MB). 지정 시 구조적 압축만으로 부족하면 이미지 재압축을 단계적으로 시도 (최선 노력 기준)",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)
    orig_size = os.path.getsize(input_path)
    target_bytes = args.target_mb * 1024 * 1024 if args.target_mb else None

    with tempfile.TemporaryDirectory() as tmp_dir:
        stage_path = os.path.join(tmp_dir, "stage.pdf")
        structural_compress(input_path, stage_path)
        best_path = stage_path
        best_size = os.path.getsize(stage_path)

        if target_bytes and best_size > target_bytes:
            for shrink_factor in (0, 1):
                for quality in QUALITY_LADDER:
                    candidate_path = os.path.join(
                        tmp_dir, f"cand_q{quality}_s{shrink_factor}.pdf"
                    )
                    recompress_images(best_path, candidate_path, quality, shrink_factor)
                    candidate_size = os.path.getsize(candidate_path)
                    if candidate_size < best_size:
                        best_path = candidate_path
                        best_size = candidate_size
                    if best_size <= target_bytes:
                        break
                if best_size <= target_bytes:
                    break

        shutil.copyfile(best_path, output_path)

    new_size = os.path.getsize(output_path)
    reduction = (1 - (new_size / orig_size)) * 100 if orig_size > 0 else 0
    target_note = ""
    if target_bytes:
        status = "달성" if new_size <= target_bytes else "미달 (최선 노력 결과)"
        target_note = f" | 목표 {args.target_mb}MB {status}"

    print_success(
        output_path,
        f"압축 완료: {orig_size / 1024:.1f}KB -> {new_size / 1024:.1f}KB "
        f"({reduction:.1f}% 감소){target_note}",
    )


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        run(args)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
