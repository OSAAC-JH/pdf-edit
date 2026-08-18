## PDF 이미지 변환 (To-Image)

- 트리거 예시: "PDF를 PNG 이미지로 바꿔줘", "전체 페이지를 긴 세로 이미지 하나로 이어붙여줘"
- 스크립트: scripts/to_image.py
- 실행 예시:
```bash
python scripts/to_image.py input.pdf --output-dir ./images --pages "1-3" --dpi 300 --format png --transparent --stitch
```
- 옵션 설명:
  - --output-dir: 이미지가 저장될 디렉터리 (기본값: ./image_output)
  - --pages: 변환할 페이지 범위 (기본값: all)
  - --dpi: 이미지 해상도 DPI (기본값: 200)
  - --format: 저장 포맷 (png, jpg, jpeg, 기본값: png)
  - --transparent: PNG 투명 배경 적용 플래그
  - --stitch: 추출된 페이지들을 하나의 긴 세로 이미지로 병합 저장