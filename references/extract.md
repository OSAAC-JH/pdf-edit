## PDF 페이지 추출 (Extract)

- 트리거 예시: "1페이지랑 3-5페이지만 뽑아서 새 파일 만들어줘", "홀수 페이지만 추출해줘"
- 스크립트: scripts/extract.py
- 실행 예시:
```bash
python scripts/extract.py input.pdf --pages "1,3-5,7" --output extracted.pdf
```
- 옵션 설명:
  - --pages: 추출할 페이지 범위 (예: 1,3-5,7 또는 all) [필수]
  - --output: 생성될 출력 PDF 파일 경로 [필수]