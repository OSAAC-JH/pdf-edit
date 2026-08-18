## PDF 분할 (Split)

- 트리거 예시: "PDF를 한 장씩 다 나눠줘", "1, 3-5, 7 페이지만 각각 낱장으로 분할해줘"
- 스크립트: scripts/split.py
- 실행 예시:
```bash
# 전체 분할
python scripts/split.py input.pdf --output-dir ./split_output --prefix doc

# 특정 페이지만 낱장 분할
python scripts/split.py input.pdf --pages "1,3-5,7" --output-dir ./split_output --prefix doc
```
- 옵션 설명:
  - --pages: 분할 대상 페이지 범위 (기본값: 00=전체, 예: 1,3-5,7)
  - --output-dir: 분할된 파일들이 저장될 디렉터리 경로 (기본값: ./split_output)
  - --prefix: 생성될 파일의 접두사 (기본값: 원본 파일명)