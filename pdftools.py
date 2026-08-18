#!/usr/bin/env python3
"""
pdftools.py
KBFG PDF Tools - PowerShell/CMD 터미널용 통합 실행기

사용법 (2가지 모드):
  1) 서브커맨드 모드 (스크립팅/자동화용, 옵션을 정확히 아는 경우)
       python pdftools.py split input.pdf --pages "1,3-5"
       python pdftools.py --help          (전체 기능 목록)
       python pdftools.py merge --help    (기능별 옵션 상세)

  2) 대화형 메뉴 모드 (사람이 직접 사용, 옵션을 몰라도 됨)
       python pdftools.py                 (인자 없이 실행하면 메뉴가 뜸)

두 모드 모두 scripts/ 폴더의 동일한 로직(build_parser/run)을 공유합니다.
"""

import os
import sys
import argparse

# scripts/ 디렉터리를 sys.path에 추가해야 각 모듈의 "from common import ..." 및
# 이 파일의 "import split, extract, ..." 가 정상 동작합니다.
SCRIPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import split
import extract
import merge
import to_image
import to_markdown
import watermark
import password
import rotate
import page_numbers
import bookmarks
import compress

# (서브커맨드 이름, 메뉴 설명, 모듈) - 이 순서가 대화형 메뉴 번호 순서
FEATURES = [
    ("split", "PDF 분할 (전체 낱장 또는 지정 페이지만)", split),
    ("extract", "PDF 페이지 추출 (범위 지정)", extract),
    ("merge", "PDF 병합 (파일별 부분 페이지 지정 가능)", merge),
    ("to-image", "PDF -> 이미지 변환 (긴 이미지 병합 옵션 포함)", to_image),
    ("to-markdown", "PDF -> Markdown 변환", to_markdown),
    ("watermark", "워터마크 삽입 (45도 타일 반복)", watermark),
    ("password", "암호 설정 / 해제", password),
    ("rotate", "페이지 회전 (그룹별 시계/반시계/180도 지정 가능)", rotate),
    ("page-numbers", "페이지 번호 삽입 (구간 지정, 표지 제외, 재시작 가능)", page_numbers),
    ("bookmarks", "북마크(목차) 추가 / 전체 삭제", bookmarks),
    ("compress", "용량 압축 (목표 용량 지정 가능)", compress),
]


# ----------------------------------------------------------------------
# 서브커맨드 모드
# ----------------------------------------------------------------------

