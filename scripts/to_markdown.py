"""
scripts/to_markdown.py
PDF 및 지원 문서를 Markdown 형식으로 구조화하여 변환합니다.
사용 예시: python scripts/to_markdown.py input.pdf --output result.md
"""

import argparse
import sys
from markitdown import MarkItDown
from common import validate_input_file, ensure_output_dir, print_success


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 문서를 Markdown으로 변환")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument("--output", type=str, required=True, help="출력 .md 파일 경로")
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)

    md = MarkItDown()
    result = md.convert(input_path)
    text_content = (result.text_content or "").strip()

    if not text_content:
        raise ValueError(
            "PDF에서 추출된 텍스트가 없습니다. 스캔된 문서이거나 이미지로만 구성된 PDF일 수 있습니다. "
            "이 기능은 텍스트 레이어가 있는 PDF에서만 동작하며, OCR은 지원하지 않습니다."
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result.text_content)

    print_success(output_path, f"Markdown 변환 완료 ({len(text_content)}자)")


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
