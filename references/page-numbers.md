## PDF 페이지 번호 삽입 (Page-Numbers)

- 트리거 예시: "하단에 페이지 번호 매겨줘", "표지 빼고 2페이지부터 번호 매겨줘", "2-10, 12-24, 26-30 페이지에 각각 1부터 번호 매겨줘"
- 스크립트: scripts/page_numbers.py
- 실행 예시:
```bash
# 전체 문서 (표지 포함, 1부터 끝까지)
python scripts/page_numbers.py input.pdf --output numbered.pdf

# 표지 제외 (2페이지부터 번호 매김)
python scripts/page_numbers.py input.pdf --output numbered.pdf --ranges "2-10"

# 구간별 번호 재시작 (각 구간 안에서 1부터 다시 시작)
python scripts/page_numbers.py input.pdf --output numbered.pdf --ranges "2-10" "12-24" "26-30"
```
- 옵션 설명:
  - --ranges: 번호를 매길 구간 목록. 각 구간은 그 안에서 1부터 재시작 (기본값: 문서 전체를 하나의 구간으로 취급)
  - --format: 번호 표기 서식 (사용 가능 변수: {n}=구간 내 번호, {total}=구간 내 총 페이지 수, 기본값: `{n} / {total}`)
  - --output: 생성될 출력 PDF 파일 경로 [필수]
  - --ranges에 포함되지 않은 페이지(예: 표지)에는 번호가 삽입되지 않음