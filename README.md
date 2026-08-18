# KBFG PDF Tools - 터미널(PowerShell/CMD) 사용 안내

이 폴더의 `pdftools.py`는 `scripts/` 안의 PDF 처리 로직을 사람이 Windows 터미널에서
직접 사용할 수 있도록 감싼 통합 실행기입니다. Claude 같은 LLM이 스킬로 호출할 때 쓰는
`SKILL.md` + `references/*.md` + `scripts/*.py` 구조와 완전히 같은 코드를 공유하므로,
동작 결과는 동일합니다.

## 1. 사전 준비

- Python 3.10 이상 설치 (설치 시 "Add Python to PATH" 체크 필수)
- PowerShell에서 아래 명령으로 설치 확인:

```powershell
python --version
```

`python`이 인식되지 않으면 Python을 재설치하면서 PATH 추가 옵션을 체크하세요.

## 2. 설치

PowerShell에서 이 폴더(`kbfg-pdf-tools`)로 이동한 뒤:

```powershell
cd kbfg-pdf-tools

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\Activate.ps1
```

> **PowerShell 실행 정책 오류가 날 경우** ("이 시스템에서 스크립트를 실행할 수 없으므로...")
> 아래 명령을 먼저 실행한 뒤 다시 활성화하세요 (현재 세션에만 적용되어 안전합니다).
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

가상환경 활성화 후 라이브러리를 설치합니다.

```powershell
pip install -r requirements.txt
```

## 3. 사용 방법

### 방법 A. 대화형 메뉴 (옵션을 몰라도 됨)

작업할 PDF 파일을 이 폴더(또는 원하는 작업 폴더)에 넣고 실행합니다.

```powershell
python pdftools.py
```

번호를 선택하면 필요한 값(페이지 범위, 출력 파일명 등)을 순서대로 물어봅니다.
Windows 탐색기에서 `pdftools.bat`을 더블클릭해도 동일하게 실행됩니다.

### 방법 B. 서브커맨드 모드 (자동화/반복 작업용)

옵션을 직접 지정해 한 줄로 실행할 수 있습니다.

```powershell
# 전체 기능 목록 확인
python pdftools.py --help

# 기능별 상세 옵션 확인
python pdftools.py split --help

# 페이지 1, 3-5만 낱장 분할
python pdftools.py split input.pdf --pages "1,3-5"

# 파일별 부분 페이지만 병합
python pdftools.py merge "a.pdf:1-10" "b.pdf:3-8" --output merged.pdf

# 그룹별로 다른 방향 회전 (양수=시계, 음수=반시계)
python pdftools.py rotate input.pdf --rotations "1,3,5:90" "2,4,6:-90" "7-10:180" --output rotated.pdf

# 워터마크 (페이지 전체에 45도 타일 반복)
python pdftools.py watermark input.pdf --text "CONFIDENTIAL" --output watermarked.pdf

# 표지 제외하고 2페이지부터 번호 매기기
python pdftools.py page-numbers input.pdf --ranges "2-10" --output numbered.pdf

# 목표 용량 지정 압축
python pdftools.py compress input.pdf --target-mb 3 --output compressed.pdf
```

전체 옵션 목록과 예시는 `references/*.md` 문서에도 동일하게 정리되어 있습니다
(단, 그 문서들은 `python scripts/xxx.py ...` 형태로 적혀 있습니다 - LLM이 스킬로
직접 스크립트를 호출할 때 쓰는 방식입니다. 사람이 터미널에서 쓸 때는 위처럼
`python pdftools.py <기능이름> ...` 형태를 쓰면 됩니다).

## 4. 폴더 구조 참고

```
kbfg-pdf-tools/
├── pdftools.py        <- 터미널용 통합 실행기 (이 문서의 주인공)
├── pdftools.bat        <- Windows 더블클릭 실행용 런처
├── SKILL.md             <- Claude 스킬 진입점 (LLM용)
├── requirements.txt
├── references/            <- 기능별 사용 설명서 (LLM용, scripts/ 직접 호출 예시)
└── scripts/                 <- 실제 처리 로직 (pdftools.py와 SKILL.md 양쪽에서 공유)
```

## 5. 문제 해결

- **`python`을 찾을 수 없다는 오류**: Python 설치 시 PATH 추가를 안 했을 가능성이 높습니다. Python을 재설치하거나, 설치 경로를 시스템 환경 변수 PATH에 직접 추가하세요.
- **PowerShell에서 `.ps1` 실행이 차단됨**: 위 2번 항목의 `Set-ExecutionPolicy` 명령을 참고하세요.
- **`ModuleNotFoundError`가 뜸**: 가상환경이 활성화된 상태인지 확인하고(`.\venv\Scripts\Activate.ps1`), `pip install -r requirements.txt`를 다시 실행하세요.
- **사내 망분리 환경에서 pip install이 안 됨**: 거버넌스 문서 9.2절 참고 - 보안팀/인프라팀에 pip 설치 허용 범위를 확인하세요.
- **`pdftools.bat` 실행 시 알아볼 수 없는 문자와 함께 "내부 또는 외부 명령이 아닙니다" 오류가 남**: 이는 `.bat` 파일이 UTF-8로 저장되어 있는데 한글 Windows의 `cmd.exe`가 기본적으로 CP949로 파일을 읽으면서 한글 주석이 깨지고, 그 조각이 명령어로 오인식되는 매우 흔한 현상입니다. 이 저장소의 `pdftools.bat`은 이 문제를 피하기 위해 파일 자체에는 한글을 전혀 쓰지 않고(`chcp 65001`만 앞부분에 추가) 순수 영문으로만 작성되어 있습니다. 만약 직접 다른 `.bat` 스크립트를 작성하게 된다면 같은 원칙(배치 파일 자체는 ASCII만 사용, 한글 메시지는 Python 쪽에서 출력)을 따르는 것을 권장합니다.
- **콘솔에 한글이 네모(□□□)로 깨져 보임**: 파싱 오류는 아니고 글꼴 문제입니다. 레거시 `cmd.exe` 콘솔 대신 최신 Windows Terminal 앱을 사용하면 대부분 해결됩니다.
