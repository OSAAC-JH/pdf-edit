## PDF 마크다운 변환 (To-Markdown)

- 트리거 예시: "PDF 내용을 마크다운으로 변환해줘", "문서 표와 텍스트를 정리해서 md 파일로 뽑아줘"
- 스크립트: scripts/to_markdown.py
- 실행 예시:
```bash
python scripts/to_markdown.py input.pdf --output document.md
```
- 옵션 설명:
  - --output: 생성될 마크다운 파일 경로 [필수]
- 텍스트 레이어가 있는 PDF에서만 동작함 (OCR 미지원). 스캔본이나 이미지로만 구성된 PDF는 추출할 텍스트가 없어 오류로 처리되며, 이 경우 to-image로 변환 후 별도 OCR 도구를 사용해야 함