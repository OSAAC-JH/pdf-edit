## PDF 북마크 목차 관리 (Bookmarks)

- 트리거 예시: "PDF 북마크 목차 새로 추가해줘", "기존 책갈피 전부 지워줘"
- 스크립트: scripts/bookmarks.py
- 실행 예시:
```bash
# 북마크 추가 (항목 구분자는 세미콜론)
python scripts/bookmarks.py input.pdf --add "1장 개요:1;2장 본론:5;3장 결론:12" --output bookmarked.pdf

# 북마크 전체 삭제
python scripts/bookmarks.py input.pdf --clear --output no_bookmarks.pdf
```
- 옵션 설명:
  - --add: 추가할 북마크 목록 (`제목:페이지;제목:페이지` 형식, 항목 구분자는 세미콜론). 제목에 콤마(,)가 포함되어도 안전하게 처리됨
  - --clear: 기존 북마크 일괄 제거 플래그
  - --output: 생성될 출력 PDF 파일 경로 [필수]
- 지정한 페이지 번호가 문서 범위를 벗어나면 오류로 처리되고 중단됨