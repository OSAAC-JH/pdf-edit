"""
scripts/page_numbers.py
PDF 문서 하단에 페이지 번호를 삽입합니다. 특정 구간만 지정하거나, 구간별로 번호를 재시작할 수 있습니다.
사용 예시:
  - 전체 문서: python scripts/page_numbers.py input.pdf --output numbered.pdf
  - 표지 제외(2페이지부터): python scripts/page_numbers.py input.pdf --output numbered.pdf --ranges "2-10"
  - 구간별 재시작: python scripts/page_numbers.py input.pdf --output numbered.pdf --ranges "2-10" "12-24" "26-30"
"""

import argparse
import io
import sys
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from common import validate_input_file, ensure_output_dir, parse_page_range, print_success


def create_number_layer(text: str, width: float, height: float) -> PdfReader:
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFont("Helvetica", 10)
    can.drawCentredString(width / 2, 25, text)
    can.save()
    packet.seek(0)
    return PdfReader(packet)


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 페이지 번호 추가 (구간 지정/재시작 가능)")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument("--output", type=str, required=True, help="출력 PDF 파일 경로")
    parser.add_argument(
        "--ranges",
        type=str,
        nargs="+",
        default=None,
        help="번호를 매길 구간 목록. 각 구간은 그 안에서 1부터 재시작 "
        "(기본값: 문서 전체를 하나의 구간으로 취급, 예: '2-10' '12-24' '26-30')",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="{n} / {total}",
        help="페이지 번호 포맷 (사용 가능 변수: {n}=구간 내 번호, {total}=구간 내 총 페이지 수)",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)

    reader = PdfReader(input_path, strict=False)
    total_doc_pages = len(reader.pages)
    writer = PdfWriter()

    range_specs = args.ranges if args.ranges else [f"1-{total_doc_pages}"]

    # {실제 페이지 번호: (구간 내 순번, 구간 내 총 페이지 수)}
    label_map = {}
    for spec in range_specs:
        pages_in_range = parse_page_range(spec, max_pages=total_doc_pages)
        group_total = len(pages_in_range)
        for local_idx, real_page in enumerate(pages_in_range, start=1):
            if real_page in label_map:
                raise ValueError(f"페이지 {real_page}가 여러 --ranges 구간에 중복 지정되었습니다.")
            label_map[real_page] = (local_idx, group_total)

    for idx, page in enumerate(reader.pages, start=1):
        if idx in label_map:
            local_idx, group_total = label_map[idx]
            w = float(page.mediabox.width)
            h = float(page.mediabox.height)
            label = args.format.format(n=local_idx, total=group_total)
            num_reader = create_number_layer(label, w, h)
            page.merge_page(num_reader.pages[0])
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print_success(
        output_path,
        f"페이지 번호 삽입 완료 ({len(label_map)}장 / {len(range_specs)}개 구간)",
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
