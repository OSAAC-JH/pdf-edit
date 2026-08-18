"""
scripts/password.py
PDF에 암호를 설정하거나 기존 암호를 제거합니다.
사용 예시:
  - 암호 설정: python scripts/password.py input.pdf --output encrypted.pdf --password "mysecret"
  - 암호 해제: python scripts/password.py encrypted.pdf --output decrypted.pdf --decrypt --password "mysecret"
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from common import validate_input_file, ensure_output_dir, print_success


def build_parser(subparser=None):
    parser = subparser or argparse.ArgumentParser(description="PDF 암호 추가 및 제거")
    parser.add_argument("input_path", help="입력 PDF 파일 경로")
    parser.add_argument("--output", type=str, required=True, help="출력 PDF 파일 경로")
    parser.add_argument("--password", type=str, required=True, help="설정할 암호 또는 기존 암호")
    parser.add_argument("--decrypt", action="store_true", help="암호 해제 모드")
    return parser


def run(args):
    input_path = validate_input_file(args.input_path)
    output_path = ensure_output_dir(args.output)

    reader = PdfReader(input_path, strict=False)

    if args.decrypt:
        if reader.is_encrypted:
            if not reader.decrypt(args.password):
                raise ValueError("제공된 암호가 일치하지 않습니다.")
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        print_success(output_path, "PDF 암호 해제 완료")
    else:
        if reader.is_encrypted:
            if not reader.decrypt(args.password):
                raise ValueError("기존 PDF의 암호가 제공된 --password 값과 일치하지 않습니다.")
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(args.password)
        with open(output_path, "wb") as f:
            writer.write(f)
        print_success(output_path, "PDF 암호 설정 완료")


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
