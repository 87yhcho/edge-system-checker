# GitHub 업로드 가이드

## 📋 사전 준비

### 1. GitHub 계정 및 저장소 생성
1. https://github.com 접속 및 로그인
2. 우측 상단 `+` 버튼 → `New repository` 클릭
3. Repository 정보 입력:
   - **Repository name**: `edge-system-checker`
   - **Description**: `Edge 시스템 종합 점검 도구 - UPS/NUT, 카메라, NAS, 시스템 자동 점검`
   - **Public** 또는 **Private** 선택
   - **Initialize this repository with a README 체크 해제** ⚠️ (이미 README가 있음)
4. `Create repository` 클릭

## 🚀 Git으로 업로드하기

### 방법 1: 로컬 PC에서 업로드 (권장)

#### 1단계: Git 초기화 및 파일 추가
```bash
# edge-system-checker 폴더로 이동
cd E:\cursor\edge-system-checker

# Git 초기화
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Edge 시스템 종합 점검 도구"
```

#### 2단계: GitHub 저장소 연결
```bash
# GitHub 저장소 URL 연결 (YOUR_USERNAME을 실제 GitHub 계정명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/edge-system-checker.git

# 기본 브랜치 이름 설정
git branch -M main
```

#### 3단계: GitHub에 푸시
```bash
# GitHub에 업로드
git push -u origin main
```

**인증 방법:**
- Username: GitHub 계정명
- Password: GitHub Personal Access Token (비밀번호 아님!)
  - Token 생성: GitHub → Settings → Developer settings → Personal access tokens → Generate new token
  - 권한: `repo` 체크

### 방법 2: 원격 서버에서 직접 업로드

서버에 이미 파일이 있으므로 서버에서 직접 업로드:

```bash
# SSH로 접속
ssh koast-user@10.1.10.128

# 프로젝트 디렉토리로 이동
cd ~/edge-system-checker

# Git 초기화
git init

# 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Edge 시스템 종합 점검 도구"

# GitHub 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/edge-system-checker.git

# 브랜치 설정
git branch -M main

# 푸시
git push -u origin main
```

## 📦 업로드 확인 사항

### 업로드되는 파일 목록
```
edge-system-checker/
├── README.md              ✓ 프로젝트 설명
├── .gitignore            ✓ Git 제외 파일
├── requirements.txt       ✓ Python 의존성
├── env.example           ✓ 환경 변수 템플릿
├── checker.py            ✓ 메인 실행 파일
├── checks/               ✓ 점검 모듈
│   ├── __init__.py
│   ├── ups_check.py
│   ├── camera_check.py
│   ├── nas_check.py
│   └── system_check.py
└── utils/                ✓ 유틸리티
    ├── __init__.py
    ├── ui.py
    └── reporter.py
```

### 업로드되지 않는 파일 (.gitignore)
- `venv/` (가상 환경)
- `.env` (실제 환경 변수 - 비밀번호 포함)
- `__pycache__/` (Python 캐시)
- `report_*.txt` (리포트 파일)
- `*.log` (로그 파일)
- 문서 파일들 (*.md, 선택적)

## 🔐 보안 주의사항

### ⚠️ 절대 업로드하면 안 되는 것
- `.env` 파일 (실제 비밀번호 포함)
- 실제 IP 주소, 계정 정보
- 리포트 파일 (민감한 시스템 정보 포함)

### ✅ 안전하게 공유하는 방법
- `env.example` 파일만 업로드 (예시 값으로 대체)
- README에 설정 방법만 안내
- Private 저장소 사용 권장

## 📝 .env 파일 보호

`.gitignore`에 이미 추가되어 있음:
```
# Environment Variables
.env
.env.local
```

**확인 방법:**
```bash
# Git에 추적되는 파일 확인
git status

# .env가 Untracked files에 있으면 OK
# Changes to be committed에 있으면 안 됨!
```

만약 실수로 추가했다면:
```bash
# Git 추적에서 제거
git rm --cached .env

# 다시 커밋
git commit -m "Remove .env file"
```

## 🔄 업데이트 방법

코드를 수정한 후 GitHub에 업데이트:

```bash
# 변경된 파일 추가
git add .

# 커밋 (의미 있는 메시지 작성)
git commit -m "Fix: 카메라 정렬 문제 해결"

# GitHub에 푸시
git push
```

## 🌿 브랜치 전략 (선택사항)

### 개발 브랜치 사용
```bash
# 개발 브랜치 생성
git checkout -b develop

# 작업 후 커밋
git add .
git commit -m "Add new feature"

# GitHub에 푸시
git push -u origin develop

# GitHub에서 Pull Request 생성
```

## 📋 커밋 메시지 가이드

### 좋은 커밋 메시지 예시
```
Initial commit: Edge 시스템 종합 점검 도구
Add: 카메라 Auto 모드 추가
Fix: 한글 테이블 정렬 문제 해결
Update: README 사용 방법 추가
Refactor: 코드 구조 개선
Docs: 설치 가이드 업데이트
```

### 커밋 메시지 규칙
- **Add**: 새 기능 추가
- **Fix**: 버그 수정
- **Update**: 기존 기능 수정
- **Refactor**: 코드 리팩토링
- **Docs**: 문서 수정
- **Style**: 코드 스타일 변경
- **Test**: 테스트 추가/수정

## 🎯 완료 확인

GitHub 저장소에서 확인할 사항:
1. ✅ README.md가 잘 표시되는지
2. ✅ 파일 구조가 올바른지
3. ✅ .env 파일이 없는지 (env.example만 있어야 함)
4. ✅ requirements.txt가 있는지
5. ✅ 라이센스 표시 확인

## 🌟 추가 설정 (선택사항)

### GitHub Actions (자동화)
- 코드 품질 검사
- 자동 테스트
- 자동 배포

### README 배지 추가
```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

### 이슈 템플릿
- Bug Report 템플릿
- Feature Request 템플릿

## 🆘 문제 해결

### 문제 1: git push 시 인증 실패
**해결:**
```bash
# Personal Access Token 사용
# Username: GitHub 계정명
# Password: Personal Access Token (Settings → Developer settings에서 생성)
```

### 문제 2: 파일이 너무 큼
**해결:**
```bash
# 큰 파일 확인
git ls-files -s | sort -k4 -n -r | head

# 큰 파일 제거
git rm --cached [큰_파일명]
```

### 문제 3: .env 파일을 실수로 커밋함
**해결:**
```bash
# 추적 제거
git rm --cached .env

# 커밋
git commit -m "Remove .env file"

# 푸시
git push

# GitHub에서 히스토리도 제거하려면 (고급)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

## 📞 도움말

- Git 공식 문서: https://git-scm.com/doc
- GitHub 가이드: https://guides.github.com/
- Git 튜토리얼: https://www.atlassian.com/git/tutorials

## ✅ 체크리스트

업로드 전 최종 확인:
- [ ] README.md 작성 완료
- [ ] .gitignore 설정 완료
- [ ] .env 파일 제외 확인
- [ ] env.example 파일 생성
- [ ] requirements.txt 확인
- [ ] 민감한 정보 제거 확인
- [ ] GitHub 저장소 생성
- [ ] Git 초기화 및 커밋
- [ ] GitHub에 푸시 완료
- [ ] 웹에서 저장소 확인

🎉 업로드 완료!

