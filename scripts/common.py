"""
scripts/common.py
KBFG PDF Tools 공통 유틸리티 모듈
- 페이지 범위 문자열 파싱 (예: "1,3-5,7" -> [1, 3, 4, 5, 7])
- 파일 경로 검증 및 표준 결과 포맷 출력
"""

import os
import sys
from typing import List, Set


def parse_page_range(range_str: str, max_pages: int = None) -> List[int]:
    """
    페이지 범위 문자열을 1-based 인덱스 리스트(오름차순, 중복 제거)로 변환합니다.
    
    Args:
        range_str: "1,3-5,7" 또는 "all" 형식의 문자열
        max_pages: PDF의 총 페이지 수 (범위 초과 검증용, 선택 사항)
        
    Returns:
        정렬된 1-based 페이지 번호 리스트
    """
    if not range_str or range_str.strip().lower() in ["all", "00"]:
        if max_pages is not None:
            return list(range(1, max_pages + 1))
        return []

    pages: Set[int] = set()
    parts = [p.strip() for p in range_str.split(",") if p.strip()]

    for part in parts:
        if "-" in part:
            sub_parts = part.split("-")
            if len(sub_parts) != 2:
                raise ValueError(f"잘못된 페이지 범위 형식입니다: '{part}'")
            
            start_str, end_str = sub_parts[0].strip(), sub_parts[1].strip()
            if not start_str.isdigit() or not end_str.isdigit():
                raise ValueError(f"페이지 번호는 정수여야 합니다: '{part}'")
            
            start, end = int(start_str), int(end_str)
            if start > end:
                raise ValueError(f"시작 페이지가 종료 페이지보다 큽니다: '{part}'")
            if start < 1:
                raise ValueError(f"페이지 번호는 1 이상이어야 합니다: '{part}'")

            pages.update(range(start, end + 1))
        else:
            if not part.isdigit():
                raise ValueError(f"페이지 번호는 정수여야 합니다: '{part}'")
            val = int(part)
            if val < 1:
                raise ValueError(f"페이지 번호는 1 이상이어야 합니다: '{part}'")
            pages.add(val)

    result = sorted(list(pages))

    if max_pages is not None:
        out_of_bounds = [p for p in result if p > max_pages]
        if out_of_bounds:
            raise ValueError(
                f"요청한 페이지({out_of_bounds})가 총 페이지 수({max_pages})를 초과합니다."
            )

    return result


def validate_input_file(file_path: str) -> str:
    """입력 파일의 존재 여부를 검증하고 절대 경로를 반환합니다."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {file_path}")
    return os.path.abspath(file_path)


def ensure_output_dir(output_path: str) -> str:
    """출력 대상 디렉터리가 없으면 생성하고 절대 경로를 반환합니다."""
    abs_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path


def print_success(output_file: str, message: str = ""):
    """챗 UI / Agent 파싱 규격에 맞춰 표준 출력(stdout)을 생성합니다."""
    if message:
        print(f"[INFO] {message}")
    print(f"OUTPUT_FILE: {os.path.abspath(output_file)}")