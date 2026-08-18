## PDF 페이지 회전 (Rotate)

- 트리거 예시: "1,3,5는 시계방향으로, 2,4,6은 반시계방향으로, 7-10은 180도 돌려줘"
- 스크립트: scripts/rotate.py
- 실행 예시:
```bash
# 단순 회전
python scripts/rotate.py input.pdf --rotations "1,3:90" --output rotated.pdf

# 그룹별로 다른 각도/방향 한 번에 적용
python scripts/rotate.py input.pdf --rotations "1,3,5:90" "2,4,6:-90" "7-10:180" --output rotated.pdf
```
- 옵션 설명:
  - --rotations: `페이지범위:각도` 형식의 회전 그룹 목록 [필수, 1개 이상]. 각도는 90의 배수만 허용, 양수=시계방향, 음수=반시계방향 (예: -90 = 반시계 90도)
  - --output: 생성될 출력 PDF 파일 경로 [필수]
  - 같은 페이지가 여러 그룹에 중복 지정되면 오류 처리됨