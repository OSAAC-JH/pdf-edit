"""
scripts/rotate.py
PDF 페이지를 90도 단위로 회전합니다. 여러 페이지 그룹에 서로 다른 회전을 한 번에 적용할 수 있습니다.
사용 예시:
  - 단순 회전: python scripts/rotate.py input.pdf --rotations "1,3:90" --output rotated.pdf
  - 그룹별 회전: python scripts/rotate.py input.pdf --rotations "1,3,5:90" "2,4,6:-90" "7-10:180" --output rotated.pdf
    (양수=시계방향, 음수=반시계방향. 예: -90은 반시계 90도)
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from common import validate_input_file, ensure_output_dir, parse_page_range, print_success


def parse_rotation_group(token: str, total_pages: int):
    """'1,3,5:90' 형식의 토큰을 (페이지 리스트, 각도)로 분리합니다."""
    if ":" not in token:
        raise ValueError(f"잘못된 --rotations 형식입니다: '{token}' (형식: '페이지범위:각도')")
    pages_str, angle_str = token.rsplit(":", 1)
    angle_str = angle_str.strip()
    try:
        angle = int(angle_str)
    except ValueError:
        raise ValueError(f"각도는 정수여야 합니다: '{token}'")
    if angle % 90 != 0:
        raise ValueError(f"각도는 90의 배수여야 합니다: '{token}'")
    pages = parse_page_range(pages_str, max_pages=total_pages)
    return pages, angle % 360


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 페이지 회전 (그룹별 다른 각도 지정 가능)")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument("--output", type=str, required=True, help="출력 PDF 파일 경로")
    parser.add_argument(
        "--rotations",
        type=str,
        nargs="+",
        required=True,
        help="'페이지범위:각도' 형식의 회전 그룹 목록. 양수=시계방향, 음수=반시계방향 "
        "(예: '1,3,5:90' '2,4,6:-90' '7-10:180')",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)

    reader = PdfReader(input_path, strict=False)
    total_pages = len(reader.pages)

    page_angle_map = {}
    for token in args.rotations:
        pages, angle = parse_rotation_group(token, total_pages)
        for p in pages:
            if p in page_angle_map:
                raise ValueError(f"페이지 {p}가 여러 회전 그룹에 중복 지정되었습니다.")
            page_angle_map[p] = angle

    writer = PdfWriter()
    for idx, page in enumerate(reader.pages, start=1):
        if idx in page_angle_map:
            page.rotate(page_angle_map[idx])
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print_success(
        output_path,
        f"{len(page_angle_map)}개 페이지 회전 완료 ({len(args.rotations)}개 그룹)",
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