def build_cli_parser():
    parser = argparse.ArgumentParser(
        prog="pdftools",
        description="KBFG PDF Tools - PDF 가공 통합 CLI. "
        "서브커맨드 없이 실행하면 대화형 메뉴가 시작됩니다.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="{" + ",".join(f[0] for f in FEATURES) + "}")
    for name, help_text, module in FEATURES:
        sub = subparsers.add_parser(name, help=help_text)
        module.build_parser(sub)
        sub.set_defaults(func=module.run)
    return parser


def run_cli():
    parser = build_cli_parser()
    args = parser.parse_args()

    if not getattr(args, "command", None):
        run_interactive_menu()
        return

    try:
        args.func(args)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


# ----------------------------------------------------------------------
# 대화형 메뉴 모드
# ----------------------------------------------------------------------

def list_pdfs(directory="."):
    return sorted(f for f in os.listdir(directory) if f.lower().endswith(".pdf"))


def prompt(msg, default=None):
    suffix = f" [{default}]" if default not in (None, "") else ""
    val = input(f"{msg}{suffix}: ").strip()
    return val if val else default


def select_pdf_interactive(prompt_msg="파일 번호 선택"):
    pdfs = list_pdfs()
    if not pdfs:
        print("현재 폴더에 PDF 파일이 없습니다. PDF 파일을 이 폴더에 두고 다시 시도하세요.")
        return None
    print("\n=== 현재 폴더의 PDF 파일 ===")
    for i, name in enumerate(pdfs, start=1):
        print(f"{i:02d}. {name}")
    while True:
        choice = input(f"{prompt_msg} (Q=취소): ").strip().lower()
        if choice == "q":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(pdfs):
            return pdfs[int(choice) - 1]
        print("잘못된 입력입니다.")


def collect_args_interactive(name):
    """선택된 기능에 필요한 입력을 받아 argparse.Namespace로 구성합니다."""
    ns = argparse.Namespace()
    needs_single_file = name not in ("merge",)

    input_file = None
    if needs_single_file:
        input_file = select_pdf_interactive()
        if input_file is None:
            return None

    if name == "split":
        ns.input_path = input_file
        ns.pages = prompt("분할 대상 페이지 (00=전체, 예: 1,3-5,7)", "00")
        ns.output_dir = prompt("출력 폴더", "./split_output")
        ns.prefix = prompt("파일 접두사 (Enter=원본 파일명)", "")
        return ns

    if name == "extract":
        ns.input_path = input_file
        ns.pages = prompt("추출할 페이지 (예: 1,3-5,7)")
        ns.output = prompt("출력 파일명", "extracted.pdf")
        return ns

    if name == "merge":
        pdfs = list_pdfs()
        if not pdfs:
            print("현재 폴더에 PDF 파일이 없습니다.")
            return None
        inputs = []
        print("\n병합할 PDF를 순서대로 선택하세요. (최소 2개, Q=선택 완료)")
        while True:
            print("\n=== 현재 폴더의 PDF 파일 ===")
            for i, p in enumerate(pdfs, start=1):
                print(f"{i:02d}. {p}")
            choice = input(f"추가할 파일 번호 (현재 {len(inputs)}개 선택됨, Q=완료): ").strip().lower()
            if choice == "q":
                break
            if choice.isdigit() and 1 <= int(choice) <= len(pdfs):
                fname = pdfs[int(choice) - 1]
                pages = prompt(f"'{fname}'에서 사용할 페이지 (Enter=전체 페이지)", "")
                inputs.append(f"{fname}:{pages}" if pages else fname)
            else:
                print("잘못된 입력입니다.")
        if len(inputs) < 2:
            print("병합에는 최소 2개 파일이 필요합니다. 처음부터 다시 시도하세요.")
            return None
        ns.inputs = inputs
        ns.output = prompt("출력 파일명", "merged.pdf")
        return ns

    if name == "to-image":
        ns.input_path = input_file
        ns.output_dir = prompt("출력 폴더", "./image_output")
        ns.pages = prompt("변환할 페이지 (all=전체, 예: 1,3-5)", "all")
        ns.dpi = int(prompt("DPI", "200"))
        ns.format = prompt("포맷 (png/jpg)", "png")
        ns.transparent = prompt("투명 배경 적용? (y/N)", "n").lower().startswith("y")
        ns.stitch = prompt("긴 이미지 한 장으로 합치기? (y/N)", "n").lower().startswith("y")
        return ns

    if name == "to-markdown":
        ns.input_path = input_file
        ns.output = prompt("출력 .md 파일명", "output.md")
        return ns

    if name == "watermark":
        ns.input_path = input_file
        ns.output = prompt("출력 파일명", "watermarked.pdf")
        ns.text = prompt("워터마크 문구")
        ns.opacity = float(prompt("투명도 (0.05-1.0)", "0.15"))
        ns.font_size = int(prompt("폰트 크기", "32"))
        ns.spacing = float(prompt("타일 간격(pt, 0=자동 계산)", "0"))
        return ns

    if name == "password":
        ns.input_path = input_file
        ns.decrypt = prompt("암호를 해제하시겠습니까? (y/N, N=암호 설정)", "n").lower().startswith("y")
        ns.output = prompt("출력 파일명", "output.pdf")
        ns.password = prompt("암호")
        return ns

    if name == "rotate":
        ns.input_path = input_file
        print("\n회전 그룹을 입력하세요. 형식: 페이지범위:각도 (양수=시계방향, 음수=반시계방향)")
        print("예: 1,3,5:90  또는  7-10:180")
        rotations = []
        while True:
            token = input(f"회전 그룹 (현재 {len(rotations)}개 입력됨, Enter=입력 완료): ").strip()
            if not token:
                break
            rotations.append(token)
        if not rotations:
            print("최소 1개의 회전 그룹이 필요합니다.")
            return None
        ns.rotations = rotations
        ns.output = prompt("출력 파일명", "rotated.pdf")
        return ns

    if name == "page-numbers":
        ns.input_path = input_file
        ns.output = prompt("출력 파일명", "numbered.pdf")
        ranges_input = prompt("번호 매길 구간 (공백으로 구분, 예: 2-10 12-24 / Enter=문서 전체)", "")
        ns.ranges = ranges_input.split() if ranges_input else None
        ns.format = prompt("번호 표기 형식", "{n} / {total}")
        return ns

    if name == "bookmarks":
        ns.input_path = input_file
        ns.output = prompt("출력 파일명", "bookmarked.pdf")
        mode = prompt("1=북마크 추가, 2=기존 북마크 전체 삭제", "1")
        if mode == "2":
            ns.clear = True
            ns.add = None
        else:
            ns.clear = False
            ns.add = prompt("북마크 목록 (형식: 제목:페이지;제목:페이지)")
        return ns

    if name == "compress":
        ns.input_path = input_file
        ns.output = prompt("출력 파일명", "compressed.pdf")
        target = prompt("목표 용량(MB, Enter=미지정)", "")
        ns.target_mb = float(target) if target else None
        return ns

    return None


def run_interactive_menu():
    print("=" * 56)
    print(" KBFG PDF Tools - 대화형 메뉴")
    print("=" * 56)
    print("PDF 파일을 이 폴더에 넣고 번호를 선택해 진행하세요.")

    while True:
        print("\n=== 기능 선택 ===")
        for i, (name, help_text, _) in enumerate(FEATURES, start=1):
            print(f"{i:02d}. {help_text}")
        print(" Q. 종료")

        choice = input("\n번호 선택: ").strip().lower()
        if choice == "q":
            print("종료합니다.")
            return
        if not (choice.isdigit() and 1 <= int(choice) <= len(FEATURES)):
            print("잘못된 입력입니다.")
            continue

        name, _, module = FEATURES[int(choice) - 1]
        try:
            args_ns = collect_args_interactive(name)
            if args_ns is None:
                continue
            module.run(args_ns)
        except Exception as e:
            print(f"[ERROR] {e}")

        again = input("\n메인 메뉴로 돌아가려면 Enter, 종료하려면 Q: ").strip().lower()
        if again == "q":
            print("종료합니다.")
            return


if __name__ == "__main__":
    run_cli()
