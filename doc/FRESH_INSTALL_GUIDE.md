# Edge System Checker 신규 서버 설치 가이드

## 📋 개요
새로운 서버에 Edge System Checker를 처음부터 설치하는 완전한 가이드입니다.

**대상 서버 환경:**
- Ubuntu 20.04+ / Debian 11+
- Python 3.8+
- sudo 권한 있는 사용자 계정

---

## 🚀 빠른 설치 (5분)

```bash
# 1. 저장소 클론 또는 파일 전송
git clone <repository-url> edge-system-checker
# 또는
scp edge-system-checker.tar.gz user@server:/home/user/
tar -xzf edge-system-checker.tar.gz

# 2. 디렉토리 이동
cd edge-system-checker

# 3. 패키지 설치
chmod +x INSTALL_PACKAGES.sh
./INSTALL_PACKAGES.sh

# 4. 환경 설정
cp env.example .env
nano .env  # 환경변수 수정

# 5. 테스트 실행
python3 checker.py
```

---

## 📖 상세 설치 가이드

### 1단계: 사전 준비

#### 1.1 시스템 요구사항 확인
```bash
# OS 버전 확인
cat /etc/os-release

# Python 버전 확인 (3.8 이상 필요)
python3 --version

# Git 설치 (선택사항)
sudo apt install -y git
```

#### 1.2 작업 디렉토리 생성
```bash
cd /home/$(whoami)
mkdir -p edge-system-checker
cd edge-system-checker
```

---

### 2단계: 프로그램 파일 가져오기

#### 방법 A: Git으로 클론 (권장)
```bash
# GitHub에서 직접 클론
git clone https://github.com/<username>/edge-system-checker.git
cd edge-system-checker
```

#### 방법 B: 압축 파일 전송
```bash
# 로컬에서 압축 파일 생성
cd /path/to/edge-system-checker
tar -czf edge-system-checker.tar.gz \
  checks/ utils/ \
  checker.py env.example requirements.txt \
  INSTALL_PACKAGES.sh check_packages.py \
  *.md *.sh

# 원격 서버로 전송
scp edge-system-checker.tar.gz user@server:/home/user/

# 서버에서 압축 해제
ssh user@server
cd /home/user
tar -xzf edge-system-checker.tar.gz
cd edge-system-checker
```

#### 방법 C: 개별 파일 전송
```bash
# 로컬에서 실행
scp -r edge-system-checker user@server:/home/user/
```

---

### 3단계: 필수 패키지 설치

#### 3.1 자동 설치 (권장)
```bash
# 설치 스크립트 실행 권한 부여
chmod +x INSTALL_PACKAGES.sh

# 패키지 설치 실행
./INSTALL_PACKAGES.sh

# 설치 확인
python3 check_packages.py
```

**설치되는 패키지:**
- python3-opencv (카메라 체크)
- python3-numpy (OpenCV 의존성)
- python3-paramiko (NAS SSH 연결)
- python3-psycopg2 (PostgreSQL)
- python3-dotenv (환경변수)
- python3-colorama (색상 출력)

#### 3.2 수동 설치
```bash
# 시스템 업데이트
sudo apt update

# Python 기본 패키지
sudo apt install -y python3-pip python3-venv python3-dev

# Edge Checker 필수 패키지
sudo apt install -y \
  python3-opencv \
  python3-numpy \
  python3-paramiko \
  python3-psycopg2 \
  python3-dotenv \
  python3-colorama

# 설치 확인
python3 check_packages.py
```

#### 3.3 설치 확인
```bash
# 모든 패키지 확인
python3 check_packages.py

# 예상 출력:
# ✓ cv2             - OpenCV (카메라 체크)
# ✓ numpy           - NumPy (카메라 체크)
# ✓ paramiko        - Paramiko (NAS SSH 연결)
# ✓ psycopg2        - psycopg2 (PostgreSQL)
# ✓ dotenv          - python-dotenv (환경변수)
# ✓ colorama        - Colorama (색상 출력)
```

---

### 4단계: 환경 설정 (.env)

#### 4.1 환경 파일 생성
```bash
# env.example을 .env로 복사
cp env.example .env

# .env 파일 편집
nano .env
# 또는
vi .env
```

#### 4.2 환경변수 설정

