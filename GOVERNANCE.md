# KBFG PDF Tools 스킬 거버넌스 문서

## 1. 목적 및 범위

본 문서는 `kbfg-pdf-tools` 스킬(Claude Skill 및 타 플랫폼 호환 버전)을 개발팀과 함께 구축, 유지보수, 배포하기 위한 공통 규칙을 정의한다.

- 대상: `kbfg-pdf-tools` 저장소에 기여하는 모든 개발자, 문서 검토자, 스킬 오너
- 범위: 폴더 구조, 개발 컨벤션, 문서화 규칙, 버전 관리, 테스트 기준, 보안/데이터 취급, 플랫폼 호환성, 배포 절차

## 2. 프로젝트 개요

### 2.1 배경

기존 `pdfedit.py`(CLI, PyPDF2/pdf2image 기반, split·extract·merge·image 4개 기능)를 챗 UI 환경(Claude, ChatGPT 등)에서 대화형으로 사용할 수 있는 스킬 형태로 재구성한다.

### 2.2 목표

- 11개 기능(split, extract, merge, to-image, watermark, password, rotate, page-numbers, bookmarks, compress, to-markdown) 전체를 원 기획 스펙대로 구현 완료 (기능 축소 없음)
- Claude Skill 패키징 규격(`SKILL.md` + `references/` + `scripts/`) 준수
- 순수 pip 설치 라이브러리만 사용하여 ChatGPT Code Interpreter 등 타 플랫폼에서도 동일 스크립트 재사용 가능

## 3. 저장소 구조

```
kbfg-pdf-tools/
├── SKILL.md
├── requirements.txt
├── README.md            (터미널/PowerShell 사용자용 설치·실행 가이드)
├── pdftools.py           (터미널용 통합 실행기 - 서브커맨드 모드 + 대화형 메뉴 모드)
├── pdftools.bat           (Windows 더블클릭 실행용 런처, 순수 ASCII로 작성)
├── references/
│   ├── split.md
│   ├── extract.md
│   ├── merge.md
│   ├── to-image.md
│   ├── watermark.md
│   ├── password.md
│   ├── rotate.md
│   ├── page-numbers.md
│   ├── bookmarks.md
│   ├── compress.md
│   └── to-markdown.md
└── scripts/
    ├── common.py           (페이지 범위 파서 등 공용 함수)
    ├── split.py
    ├── extract.py
    ├── merge.py
    ├── to_image.py
    ├── watermark.py
    ├── password.py
    ├── rotate.py
    ├── page_numbers.py
    ├── bookmarks.py
    ├── compress.py
    └── to_markdown.py
```

- `SKILL.md`: 트리거 조건, 공통 작업 흐름, 기능별 라우팅 표만 포함 (구현 로직 없음)
- `references/*.md`: 사용 설명서 (트리거 예시, 스크립트 경로, 실행 예시, 옵션 설명)
- `scripts/*.py`: 실제 구현. 각 모듈은 `build_parser()` / `run()` / `main()`으로 분리되어 있어, 독립 실행(`python scripts/xxx.py`)과 `pdftools.py`를 통한 통합 실행이 동일한 코드를 공유함
- `pdftools.py`: 사람이 터미널에서 직접 쓰기 위한 진입점. 서브커맨드 모드(`pdftools.py split ...`)와 인자 없이 실행 시 대화형 메뉴 모드를 모두 지원

## 4. 역할과 책임

| 역할 | 담당 범위 |
|---|---|
| 스킬 오너 | `SKILL.md` 라우팅 표 관리, 신규 기능 승인, 배포 승인 |
| 스크립트 개발자 | `scripts/*.py` 구현 및 단위 테스트 작성 |
| 문서 담당 | `references/*.md` 작성 및 최신화 |
| 리뷰어 | PR 리뷰, 테스트 케이스 검증 |

## 5. 개발 컨벤션

### 5.1 코드 스타일

- PEP 8 준수, 함수/모듈 단위 docstring 작성
- 모든 스크립트는 `argparse` 기반 CLI로 작성하여 `input()` 등 대화형 블로킹 호출 금지 (챗 UI에서는 Claude가 값을 이미 확정한 뒤 스크립트를 호출하는 구조이기 때문)

### 5.2 라이브러리 정책

