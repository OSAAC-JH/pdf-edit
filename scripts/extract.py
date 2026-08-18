"""
scripts/extract.py
지정한 페이지 범위를 추출하여 새로운 PDF 파일로 생성합니다.
사용 예시: python scripts/extract.py input.pdf --pages "1,3-5" --output extracted.pdf
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from common import (
    validate_input_file,
    ensure_output_dir,
    parse_page_range,
    print_success,
)


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF에서 특정 페이지 추출")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument(
        "--pages",
        type=str,
        required=True,
        help="추출 대상 페이지 범위 (예: 1,3-5,7)",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="생성될 출력 PDF 파일 경로",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    target_pages = parse_page_range(args.pages, max_pages=total_pages)

    writer = PdfWriter()
    for p_num in target_pages:
        writer.add_page(reader.pages[p_num - 1])

    with open(output_path, "wb") as f:
        writer.write(f)

    print_success(
        output_path,
        f"총 {len(target_pages)}개 페이지 추출 완료 ({args.pages})",
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
