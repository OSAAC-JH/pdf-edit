## PDF 암호 설정 및 해제 (Password)

- 트리거 예시: "이 PDF에 비밀번호 걸어줘", "PDF 암호 해제해서 저장해줘"
- 스크립트: scripts/password.py
- 실행 예시:
```bash
# 암호 설정
python scripts/password.py input.pdf --output encrypted.pdf --password "mysecret123"

# 암호 해제
python scripts/password.py encrypted.pdf --output decrypted.pdf --decrypt --password "mysecret123"
```
- 옵션 설명:
  - --password: 설정할 암호 또는 기존 복호화용 암호 [필수]
  - --decrypt: 암호 해제 모드 활성화 플래그 (지정하지 않으면 암호화 수행)
  - --output: 생성될 출력 PDF 파일 경로 [필수]
- 입력 파일이 이미 암호화되어 있는 상태에서 재암호화(--decrypt 미지정)를 시도할 경우, --password가 기존 암호와 일치하지 않으면 오류로 처리되고 중단됨