| 기능 | 라이브러리 | 비고 |
|---|---|---|
| 분할/추출/병합/암호/회전 | pypdf | `PdfMerger`는 pypdf 5.0.0부터 제거되어 사용 금지 - 병합은 `PdfWriter.append()`로 구현 |
| 이미지 변환 (긴 이미지 병합 포함) | PyMuPDF (fitz) | v1.22.0부터 PNG/JPG 네이티브 지원 - Pillow 불필요. 긴 이미지 병합 시 `Pixmap.copy()`는 절대좌표 기준으로 동작하므로 반드시 `set_origin()`으로 좌표계를 옮긴 뒤 복사할 것 |
| 워터마크/페이지 번호 | reportlab + pypdf | 오버레이 생성 후 병합. 워터마크는 텍스트 폭 기반 간격 계산으로 페이지 전체에 타일링 |
| 북마크 | PyMuPDF | `doc.set_toc()`로 아웃라인 조작 |
| 압축 | pikepdf + PyMuPDF | 구조적 압축(pikepdf)이 기본, `--target-mb` 지정 시 PyMuPDF로 내장 이미지 JPEG 재인코딩을 단계적으로 시도 (목표 용량은 최선 노력 기준) |
| to-markdown | markitdown[pdf] | 기존 `docs-preprocessor` 스킬과 동일 라이브러리 - 버전 정책 통일 필요. 텍스트 레이어 없는(스캔/이미지) PDF는 빈 문자열이 반환되므로 0바이트로 조용히 성공 처리하지 않고 오류로 raise할 것 (OCR 미지원) |

- 신규 의존성 추가 시 스킬 오너 승인 필요
- 시스템 바이너리(poppler, ghostscript 등) 의존 라이브러리는 플랫폼 호환성 검토 후 채택
- Pillow는 사용하지 않음 (PyMuPDF 네이티브 기능으로 대체)

### 5.3 스크립트 인터페이스 규칙

모든 스크립트는 아래 형태의 표준 인터페이스를 따른다.

```bash
python scripts/extract.py input.pdf --pages "1,3-5,7" --output extract_input.pdf
```

- 입력 파일 경로는 위치 인자, 옵션은 `--`로 시작
- 페이지 범위 표기는 `1,3-5,7` 형식으로 통일 (`common.py`의 파서 공용 사용)
- 실행 결과 파일 경로를 표준 출력에 `OUTPUT_FILE: <경로>` 형식으로 명시적으로 출력

기능별로 아래와 같은 확장 문법을 사용한다 (파서 구현은 각 스크립트 참조).

- **merge**: 파일별 부분 페이지 지정 시 `"경로:페이지범위"` 형식 (예: `"a.pdf:1-10"`), 페이지범위 생략 시 파일 전체 포함
- **rotate**: `--rotations "페이지범위:각도"`를 다중 지정하여 그룹별로 다른 각도 적용 (예: `"1,3,5:90" "2,4,6:-90"`). 양수=시계방향, 음수=반시계방향
- **page-numbers**: `--ranges`를 다중 지정하여 구간별로 번호를 1부터 재시작 (예: `"2-10" "12-24"`). 지정되지 않은 페이지(표지 등)에는 번호 미삽입
- **compress**: `--target-mb` 지정 시 최선 노력(best-effort) 기준으로 목표에 근접시키며, 결과 메시지에 달성/미달 여부를 표시

## 6. 문서화 규칙

### 6.1 SKILL.md 라우팅 표

기능 추가/변경 시 `SKILL.md`의 라우팅 표를 함께 갱신한다 (요청 예시 → 참조 문서 → 스크립트 경로).

### 6.2 reference md 템플릿

```markdown
## 기능명

- 트리거 예시: "..."
- 스크립트: scripts/xxx.py
- 실행 예시:
  python scripts/xxx.py input.pdf --옵션 값 --output 결과파일.pdf
- 옵션 설명:
  - --옵션명: 설명
```

## 7. 버전 관리 및 변경 관리

### 7.1 브랜치 전략

- `main`: 배포 가능 상태만 유지
- `feature/기능명`: 기능 단위 개발 브랜치
- `docs/문서명`: 문서 전용 수정 브랜치

### 7.2 커밋 및 PR 규칙

- 커밋 메시지: `[기능명] 변경 요약` 형식 (예: `[watermark] 대각선 타일 간격 조정`)
- PR에는 관련 `references/*.md` 갱신 여부, 테스트 결과를 함께 명시
- 최소 1인 이상 리뷰 승인 후 병합

### 7.3 CHANGELOG

`CHANGELOG.md`에 버전, 날짜, 변경 내용, 작성자를 기록한다 (본 문서 12절 표 형식 준용).

