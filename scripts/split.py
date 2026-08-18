"""
scripts/split.py
PDF 문서를 개별 단일 페이지 PDF 파일들로 분할합니다.
사용 예시:
  - 전체 분할: python scripts/split.py input.pdf --output-dir ./output_pages/
  - 특정 페이지만 분할: python scripts/split.py input.pdf --pages "1,3-5,7" --output-dir ./output_pages/
"""

import argparse
import os
import sys
from pypdf import PdfReader, PdfWriter
from common import validate_input_file, parse_page_range, print_success


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 문서를 개별 페이지 파일로 분할")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument(
        "--pages",
        type=str,
        default="00",
        help="분할 대상 페이지 범위 (기본값: 00=전체, 예: 1,3-5,7)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./split_output",
        help="분할된 파일들이 저장될 디렉터리 경로",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="저장 파일 접두사 (기본값: 원본 파일명)",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    prefix = args.prefix if args.prefix else base_name

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    target_pages = parse_page_range(args.pages, max_pages=total_pages)

    for p_num in target_pages:
        writer = PdfWriter()
        writer.add_page(reader.pages[p_num - 1])
        out_file = os.path.join(output_dir, f"{prefix}_page_{p_num}.pdf")
        with open(out_file, "wb") as f:
            writer.write(f)

    print_success(
        output_dir,
        f"총 {len(target_pages)}개 페이지 분할 완료 ({args.pages}) -> {output_dir}",
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
