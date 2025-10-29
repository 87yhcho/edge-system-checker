# Edge 시스템 종합 점검 도구 - 배포 패키지

이 압축 파일에는 Edge 시스템 종합 점검 도구의 모든 소스 코드가 포함되어 있습니다.

## 📦 포함된 내용

### 필수 파일
- `checker.py` - 메인 실행 파일
- `requirements.txt` - Python 의존성
- `env.example` - 환경 변수 템플릿
- `.gitignore` - Git 제외 파일 설정
- `README.md` - 프로젝트 전체 문서

### 모듈
- `checks/` - 점검 모듈 디렉토리
  - `ups_check.py` - UPS/NUT 점검
  - `camera_check.py` - 카메라 RTSP 점검
  - `nas_check.py` - NAS 점검
  - `system_check.py` - 시스템 종합 점검
  - `pg_check.py` - PostgreSQL 점검 (현재 비활성화)

- `utils/` - 유틸리티 디렉토리
  - `ui.py` - CLI UI (색상, 출력)
  - `reporter.py` - 리포트 생성

### 문서 (선택사항)
- 다양한 업데이트 가이드 및 상세 문서 (*.md)
- GitHub 업로드 가이드

## 🚀 GitHub에 올리는 방법

### 1단계: GitHub 저장소 생성
1. https://github.com 접속 및 로그인
2. 우측 상단 `+` → `New repository`
3. Repository name 입력 (예: `edge-system-checker`)
4. Public 또는 Private 선택
5. **"Initialize this repository with a README" 체크 해제**
6. `Create repository` 클릭

### 2단계: 압축 파일 압축 해제
```bash
# 적절한 위치에 압축 해제
unzip edge-system-checker.zip
cd edge-system-checker
```

### 3단계: Git 초기화 및 커밋
```bash
# Git 초기화
git init

# 사용자 정보 설정 (최초 1회)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Edge 시스템 종합 점검 도구"

# 브랜치 이름 설정
git branch -M main
```

### 4단계: GitHub에 업로드
```bash
# GitHub 저장소 연결 (YOUR_USERNAME을 실제 계정으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/edge-system-checker.git

# 푸시
git push -u origin main
```

**인증 방법:**
- Username: GitHub 계정명
- Password: Personal Access Token
  - Settings → Developer settings → Personal access tokens → Generate new token
  - 권한: `repo` 체크

## 🔐 중요: 보안 확인

### ⚠️ 업로드 전 확인 사항
1. `.env` 파일이 **없는지** 확인 (있으면 안 됨!)
2. `env.example` 파일만 있어야 함
3. 실제 비밀번호나 IP 주소가 코드에 포함되지 않았는지 확인

### .gitignore가 자동으로 제외하는 파일
- `.env` (실제 환경 변수)
- `venv/` (가상 환경)
- `__pycache__/` (Python 캐시)
- `report_*.txt` (리포트 파일)
- `*.log` (로그 파일)

## 📖 사용 방법

### 설치
```bash
# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env.example .env
# .env 파일을 열어서 실제 값으로 수정
```

### 실행
```bash
python checker.py
```

## 📋 환경 변수 설정 (.env)

`.env` 파일 예시:
```env
# NUT/UPS
NUT_UPS_NAME=ups

# NAS
NAS_IP=192.168.10.30
NAS_USER=admin
NAS_PASSWORD=your_password
NAS_PORT=2222

# 카메라
CAMERA_BASE_IP=192.168.1
CAMERA_START_IP=101
CAMERA_USER=root
CAMERA_PASS=root
CAMERA_RTSP_PATH=cam0_0
CAMERA_RTSP_PORT=554
CAMERA_MEDIAMTX_BASE_PORT=1111
```

## 🎯 점검 항목

### 1. UPS/NUT 상태
- NUT 서비스 상태
- 포트 리스닝
- UPS 정보
- NAS 연결

### 2. 카메라 RTSP
- 원본 스트림
- 블러 처리 스트림
- 로그 분석
- 영상 파일 확인

### 3. NAS 상태
- SSH 연결
- 디스크 사용량
- RAID 상태
- 마운트 포인트

### 4. 시스템 종합
- OS 설정
- 서비스 상태
- 포트 리스닝
- Java 설정
- 네트워크 (IP 필수 체크)
- 디스크 공간
- Cron 작업

## 📞 문의 및 지원

- GitHub Issues: 저장소의 Issues 탭 활용
- 상세 문서: README.md 참조
- 업데이트 가이드: 각 *.md 파일 참조

## 📝 라이센스

MIT License

---

**원본 저장소:** https://github.com/87yhcho/edge-system-checker

이 파일은 배포용으로 패키징되었습니다.