```bash
# ============================================
# .env 파일 내용
# ============================================

# PostgreSQL 설정
PG_HOST=localhost
PG_PORT=5432
PG_DB=blackbox
PG_USER=postgres
PG_PASS=your_password_here

# NUT/UPS 설정
NUT_UPS_NAME=ups

# NAS 설정 (⭐ 중요)
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD="Your_NAS_Password_Here"  # ⚠️ 특수문자 있으면 따옴표 필수!
NAS_PORT=2222  # Synology 커스텀 SSH 포트 (실패 시 22로 재시도)

# 카메라 설정
CAMERA_BASE_IP=192.168.1
CAMERA_START_IP=101
CAMERA_USER=root
CAMERA_PASS=root
CAMERA_RTSP_PATH=cam0_0
CAMERA_RTSP_PORT=554
CAMERA_MEDIAMTX_BASE_PORT=1111
```

#### 4.3 환경변수 중요 포인트

**비밀번호에 특수문자가 있는 경우:**
```bash
# ❌ 잘못된 예 (# 때문에 잘림)
NAS_PASSWORD=Pass#word123

# ✅ 올바른 예 (따옴표로 감싸기)
NAS_PASSWORD="Pass#word123"
```

**NAS 포트 설정:**
```bash
# 기본값: 2222 (Synology 커스텀 포트)
# 실패 시 자동으로 22번 포트로 재시도
NAS_PORT=2222

# 표준 SSH 포트 사용 시:
NAS_PORT=22
```

---

### 5단계: 파일 권한 설정

```bash
# 실행 스크립트 권한 부여
chmod +x checker.py
chmod +x run_edge_checker.sh
chmod +x INSTALL_PACKAGES.sh
chmod +x install_desktop_icon.sh
chmod +x test_nas_only.py
chmod +x check_packages.py

# 전체 디렉토리 권한 확인
ls -la
```

---

### 6단계: 테스트 실행

#### 6.1 개별 모듈 테스트

```bash
# NAS Check만 테스트
python3 test_nas_only.py

# 패키지 확인
python3 check_packages.py
```

#### 6.2 전체 시스템 체크

```bash
# 전체 체크 실행
python3 checker.py

# 또는 스크립트 사용
./run_edge_checker.sh
```

---

### 7단계: 데스크톱 아이콘 설치 (선택사항)

```bash
# 데스크톱 환경이 있는 경우
./install_desktop_icon.sh

# 아이콘이 바탕화면에 생성됨
# 더블클릭으로 실행 가능
```

---

## 📦 설치 스크립트 (올인원)

완전 자동화된 설치를 위한 스크립트:

```bash
#!/bin/bash
# complete_install.sh - 완전 자동 설치 스크립트

set -e  # 오류 시 중단

echo "=========================================="
echo "Edge System Checker 완전 자동 설치"
echo "=========================================="
echo ""

# 1. 파일 존재 확인
if [ ! -f "checker.py" ]; then
    echo "❌ checker.py 파일이 없습니다. 올바른 디렉토리인지 확인하세요."
    exit 1
fi

# 2. 패키지 설치
echo "1. 필수 패키지 설치 중..."
if [ -f "INSTALL_PACKAGES.sh" ]; then
    chmod +x INSTALL_PACKAGES.sh
    ./INSTALL_PACKAGES.sh
else
    echo "⚠️  INSTALL_PACKAGES.sh 없음, 수동 설치 필요"
fi

# 3. 환경 파일 생성
echo ""
echo "2. 환경 파일 생성 중..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✓ .env 파일 생성됨"
    echo "⚠️  .env 파일을 편집하여 환경변수를 설정하세요!"
    echo "   nano .env"
else
    echo "✓ .env 파일이 이미 존재합니다"
fi

# 4. 권한 설정
echo ""
echo "3. 파일 권한 설정 중..."
chmod +x checker.py run_edge_checker.sh test_nas_only.py check_packages.py 2>/dev/null || true
echo "✓ 권한 설정 완료"

# 5. 패키지 확인
echo ""
echo "4. 패키지 설치 확인 중..."
python3 check_packages.py

# 6. 완료
echo ""
echo "=========================================="
echo "✅ 설치 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. .env 파일 편집:"
echo "   nano .env"
echo ""
echo "2. 테스트 실행:"
echo "   python3 checker.py"
echo ""
```

