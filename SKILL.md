---
name: kbfg-pdf-tools
description: PDF 분할, 병합, 추출, 이미지 변환, Markdown 변환, 암호화, 회전, 워터마크, 페이지 번호, 북마크, 압축을 처리하는 종합 PDF 가공 도구
allowed-tools: [Bash, ReadFile, GlobTool]
---

## 1. 개요
사용자의 자연어 요청 의도를 분석하여 해당하는 `references/*.md` 문서를 확인하고, 비대화형(non-interactive) Python 스크립트(`scripts/*.py`)를 CLI로 호출하여 PDF 작업을 완수합니다.

## 2. 라우팅 테이블 (Routing Table)

| 요청 의도 / 주요 키워드 | 참조 문서 | 실행 스크립트 |
| :--- | :--- | :--- |
| 1페이지씩 전체/부분 분할, 낱장 쪼개기 | references/split.md | scripts/split.py |
| 특정 페이지만 추출, 범위 선택 | references/extract.md | scripts/extract.py |
| 여러 PDF 결합, 파일별 부분 페이지만 병합 | references/merge.md | scripts/merge.py |
| PNG/JPG 이미지 변환, 세로 긴 이미지 합성 | references/to-image.md | scripts/to_image.py |
| 본문/표 텍스트를 Markdown으로 변환 | references/to-markdown.md | scripts/to_markdown.py |
| 비밀번호 잠금 설정, 암호 해제 | references/password.md | scripts/password.py |
| 페이지 그룹별 시계/반시계/180도 회전 | references/rotate.md | scripts/rotate.py |
| 45도 반복 타일 워터마크 합성 (대외비 등) | references/watermark.md | scripts/watermark.py |
| 하단 페이지 번호 삽입, 표지 제외, 구간별 재시작 | references/page-numbers.md | scripts/page_numbers.py |
| 목차/북마크 추가 또는 기존 목차 삭제 | references/bookmarks.md | scripts/bookmarks.py |
| 파일 용량 줄이기, 목표 용량(MB) 지정 압축 | references/compress.md | scripts/compress.py |

## 3. 공통 실행 워크플로우
1. 요청 분석: 사용자의 발화 내용에 매칭되는 라우팅 대상을 확인합니다.
2. 세부 지침 확인: 해당 `references/<기능명>.md` 문서를 읽어 필요한 인자(Arguments)와 플래그 구조를 파악합니다.
3. 사전 검증: 대상 PDF 파일이 실제 존재하는지 확인합니다.
4. CLI 실행: 스크립트를 비대화형으로 실행합니다 (`input()` 대기 없음).
5. 결과 확인: 표준 출력(`OUTPUT_FILE: <경로>`)을 확인하여 사용자에게 최종 완료 보고를 수행합니다.