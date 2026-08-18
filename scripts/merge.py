"""
scripts/merge.py
여러 PDF 파일을 지정된 순서대로 하나의 PDF로 병합합니다.
각 입력은 "경로" 또는 "경로:페이지범위" 형식을 사용할 수 있습니다 (페이지범위 생략 시 전체 페이지).
사용 예시:
  - 전체 병합: python scripts/merge.py a.pdf b.pdf c.pdf --output merged.pdf
  - 부분 병합: python scripts/merge.py "a.pdf:1-10" "b.pdf:3-8" "c.pdf:4,8,10" --output merged.pdf
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from common import validate_input_file, ensure_output_dir, parse_page_range, print_success


def parse_input_spec(spec: str):
    """'path' 또는 'path:pages' 문자열을 (path, pages_str|None)으로 분리합니다.

    Windows 드라이브 경로(예: C:\\...)의 콜론과 혼동되지 않도록,
    마지막 콜론 뒤가 페이지 범위 패턴(숫자/콤마/하이픈)일 때만 분리합니다.
    """
    if ":" not in spec:
        return spec, None

    path_part, _, tail = spec.rpartition(":")
    tail_stripped = tail.strip()
    is_page_spec = tail_stripped != "" and all(
        c.isdigit() or c in ",-" for c in tail_stripped
    )
    if path_part and is_page_spec:
        return path_part, tail_stripped
    return spec, None


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(
        description="여러 PDF 파일을 순차적으로 병합 (부분 페이지 지정 가능)"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help='병합할 PDF 파일 경로 목록. "파일.pdf" 또는 "파일.pdf:1-10" 형식 (순서대로 병합)',
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="생성될 출력 PDF 파일 경로",
    )
    return parser


def run(args):
    if len(args.inputs) < 2:
        raise ValueError("병합을 위해서는 최소 2개 이상의 PDF 파일이 필요합니다.")

    output_path = ensure_output_dir(args.output)
    writer = PdfWriter()
    summary = []

    for spec in args.inputs:
        file_path, page_spec = parse_input_spec(spec)
        valid_path = validate_input_file(file_path)

        if page_spec:
            total_pages = len(PdfReader(valid_path).pages)
            pages_1based = parse_page_range(page_spec, max_pages=total_pages)
            pages_0based = [p - 1 for p in pages_1based]
            writer.append(valid_path, pages=pages_0based)
            summary.append(f"{file_path}({page_spec}: {len(pages_1based)}장)")
        else:
            writer.append(valid_path)
            summary.append(file_path)

    with open(output_path, "wb") as f:
        writer.write(f)

    print_success(
        output_path,
        f"총 {len(args.inputs)}개 소스 병합 완료 [{', '.join(summary)}]",
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