저장하여 사용:
```bash
# 스크립트 저장
nano complete_install.sh
# (위 내용 붙여넣기)

# 실행 권한
chmod +x complete_install.sh

# 실행
./complete_install.sh
```

---

## 🔧 트러블슈팅

### 문제 1: 패키지 설치 실패
```bash
# 에러: "Unable to locate package"
sudo apt update
sudo apt upgrade

# 다시 시도
./INSTALL_PACKAGES.sh
```

### 문제 2: Python 버전 오류
```bash
# Python 버전 확인
python3 --version

# 3.8 미만이면 업그레이드 필요
sudo apt install python3.10
```

### 문제 3: 권한 오류
```bash
# sudo 권한 확인
sudo -v

# 사용자를 sudo 그룹에 추가
sudo usermod -aG sudo $USER
```

### 문제 4: .env 파일 로드 안 됨
```bash
# .env 파일 위치 확인
ls -la .env

# 파일이 없으면
cp env.example .env

# 권한 확인
chmod 600 .env
```

### 문제 5: NAS 연결 실패
```bash
# 포트 확인
# .env 파일에서 NAS_PORT=2222 확인

# 수동 SSH 테스트
ssh -p 2222 user@192.168.10.30

# 포트 22도 테스트
ssh -p 22 user@192.168.10.30

# 방화벽 확인
sudo ufw status
```

---

## 📁 설치 후 디렉토리 구조

```
edge-system-checker/
├── checks/                    # 체크 모듈
│   ├── __init__.py
│   ├── camera_check.py        # 카메라 체크
│   ├── nas_check.py           # NAS 체크 (v2.1)
│   ├── pg_check.py            # PostgreSQL 체크
│   ├── system_check.py        # 시스템 체크
│   └── ups_check.py           # UPS 체크
│
├── utils/                     # 유틸리티
│   ├── __init__.py
│   ├── reporter.py            # 리포트 생성
│   └── ui.py                  # UI 출력
│
├── doc/                       # 문서
│
├── checker.py                 # 메인 프로그램 ⭐
├── .env                       # 환경 설정 (생성 필요) ⭐
├── env.example                # 환경 설정 예시
├── requirements.txt           # Python 패키지 목록
│
├── INSTALL_PACKAGES.sh        # 패키지 설치 스크립트 ⭐
├── check_packages.py          # 패키지 확인 스크립트
├── test_nas_only.py           # NAS 테스트
│
├── run_edge_checker.sh        # 실행 스크립트
├── install_desktop_icon.sh    # 데스크톱 아이콘 설치
├── edge-system-checker.desktop
│
└── *.md                       # 문서 파일들
    ├── README.md
    ├── CHANGELOG.md
    ├── FRESH_INSTALL_GUIDE.md  # 이 파일
    └── ...
```

---

## ✅ 설치 완료 체크리스트

```
□ 1. 파일 다운로드/전송 완료
□ 2. 필수 패키지 설치 완료 (check_packages.py로 확인)
□ 3. .env 파일 생성 및 설정 완료
□ 4. 파일 권한 설정 완료
□ 5. NAS 연결 테스트 성공 (test_nas_only.py)
□ 6. 전체 시스템 체크 성공 (checker.py)
□ 7. (선택) 데스크톱 아이콘 설치
```

---

## 🚀 빠른 명령어 참조

```bash
# 설치
./INSTALL_PACKAGES.sh

# 설정
cp env.example .env && nano .env

# 테스트
python3 check_packages.py    # 패키지 확인
python3 test_nas_only.py     # NAS 테스트
python3 checker.py           # 전체 시스템 체크

# 실행
./run_edge_checker.sh

# 업데이트 (Git 사용 시)
git pull
./INSTALL_PACKAGES.sh  # 새 패키지 있으면
```

---

## 📞 지원

문제 발생 시:
1. `check_packages.py` 실행하여 패키지 확인
2. `.env` 파일 설정 확인
3. 트러블슈팅 섹션 참조
4. 로그 파일 확인: `report_*.txt`

---

*이 가이드는 Ubuntu/Debian 기반 시스템을 기준으로 작성되었습니다.*
*다른 Linux 배포판은 패키지 관리자를 적절히 변경하세요 (yum, dnf 등)*

