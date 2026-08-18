"""
scripts/bookmarks.py
PDF 문서의 북마크(목차)를 추가하거나 기존 북마크를 일괄 제거합니다.
사용 예시:
  - 북마크 제거: python scripts/bookmarks.py input.pdf --output clean.pdf --clear
  - 북마크 추가: python scripts/bookmarks.py input.pdf --output marked.pdf --add "제1장 서론:1;제2장 본론:5"
"""

import argparse
import sys
import pymupdf
from common import validate_input_file, ensure_output_dir, print_success


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 북마크 추가 및 제거")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument("--output", type=str, required=True, help="출력 PDF 파일 경로")
    parser.add_argument("--clear", action="store_true", help="기존 북마크 일괄 제거")
    parser.add_argument(
        "--add",
        type=str,
        help="추가할 북마크 목록 (형식: '제목:페이지;제목:페이지', 예: '서론:1;본론:5'). "
        "제목에 콤마(,)가 들어가도 되도록 항목 구분자는 세미콜론(;)을 사용합니다.",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)

    doc = pymupdf.open(input_path)
    total_pages = len(doc)

    if args.clear:
        doc.set_toc([])
        doc.save(output_path)
        print_success(output_path, "기존 북마크 일괄 제거 완료")
    elif args.add:
        toc = []
        entries = [e.strip() for e in args.add.split(";") if e.strip()]
        for entry in entries:
            if ":" not in entry:
                raise ValueError(f"잘못된 북마크 형식입니다: '{entry}' (형식: '제목:페이지')")
            title, page_str = entry.rsplit(":", 1)
            title = title.strip()
            page_str = page_str.strip()
            if not title:
                raise ValueError(f"북마크 제목이 비어 있습니다: '{entry}'")
            if not page_str.isdigit():
                raise ValueError(f"페이지 번호는 정수여야 합니다: '{entry}'")
            page = int(page_str)
            if page < 1 or page > total_pages:
                raise ValueError(
                    f"페이지 번호({page})가 문서 범위(1-{total_pages})를 벗어났습니다: '{entry}'"
                )
            toc.append([1, title, page])

        doc.set_toc(toc)
        doc.save(output_path)
        print_success(output_path, f"{len(toc)}개 북마크 추가 완료")
    else:
        raise ValueError("--clear 또는 --add 옵션 중 하나를 지정해야 합니다.")

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