## 8. 테스트 및 품질 기준

### 8.1 기능별 최소 테스트 케이스

- 정상 케이스: 단일 페이지, 다중 페이지, 전체(00) 처리
- 엣지 케이스: 빈 PDF, 1페이지 PDF, 이미 암호화된 PDF, 대용량(100MB 이상) PDF
- 예외 케이스: 잘못된 페이지 범위, 존재하지 않는 페이지 번호, 여러 그룹에 중복 지정된 페이지
- 모든 스크립트는 병합 전 더미 PDF(reportlab로 즉석 생성)를 이용한 실행 스모크 테스트를 거친다 - 특히 좌표/픽셀 단위 결과가 중요한 기능(스티칭, 회전 방향, 워터마크 타일링)은 실제 실행 결과를 픽셀 색상 또는 텍스트 추출로 검증한다

### 8.2 회귀 테스트

- 스크립트 변경 시 동일 입력에 대한 출력 파일 해시 또는 페이지 수 비교로 회귀 여부 확인
- 라이브러리 버전 업그레이드 시 전체 기능 스모크 테스트 실시

## 9. 보안 및 데이터 취급

### 9.1 테스트 데이터 정책

- 테스트/예시용 PDF는 반드시 더미 데이터만 사용, 실제 고객정보·내부 기밀 문서 사용 금지
- 저장소(git)에 실제 업무 문서를 커밋하지 않는다

### 9.2 실행 환경 확인 필요 사항

- 사내 망분리 정책 및 외부 라이브러리 설치(pip) 허용 범위는 보안팀/인프라팀과 별도 확인 필요 (본 문서 작성 시점 기준 미확정)
- 외부 API로 파일 내용이 전송되지 않는 구조인지(로컬/사내 실행 환경 한정) 배포 전 재확인

## 10. 플랫폼 호환성

### 10.1 Claude 스킬 패키징

- `SKILL.md`는 폴더 루트에 대문자로 위치해야 Claude가 스킬로 인식
- `package_skill.py`로 `.skill` 파일 생성 후 배포

### 10.2 ChatGPT 등 타 플랫폼 활용

- `references/*.md`, `scripts/*.py`는 순수 텍스트/코드 파일이므로 지식 파일 업로드 + Code Interpreter 조합으로 재사용 가능
- 단, `SKILL.md` 프론트매터 기반 자동 트리거 기능은 Claude 전용이므로 타 플랫폼에서는 안내 문서로만 활용

### 10.3 터미널 (PowerShell/CMD) 활용

- `pdftools.py`가 `scripts/*.py`를 서브커맨드로 감싸 사람이 직접 터미널에서 쓸 수 있게 함 (설치/사용법은 `README.md` 참고)
- `pdftools.bat`은 Windows 배치 파일 특유의 인코딩 문제(한글 Windows `cmd.exe`가 UTF-8로 저장된 `.bat`을 CP949로 오인식하여 주석이 깨지고 명령어 오류로 이어지는 현상)를 피하기 위해 순수 ASCII로만 작성됨 - 향후 `.bat` 파일을 추가/수정할 때도 이 원칙을 유지할 것

## 11. 배포 절차

### 11.1 패키징

- 스킬 오너 승인 → `package_skill.py` 실행 → `.skill` 파일 생성

### 11.2 배포 채널

- 사내 배포 방식(공유 드라이브, 사내 포털 등)은 별도 협의 후 확정

## 12. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|---|---|---|---|
| 0.1 | 2026-08-03 | 초안 작성 | - |
| 0.2 | 2026-08-17 | to-markdown 기능 추가(11개 기능), to-image "긴 이미지 저장" 옵션 삭제, Pillow 의존성 제외 | - |
| 0.3 | 2026-08-17 | 코드 리뷰로 발견된 merge.py 크래시(PdfMerger 제거) 수정, split/merge/rotate/watermark/page-numbers/compress 6개 기능 원 스펙대로 전면 확장, --stitch 재도입(좌표 버그 수정), password/bookmarks 이슈 수정 | - |
| 0.4 | 2026-08-18 | 터미널(PowerShell/CMD) 사용을 위한 `pdftools.py` 통합 실행기 및 `pdftools.bat` 런처 추가 (scripts/*.py를 build_parser/run으로 리팩터링해 로직 공유), to-markdown이 텍스트 없는 PDF에서 0바이트 파일을 조용히 생성하던 버그 수정 (이제 명확한 오류로 처리) | - |