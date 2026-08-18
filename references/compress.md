## PDF 용량 압축 및 최적화 (Compress)

- 트리거 예시: "PDF 용량 줄여줘", "이 PDF 3MB까지 압축해줘"
- 스크립트: scripts/compress.py
- 실행 예시:
```bash
# 기본 압축 (구조적 압축만)
python scripts/compress.py input.pdf --output compressed.pdf

# 목표 용량 지정
python scripts/compress.py input.pdf --output compressed.pdf --target-mb 3
```
- 옵션 설명:
  - --target-mb: 목표 용량(MB). 지정 시 구조적 압축(pikepdf)만으로 부족하면 내장 이미지를 JPEG로 단계적 재압축/다운스케일하여 목표에 최대한 근접시킴
  - --output: 압축된 PDF 파일 경로 [필수]
- 목표 용량은 최선 노력(best-effort) 기준이며, 텍스트 위주 PDF 등 이미지 재압축 여지가 적은 문서는 목표에 도달하지 못할 수 있음 (결과 메시지에 달성/미달 여부 표시)