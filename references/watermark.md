## PDF 워터마크 합성 (Watermark)

- 트리거 예시: "문서 배경에 '대외비' 워터마크 넣어줘", "CONFIDENTIAL 문구를 45도로 고르게 반복해서 넣어줘"
- 스크립트: scripts/watermark.py
- 실행 예시:
```bash
python scripts/watermark.py input.pdf --text "CONFIDENTIAL" --opacity 0.15 --output watermarked.pdf
```
- 옵션 설명:
  - --text: 워터마크로 출력할 문자열 [필수]
  - --opacity: 워터마크 투명도 (0.05 - 1.0, 기본값: 0.15)
  - --font-size: 워터마크 폰트 크기 (기본값: 32)
  - --spacing: 타일 간격(pt). 미지정 시 텍스트 길이 기반으로 자동 계산되어 겹치지 않게 배치됨
  - --output: 생성될 출력 PDF 파일 경로 [필수]
- 페이지 전체에 45도 회전된 텍스트가 격자 형태로 고르게 반복 배치됨 (단일 중앙 배치 아님)