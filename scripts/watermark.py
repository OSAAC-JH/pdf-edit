"""
scripts/watermark.py
PDF 문서 전체에 45도 대각선 텍스트 워터마크를 고르게(타일 형태로) 반복 배치합니다.
사용 예시: python scripts/watermark.py input.pdf --text "CONFIDENTIAL" --output watermarked.pdf
"""

import argparse
import io
import math
import sys
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from common import validate_input_file, ensure_output_dir, print_success


def create_watermark_layer(
    text: str, width: float, height: float, opacity: float, font_size: int, spacing: float
) -> PdfReader:
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))
    can.setFont("Helvetica-Bold", font_size)

    text_width = stringWidth(text, "Helvetica-Bold", font_size)
    # 45도 회전된 텍스트끼리 겹치지 않도록, 텍스트 폭보다 약간 넉넉한 간격을 기본값으로 사용
    diag = math.hypot(width, height)
    step = spacing if spacing > 0 else text_width * 1.3

    can.saveState()
    can.translate(width / 2, height / 2)
    can.rotate(45)
    # 회전된 좌표계 기준으로 (-diag, -diag) ~ (diag, diag) 범위를 격자로 채움
    y = -diag
    while y <= diag:
        x = -diag
        while x <= diag:
            can.drawCentredString(x, y, text)
            x += step
        y += step
    can.restoreState()

    can.save()
    packet.seek(0)
    return PdfReader(packet)


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 텍스트 워터마크 추가 (전체 페이지 타일링)")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument("--output", type=str, required=True, help="출력 PDF 파일 경로")
    parser.add_argument("--text", type=str, required=True, help="워터마크 텍스트")
    parser.add_argument("--opacity", type=float, default=0.15, help="투명도 (0.05 - 1.0, 기본값: 0.15)")
    parser.add_argument("--font-size", type=int, default=32, help="워터마크 폰트 크기 (기본값: 32)")
    parser.add_argument(
        "--spacing",
        type=float,
        default=0,
        help="타일 간격(pt). 0 또는 미지정 시 텍스트 길이 기반 자동 계산",
    )
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)

    reader = PdfReader(input_path, strict=False)
    writer = PdfWriter()

    for page in reader.pages:
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        wm_reader = create_watermark_layer(
            args.text, w, h, args.opacity, args.font_size, args.spacing
        )
        page.merge_page(wm_reader.pages[0])
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print_success(output_path, f"워터마크('{args.text}') 전체 페이지 타일 배치 완료")


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
