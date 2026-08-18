## PDF 병합 (Merge)

- 트리거 예시: "이 PDF 파일들 순서대로 하나로 합쳐줘", "1번은 1-10, 2번은 3-8 페이지만 합쳐줘"
- 스크립트: scripts/merge.py
- 실행 예시:
```bash
# 전체 파일 병합
python scripts/merge.py doc1.pdf doc2.pdf doc3.pdf --output merged.pdf

# 파일별 부분 페이지만 병합 ("경로:페이지범위" 형식, 생략 시 전체 페이지)
python scripts/merge.py "doc1.pdf:1-10" "doc2.pdf:3-8" "doc3.pdf:4,8,10" --output merged.pdf
```
- 옵션 설명:
  - inputs: 병합할 PDF 경로 목록 (2개 이상, 나열된 순서대로 병합). 각 항목은 `경로` 또는 `경로:페이지범위` 형식
  - --output: 생성될 병합 PDF 파일 경로 [필수]