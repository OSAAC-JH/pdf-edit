"""
scripts/to_image.py
PyMuPDF를 활용하여 PDF 페이지를 이미지로 변환합니다.
- 단일 페이지 변환 / 전체 페이지 변환
- 세로 긴 이미지로 합치기 (--stitch) 지원
- 투명 배경 (--transparent) 지원
"""

import argparse
import os
import sys
import pymupdf
from common import (
    validate_input_file,
    parse_page_range,
    print_success,
)


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 페이지를 이미지로 변환 (PyMuPDF 기반)")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./image_output",
        help="이미지가 저장될 디렉터리 경로",
    )
    parser.add_argument(
        "--pages",
        type=str,
        default="all",
        help="변환할 페이지 범위 (기본값: all, 예: 1,3-5)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="이미지 해상도 DPI (기본값: 200)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["png", "jpg", "jpeg"],
        default="png",
        help="이미지 포맷 (기본값: png)",
    )
    parser.add_argument(
        "--transparent",
        action="store_true",
        help="투명 배경 적용 (PNG 포맷 전용)",
    )
    parser.add_argument(
        "--stitch",
        action="store_true",
        help="모든 페이지를 하나의 긴 세로 이미지로 병합하여 저장",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    doc = pymupdf.open(input_path)
    total_pages = len(doc)
    target_pages = parse_page_range(args.pages, max_pages=total_pages)

    alpha = args.transparent and args.format == "png"
    pixmaps = []

    for p_num in target_pages:
        page = doc[p_num - 1]
        pix = page.get_pixmap(dpi=args.dpi, alpha=alpha)
        pixmaps.append((p_num, pix))

    if args.stitch and len(pixmaps) > 1:
        total_height = sum(pix.height for _, pix in pixmaps)
        max_width = max(pix.width for _, pix in pixmaps)

        colorspace = pymupdf.csRGB
        stitched_pix = pymupdf.Pixmap(colorspace, pymupdf.IRect(0, 0, max_width, total_height), alpha)
        if not alpha:
            stitched_pix.clear_with(255)

        y_offset = 0
        for _, pix in pixmaps:
            # set_origin으로 픽스맵의 좌표계 자체를 이동시켜야 stitched_pix의
            # 해당 위치에 정확히 복사된다 (copy()는 절대 좌표 기준으로 동작).
            pix.set_origin(0, y_offset)
            stitched_pix.copy(pix, pix.irect)
            y_offset += pix.height

        out_file = os.path.join(output_dir, f"{base_name}_stitched.{args.format}")
        stitched_pix.save(out_file)
        print_success(out_file, f"총 {len(pixmaps)}개 페이지 긴 이미지 병합 완료")
    else:
        for p_num, pix in pixmaps:
            out_file = os.path.join(output_dir, f"{base_name}_p{p_num}.{args.format}")
            pix.save(out_file)
        print_success(output_dir, f"총 {len(pixmaps)}개 페이지 이미지 변환 완료")

    doc.close()


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
